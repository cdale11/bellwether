#!/usr/bin/env python3
"""Offline structural stress runner for Bellwether Part 31.

Uses seeded local candidate selection instead of Ollama so hundreds of gameplay
steps can be tested quickly. This tests state structure, scheduling, movement,
branch reachability and repetition; it is not a prose-quality playtest.
"""
import argparse, json, os, random, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
os.environ["BELLWETHER_AI"]="0"

from backend.ai import specific_directors as directors
from backend.ai.provider import provider
from backend.core.game import Game
from backend.core.structural_validation import validate_state, collect_metrics

PROFILES=("social","homebody","investigator","wanderer","avoidant","repetitive","random")

def install_seeded_director(seed):
    rng=random.Random(seed)
    def choose(director, instruction, context, candidates):
        if not candidates: return None
        # Seeded but non-degenerate: variety tests should exercise many transitions.
        return dict(rng.choice(candidates))
    provider.ask_choice=choose
    provider.ask_text=lambda *a,**k: None
    provider.enabled=False

def choose_action(game, profile, rng):
    actions=game.actions()
    if not actions: return None
    # Dialogue choices are authored state; choose a stable varied branch.
    if game.state.get("dialogue"):
        return rng.choice(actions)["id"]

    by_kind={}
    for a in actions: by_kind.setdefault(a.get("kind"),[]).append(a)
    def pick(kinds):
        pool=[a for k in kinds for a in by_kind.get(k,[])]
        return rng.choice(pool)["id"] if pool else None

    if profile=="social":
        return pick(["talk","free_talk"]) or pick(["travel","life","observe"])
    if profile=="homebody":
        cottage=[a for a in actions if a["id"].startswith("life:") and game.state["location"]=="ashcroft_cottage"]
        return rng.choice(cottage)["id"] if cottage else pick(["travel","life"])
    if profile=="investigator":
        return pick(["investigate"]) or pick(["travel","observe","life"])
    if profile=="wanderer":
        return pick(["travel"]) or pick(["observe","life"])
    if profile=="avoidant":
        return pick(["life","travel","observe"])
    if profile=="repetitive":
        life=by_kind.get("life",[])
        return life[0]["id"] if life else (by_kind.get("observe",[actions[0]])[0]["id"])
    return rng.choice(actions)["id"]

def run_profile(profile, steps, seed):
    install_seeded_director(seed)
    rng=random.Random(seed+10000)
    game=Game()
    issues=[]
    actions_done=0
    visited_locations={game.state["location"]}
    for _ in range(steps):
        if game.state.get("branch_state",{}).get("run_complete"): break
        action=choose_action(game,profile,rng)
        if action is None:
            issues.append("no_actions_available")
            break
        try:
            game.perform(action)
        except Exception as exc:
            issues.append(f"exception:{type(exc).__name__}:{str(exc)[:120]}")
            break
        actions_done+=1
        visited_locations.add(game.state["location"])
        issues.extend(validate_state(game.state))
    # de-duplicate while preserving order
    issues=list(dict.fromkeys(issues))
    metrics=collect_metrics(game.state,actions_done,profile,issues)
    metrics["locations_visited"]=len(visited_locations)
    metrics["visited_locations"]=sorted(visited_locations)
    return metrics

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--steps",type=int,default=120)
    ap.add_argument("--runs",type=int,default=2,help="runs per profile")
    ap.add_argument("--seed",type=int,default=3100)
    ap.add_argument("--json-out")
    args=ap.parse_args()
    results=[]
    for pi,profile in enumerate(PROFILES):
        for run in range(args.runs):
            seed=args.seed+pi*100+run
            result=run_profile(profile,args.steps,seed)
            results.append(result)
            status="PASS" if not result["structural_issues"] else "ISSUES"
            print(f"{status:6} {profile:12} run={run+1} steps={result['steps']:3} "
                  f"day={result['day']} locs={result['locations_visited']} "
                  f"evidence={result['evidence_count']} npc_rep={result['npc_repetition']:.2f} "
                  f"traffic_rep={result['traffic_repetition']:.2f}")
            if result["structural_issues"]:
                print("       ",result["structural_issues"])
    summary={
        "runs":len(results),
        "passes":sum(not r["structural_issues"] for r in results),
        "profiles":list(PROFILES),
        "results":results,
    }
    print(f"\nStructural passes: {summary['passes']}/{summary['runs']}")
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(summary,indent=2))
        print("Wrote",args.json_out)
    if summary["passes"] != summary["runs"]:
        raise SystemExit(1)

if __name__=="__main__":
    main()
