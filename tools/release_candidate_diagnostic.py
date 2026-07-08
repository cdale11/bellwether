#!/usr/bin/env python3
"""Bellwether v0.1.0 RC conclusive diagnostic.

Runs deterministic structural, persistence, migration, conversation-parser,
failure-recovery, scheduling, pacing, and optional real-Qwen continuity checks.
Print the complete output when reporting a problem.
"""
import argparse, copy, json, os, py_compile, random, subprocess, sys, tempfile, time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

def banner(name):
    print("\n"+"="*78)
    print(name)
    print("="*78, flush=True)

def run_cmd(cmd, timeout):
    started=time.time()
    p=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,timeout=timeout)
    return {"returncode":p.returncode,"seconds":round(time.time()-started,2),
            "stdout":p.stdout,"stderr":p.stderr}

def compact_lines(text, prefixes):
    return [x for x in text.splitlines() if x.startswith(prefixes)]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--skip-qwen",action="store_true",help="Skip actual local-model continuity test")
    ap.add_argument("--json-out",default="rc_diagnostic_report.json")
    ap.add_argument("--stress-steps",type=int,default=180)
    ap.add_argument("--blind-steps",type=int,default=500)
    args=ap.parse_args()
    report={"version":(ROOT/"VERSION").read_text().strip(),"started":time.strftime("%Y-%m-%d %H:%M:%S"),
            "checks":{},"failures":[]}

    banner("1/8 COMPILE AND PACKAGE INTEGRITY")
    try:
        files=list((ROOT/"backend").rglob("*.py"))+list((ROOT/"tools").glob("*.py"))
        for f in files: py_compile.compile(str(f),doraise=True)
        mode=(ROOT/"run.sh").stat().st_mode & 0o777
        assert mode & 0o111, f"run.sh mode is {oct(mode)}"
        report["checks"]["compile"]={"ok":True,"python_files":len(files),"run_sh_mode":oct(mode)}
        print("PASS compile",len(files),"Python files; run.sh",oct(mode))
    except Exception as exc:
        report["failures"].append("compile/package: "+repr(exc)); print("FAIL",repr(exc))

    banner("2/8 STRUCTURAL SIMULATION MATRIX")
    try:
        r=run_cmd([sys.executable,str(ROOT/"tools/stress_test.py"),"--steps",str(args.stress_steps),
                   "--runs","2","--seed","3500"],360)
        lines=compact_lines(r["stdout"],("PASS","FAIL","ISSUES","Structural"))
        print("\n".join(lines))
        ok=r["returncode"]==0 and any("Structural passes:" in x for x in lines)
        report["checks"]["structural"]={"ok":ok,"seconds":r["seconds"],"summary":lines}
        if not ok: report["failures"].append("structural matrix failed")
    except Exception as exc:
        report["failures"].append("structural exception: "+repr(exc)); print("FAIL",repr(exc))

    banner("3/8 PLAYER-PERSPECTIVE PROFILES AND PACING VARIANCE")
    try:
        r=run_cmd([sys.executable,str(ROOT/"tools/blind_playtest.py"),"--steps",str(args.blind_steps),
                   "--runs","2","--seed","3500"],600)
        prefixes=("story_follower","social_explorer","life_sim","investigator","cautious_wanderer","balanced_reader")
        lines=compact_lines(r["stdout"],prefixes)
        print("\n".join(lines))
        report["checks"]["blind_profiles"]={"ok":r["returncode"]==0,"seconds":r["seconds"],"summary":lines}
        if r["returncode"]!=0: report["failures"].append("blind playtest tool failed")
    except Exception as exc:
        report["failures"].append("blind playtest exception: "+repr(exc)); print("FAIL",repr(exc))

    banner("4/8 SAVE/LOAD, OLD-SAVE MIGRATION, AND STATE ROUND-TRIP")
    try:
        os.environ["BELLWETHER_AI"]="0"
        from backend.core import game as gm
        from backend.ai.provider import provider
        original_save=gm.SAVE_PATH
        td=Path(tempfile.mkdtemp(prefix="bellwether_rc_save_"))
        gm.SAVE_PATH=td/"save.json"
        g=gm.Game()
        g.state["location"]="village_road"
        g.state["npcs"]["mrs_ellis"].update(location="village_road",visible=True)
        g.state["conversation_sessions"]["mrs_ellis"]=[
            {"time":"09:10","player":"Morning.","npc":"Morning, dear."}]
        g.state["social_memory"]["mrs_ellis"]=["The newcomer greeted Mrs Ellis politely."]
        g.state["relationships"]["mrs_ellis"].update(affinity=2,familiarity=3,trust=1,talks=1)
        g.state["investigation"]["evidence"].append({"id":"diag","title":"Diagnostic note","text":"Persistence marker"})
        before=copy.deepcopy(g.state)
        assert g.save()["ok"]
        assert not Path(str(gm.SAVE_PATH)+".tmp").exists()
        g.state["money"]=-999
        loaded=g.load()
        assert loaded["ok"] and g.state["money"]==before["money"]
        assert g.state["conversation_sessions"]["mrs_ellis"]==before["conversation_sessions"]["mrs_ellis"]
        assert g.state["relationships"]["mrs_ellis"]==before["relationships"]["mrs_ellis"]
        assert g.state["investigation"]["evidence"][-1]["id"]=="diag"
        # Simulate Part 33 save lacking Part 34 short-term buffers.
        old=copy.deepcopy(g.state); old.pop("conversation_sessions",None)
        gm.SAVE_PATH.write_text(json.dumps(old))
        assert g.load()["ok"]
        assert set(g.state["conversation_sessions"]) >= set(g.state["npcs"])
        gm.SAVE_PATH=original_save
        report["checks"]["save_load"]={"ok":True,"bytes":len(json.dumps(before))}
        print("PASS atomic round-trip, conversation persistence, relationship persistence, evidence persistence, old-save migration")
    except Exception as exc:
        report["failures"].append("save/load: "+repr(exc)); print("FAIL",repr(exc))
        try: gm.SAVE_PATH=original_save
        except Exception: pass

    banner("5/8 CONVERSATION CONTINUITY, SOCIAL PARSER, AND FALLBACK ISOLATION")
    try:
        from backend.core.game import Game
        from backend.ai.provider import provider
        g=Game(); g.state["location"]="village_road"
        g.state["npcs"]["mrs_ellis"].update(location="village_road",visible=True,activity="walking toward the shops")
        raw=[
          'Mrs Ellis: "Of course I remember you. We spoke only minutes ago, dear."\nSOCIAL: {"affinity":0,"trust":0,"familiarity":1,"tone":["friendly"],"memory":"The player checked whether Mrs Ellis remembered their recent greeting."}',
          'Mrs Ellis: Get yourself settled first; the cottage has waited long enough.\nSOCIAL: {"affinity":0,"trust":0,"familiarity":1,"tone":["helpful"],"memory":"The player asked Mrs Ellis for practical advice."}',
          "Mrs Ellis: Then that's settled. Mind the puddles.\nSOCIAL: {broken json}",
        ]
        prompts=[]; orig=provider._plain_request; enabled=provider.enabled; provider.enabled=True
        provider._plain_request=lambda *a,**k: prompts.append(a[1]) or raw.pop(0)
        try:
            g.start_ai_player_conversation("mrs_ellis","Do you not remember me?")
            g.start_ai_player_conversation("mrs_ellis","Any ideas what I should do next?")
            before=copy.deepcopy(g.state["relationships"]["mrs_ellis"])
            g.start_ai_player_conversation("mrs_ellis","Perfect!")
        finally:
            provider._plain_request=orig; provider.enabled=enabled
        after=g.state["relationships"]["mrs_ellis"]
        assert len(g.state["conversation_sessions"]["mrs_ellis"])==3
        assert "We spoke only minutes ago" in prompts[1]
        assert "Any ideas what I should do next?" in prompts[2]
        assert g.state["history"][-1]["text"]=="Then that's settled. Mind the puddles."
        assert after["affinity"]==before["affinity"] and after["trust"]==before["trust"]
        assert after["familiarity"]==before["familiarity"]+1
        assert all("perfect" not in m.lower() for m in g.state["social_memory"]["mrs_ellis"])
        report["checks"]["conversation_parser"]={"ok":True,"session_turns":3,
          "long_term_memories":g.state["social_memory"]["mrs_ellis"],
          "relationship":g.state["relationships"]["mrs_ellis"]}
        print("PASS exact continuity, quote cleanup, malformed metadata isolation, neutral fallback, selective memory")
    except Exception as exc:
        report["failures"].append("conversation/parser: "+repr(exc)); print("FAIL",repr(exc))

    banner("6/8 DIRECTOR SCHEDULER, TEMPERATURE, AND TRANSITION INVARIANTS")
    try:
        g=Game()
        start_temp=g.state["weather"]["temperature_c"]; start_min=g.state["minute"]
        g.advance(180)
        end_temp=g.state["weather"]["temperature_c"]
        scheduler=g.state["simulation_scheduler"]
        assert not scheduler.get("round_in_progress")
        assert not scheduler.get("advance_active")
        # Temperature must be season-bounded and time must advance exactly.
        lo,hi=g.state["season"]["temperature_range_c"]
        assert lo-2 <= end_temp <= hi+2
        assert (g.state["minute"]-start_min)%1440==180
        # Transition validators reject impossible identifiers/teleports.
        from backend.ai.specific_directors import npc_transition_is_valid, traffic_transition_is_valid
        bad_npc=npc_transition_is_valid(g.state["npcs"]["jonah"]["location"],"not_a_place")
        vehicle=g.state["traffic"]["bus_7"]
        bad_traffic=traffic_transition_is_valid("bus_7",vehicle,"diagnostic_invalid","not_a_place",g.state)
        assert not bad_npc and not bad_traffic
        report["checks"]["scheduler_weather"]={"ok":True,"start_temp":start_temp,"end_temp":end_temp,
          "season":g.state["season"]["label"],"scheduler":scheduler}
        print(f"PASS time {start_min}->{g.state['minute']}; temperature {start_temp}C->{end_temp}C; scheduler unlocked; invalid transitions rejected")
    except Exception as exc:
        report["failures"].append("scheduler/weather: "+repr(exc)); print("FAIL",repr(exc))

    banner("7/8 REAL QWEN HEALTH AND CONTINUITY")
    if args.skip_qwen:
        report["checks"]["real_qwen"]={"ok":None,"skipped":True}
        print("SKIP requested by --skip-qwen")
    else:
        try:
            # Use the dedicated real-model QA path. It prints per-turn latency and deltas.
            env=dict(os.environ); env["BELLWETHER_AI"]="1"
            q0=time.time()
            r=subprocess.run([sys.executable,str(ROOT/"tools/real_qwen_narrative_qa.py"),
                              "--npc","mrs_ellis","--scenario","continuity"],
                             cwd=ROOT,text=True,capture_output=True,timeout=420,env=env)
            qseconds=round(time.time()-q0,2)
            print(r.stdout)
            if r.stderr.strip(): print("STDERR:",r.stderr)
            ok=r.returncode==0
            report["checks"]["real_qwen"]={"ok":ok,"seconds":qseconds,
                "output":r.stdout[-12000:],"stderr":r.stderr[-3000:]}
            if not ok: report["failures"].append("real Qwen continuity runner failed")
        except Exception as exc:
            report["failures"].append("real Qwen: "+repr(exc)); print("FAIL",repr(exc))

    banner("8/8 FINAL DIAGNOSTIC VERDICT")
    report["finished"]=time.strftime("%Y-%m-%d %H:%M:%S")
    report["ok"]=not report["failures"]
    out=Path(args.json_out)
    if not out.is_absolute(): out=ROOT/out
    out.write_text(json.dumps(report,indent=2))
    if report["ok"]:
        print("PASS: all executed certification checks completed without detected engineering failures.")
    else:
        print("ATTENTION:",len(report["failures"]),"failure(s)")
        for x in report["failures"]: print(" -",x)
    print("REPORT:",out)
    print("\nWhen asking for diagnosis, paste the COMPLETE terminal output and attach",out.name)
    return 0 if report["ok"] else 1

if __name__=="__main__":
    raise SystemExit(main())
