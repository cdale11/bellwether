#!/usr/bin/env python3
"""Player-perspective sequential playtest harness for Bellwether Part 32.

Agents may inspect only Game.view(): visible prose, visible quests, location,
present actors, and currently offered actions. They do not inspect hidden flags,
branch thresholds, Director internals, or code state when choosing actions.
"""
import argparse, json, os, random, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
os.environ["BELLWETHER_AI"]="0"

from backend.core.game import Game
from backend.ai.provider import provider
from backend.ai import specific_directors as directors

PROFILES=("story_follower","social_explorer","life_sim","investigator","cautious_wanderer","balanced_reader")

def install_seeded_world(seed):
    rng=random.Random(seed)
    def choose(director,instruction,context,candidates):
        return dict(rng.choice(candidates)) if candidates else None
    provider.ask_choice=choose
    provider.ask_text=lambda *a,**k: None
    provider.enabled=False

def visible_snapshot(view):
    s=view["state"]
    return {
        "day":s["day"],"time":s["time"],"location":view["location"]["name"],
        "quests":s["quests"],
        "present_npcs":[n["name"] for n in view["present"]["npcs"]],
        "actions":[{"id":a["id"],"label":a["label"],"kind":a["kind"]} for a in view["actions"]],
        "new_messages":s.get("new_messages",[]),
    }

def choose_from_visible(view, profile, rng, recent_actions):
    actions=view["actions"]
    if not actions: return None
    by_kind={}
    for a in actions: by_kind.setdefault(a["kind"],[]).append(a)
    def pick(kinds, avoid_recent=True):
        pool=[a for k in kinds for a in by_kind.get(k,[])]
        if avoid_recent:
            fresh=[a for a in pool if a["id"] not in recent_actions[-3:]]
            if fresh: pool=fresh
        return rng.choice(pool) if pool else None

    # Dialogue and ending choices are explicit player-facing decisions.
    if by_kind.get("choice"):
        return rng.choice(by_kind["choice"])
    endings=[a for a in actions if a["id"].startswith("ending:")]
    if endings:
        return rng.choice(endings)

    # Explicit story affordances remain authored and take priority for story-oriented runs.
    if profile in ("story_follower","social_explorer") and by_kind.get("story"):
        return rng.choice(by_kind["story"])
    if profile=="story_follower" and by_kind.get("talk"):
        return rng.choice(by_kind["talk"])

    weights={
      "story_follower":["story","talk","travel","life","investigate","observe"],
      "social_explorer":["talk","free_talk","travel","life","observe","investigate"],
      "life_sim":["life","travel","talk","observe","investigate"],
      "investigator":["investigate","travel","observe","talk","life"],
      "cautious_wanderer":["travel","observe","life","investigate","talk"],
      "balanced_reader":["story","talk","free_talk","life","investigate","travel","observe"],
    }[profile]

    if profile=="balanced_reader":
        # Cycle through visible systems as a curious player might, based only on
        # this agent's own recent choices—not hidden game thresholds.
        cycle=("story","free_talk","life","investigate","travel","life","observe","travel")
        desired=cycle[len(recent_actions)%len(cycle)]
        pool=by_kind.get(desired,[])
        if desired=="free_talk": pool=[]
        if pool:
            fresh=[a for a in pool if a["id"] not in recent_actions[-4:]]
            return rng.choice(fresh or pool)

    # Sleeping is a visible life choice but should not dominate ordinary life-sim play.
    for kind in weights:
        pool=by_kind.get(kind,[])
        if kind=="life":
            non_sleep=[a for a in pool if a["id"]!="sleep"]
            if non_sleep: pool=non_sleep
        if pool:
            fresh=[a for a in pool if a["id"] not in recent_actions[-3:]]
            return rng.choice(fresh or pool)

    return rng.choice(actions)

