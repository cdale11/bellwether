"""Structural validation helpers for Bellwether Part 31."""
from collections import Counter

TRAIN_LOCATIONS={"away","railway_halt"}
ROAD_VEHICLE_LOCATIONS={"away","village_road","village_green","village_shop"}

def validate_state(state):
    issues=[]
    traffic=state.get("traffic",{})
    train=traffic.get("train",{})
    if train.get("location") not in TRAIN_LOCATIONS:
        issues.append(f"train_invalid_location:{train.get('location')}")
    for vid in ("bus_7","delivery_van"):
        loc=traffic.get(vid,{}).get("location")
        if loc not in ROAD_VEHICLE_LOCATIONS:
            issues.append(f"{vid}_invalid_location:{loc}")
    for nid,npc in state.get("npcs",{}).items():
        if npc.get("location") in (None,"away"):
            issues.append(f"npc_invalid_location:{nid}:{npc.get('location')}")
    scheduler=state.get("simulation_scheduler",{})
    if scheduler.get("round_in_progress"):
        issues.append("director_round_left_in_progress")
    return issues

def repetition_score(history, window=6):
    ids=[x.get("choice") for x in history if x.get("choice")]
    if len(ids)<2:
        return 0.0
    ids=ids[-window:]
    return 1.0 - len(set(ids))/len(ids)

def collect_metrics(state, steps, profile, issue_log=None):
    npc_hist=state.get("npc_action_history",{})
    traffic_hist=state.get("traffic_action_history",{})
    action_hist=state.get("player_life",{}).get("activity_history",[])
    visited=sum(1 for v in state.get("player_life",{}).get("location_familiarity",{}).values() if v>0)
    kinds=Counter(x.get("activity","unknown") for x in action_hist)
    return {
        "profile":profile,
        "steps":steps,
        "day":state.get("day"),
        "minute":state.get("minute"),
        "world_rounds":state.get("ai_runtime",{}).get("world_rounds",0),
        "failed_rounds":state.get("ai_runtime",{}).get("failed_rounds",0),
        "accepted_proposals":state.get("director_status",{}).get("accepted_proposals",0),
        "locations_visited":visited,
        "life_activity_types":len(kinds),
        "evidence_count":len(state.get("investigation",{}).get("evidence",[])),
        "encounter_count":len(state.get("encounters",[])),
        "endgame_unlocked":bool(state.get("branch_state",{}).get("endgame_unlocked")),
        "run_complete":bool(state.get("branch_state",{}).get("run_complete")),
        "npc_repetition":round(sum(repetition_score(h) for h in npc_hist.values())/max(1,len(npc_hist)),3),
        "traffic_repetition":round(sum(repetition_score(h) for h in traffic_hist.values())/max(1,len(traffic_hist)),3),
        "structural_issues":list(issue_log or validate_state(state)),
        "branch":dict(state.get("branch_state",{})),
    }
