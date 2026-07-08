#!/usr/bin/env python3
"""Cumulative post-v0.1.0 diagnostic runner.

Run on the target machine after each Part. Produces a JSON report that can be
shared with the next development chat/build for regression analysis.
"""
import argparse, json, os, py_compile, subprocess, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def run(cmd, timeout=900):
    started=time.time(); p=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,timeout=timeout)
    return {"command":cmd,"returncode":p.returncode,"seconds":round(time.time()-started,2),"stdout":p.stdout[-20000:],"stderr":p.stderr[-10000:]}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output",default="post_v010_diagnostic_report.json"); ap.add_argument("--include-release",action="store_true"); args=ap.parse_args()
    report={"version":(ROOT/"VERSION").read_text().strip(),"generated_unix":int(time.time()),"stages":[]}
    compile_errors=[]; count=0
    for source_dir in ("backend","tools"):
      for p in (ROOT/source_dir).rglob("*.py"):
        if "__pycache__" in p.parts: continue
        count+=1
        try: py_compile.compile(str(p),doraise=True)
        except Exception as e: compile_errors.append(f"{p.relative_to(ROOT)}: {e}")
    report["stages"].append({"name":"compile_all_python","passed":not compile_errors,"count":count,"errors":compile_errors})
    scripts=["tools/part1_world_architecture_diagnostic.py","tools/part2_npc_lives_diagnostic.py","tools/part3_social_web_diagnostic.py","tools/part4_player_activities_diagnostic.py","tools/part5_economy_diagnostic.py","tools/part6_jobs_diagnostic.py","tools/part7_dynamic_events_diagnostic.py","tools/part8_seasonal_life_diagnostic.py","tools/part9_npc_autonomy_diagnostic.py","tools/part10_knowledge_gossip_diagnostic.py","tools/part11_investigation_diagnostic.py","tools/part12_systemic_horror_diagnostic.py","tools/part13_player_identity_diagnostic.py","tools/part14_danger_death_diagnostic.py","tools/part15_recurrence_diagnostic.py","tools/part16_content_integration_diagnostic.py","tools/part17_release_certification_diagnostic.py","tools/part18_weather_ui_mara_diagnostic.py","tools/part19_v030_ui_architecture_diagnostic.py","tools/part20_visual_identity_diagnostic.py"]
    for script in scripts:
        result=run([sys.executable,script]); result.update({"name":Path(script).stem,"passed":result["returncode"]==0}); report["stages"].append(result)
    if args.include_release:
        result=run([sys.executable,"tools/release_candidate_diagnostic.py"],timeout=7200); result.update({"name":"legacy_release_candidate_diagnostic","passed":result["returncode"]==0}); report["stages"].append(result)
    report["passed"]=all(x.get("passed",False) for x in report["stages"])
    out=ROOT/args.output; out.write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps({"passed":report["passed"],"report":str(out),"stages":[{"name":x["name"],"passed":x["passed"]} for x in report["stages"]]},indent=2))
    return 0 if report["passed"] else 1
if __name__=="__main__": raise SystemExit(main())