def run(profile, steps, seed, transcript_dir=None):
    install_seeded_world(seed)
    rng=random.Random(seed+90000)
    game=Game()
    recent=[]
    transcript=[]
    visited=set()
    action_kinds={}
    message_cursor=0
    first_anomaly_step=None
    first_horror_stage_step=None
    completed_step=None

    for step in range(1,steps+1):
        view=game.view()
        snap=visible_snapshot(view)
        visited.add(snap["location"])
        # Record only newly visible prose in sequence.
        messages=game.state["history"][message_cursor:]
        message_cursor=len(game.state["history"])
        for m in messages:
            transcript.append({"step":step,"type":"message","speaker":m["speaker"],"text":m["text"]})
        action=choose_from_visible(view,profile,rng,recent)
        if action is None:
            transcript.append({"step":step,"type":"error","text":"No visible actions available"})
            break
        transcript.append({"step":step,"type":"action","label":action["label"],"kind":action["kind"],"location":snap["location"]})
        recent.append(action["id"])
        action_kinds[action["kind"]]=action_kinds.get(action["kind"],0)+1
        if action["id"].startswith("free_talk:"):
            npc_id=action["id"].split(":",1)[1]
            utterances=("Morning. How are you?","How has your day been?","Good to see you. Take care.")
            game.free_talk(npc_id,utterances[(step-1)%len(utterances)])
        else:
            game.perform(action["id"])

        # Metrics are collected after play; they are never used by choose_from_visible.
        ps=game.state.get("psychological_state",{})
        if first_anomaly_step is None and ps.get("recent_anomalies"):
            first_anomaly_step=step
        if first_horror_stage_step is None and ps.get("stage","ordinary")!="ordinary":
            first_horror_stage_step=step
        if game.state.get("branch_state",{}).get("run_complete"):
            completed_step=step
            break

    # Append final unread prose.
    for m in game.state["history"][message_cursor:]:
        transcript.append({"step":len(recent)+1,"type":"message","speaker":m["speaker"],"text":m["text"]})

    result={
        "profile":profile,"seed":seed,"steps":len(recent),
        "days_elapsed":game.state["day"],
        "visited_locations":sorted(visited),
        "location_count":len(visited),
        "action_kinds":action_kinds,
        "completed_main":[q["title"] for q in game.state["quests"]["main"] if q.get("done")],
        "active_visible_main":[q["title"] for q in game.visible_quests("main") if not q.get("done")],
        "evidence_count":len(game.state["investigation"]["evidence"]),
        "talk_count":sum(r.get("talks",0) for r in game.state["relationships"].values()),
        "life_activity_count":len(game.state["player_life"]["activity_history"]),
        "first_anomaly_step":first_anomaly_step,
        "first_horror_stage_step":first_horror_stage_step,
        "endgame_unlocked":game.state["branch_state"]["endgame_unlocked"],
        "run_complete":game.state["branch_state"]["run_complete"],
        "completion_step":completed_step,
        "ending":game.state["branch_state"].get("ending"),
        "transcript_entries":len(transcript),
    }
    if transcript_dir:
        out=Path(transcript_dir); out.mkdir(parents=True,exist_ok=True)
        (out/f"{profile}_{seed}.json").write_text(json.dumps({"result":result,"transcript":transcript},indent=2))
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--steps",type=int,default=220)
    ap.add_argument("--runs",type=int,default=2)
    ap.add_argument("--seed",type=int,default=3200)
    ap.add_argument("--transcript-dir")
    ap.add_argument("--json-out")
    args=ap.parse_args()
    results=[]
    for pi,profile in enumerate(PROFILES):
        for ri in range(args.runs):
            r=run(profile,args.steps,args.seed+pi*100+ri,args.transcript_dir)
            results.append(r)
            print(f"{profile:18} run={ri+1} steps={r['steps']:3} day={r['days_elapsed']} "
                  f"locs={r['location_count']} life={r['life_activity_count']} evidence={r['evidence_count']} "
                  f"anomaly={r['first_anomaly_step']} complete={r['completion_step']}")
    summary={"runs":len(results),"profiles":list(PROFILES),"results":results}
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(summary,indent=2))
        print("Wrote",args.json_out)

if __name__=="__main__":
    main()
