#!/usr/bin/env python3
"""Focused Part 1 world architecture checks; deterministic and Ollama-free."""
import copy, json, os, py_compile, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
os.environ["BELLWETHER_AI"]="0"

from backend.core.world_model import WORLD_MODEL, WORLD
from backend.core.game import Game
from backend.ai.specific_directors import npc_transition_is_valid

def main():
    checks=[]
    def check(name, fn):
        fn(); checks.append(name); print("PASS", name)

    check("world schema validates", WORLD_MODEL.validate)
    check("legacy WORLD compatibility", lambda: (
        WORLD["bus_stop"]["exits"]["Walk toward the village"] == "village_road"
        or (_ for _ in ()).throw(AssertionError())))
    check("route query", lambda: (
        WORLD_MODEL.shortest_player_route("bus_stop","ashcroft_cottage") is not None
        or (_ for _ in ()).throw(AssertionError())))
    check("opening hours access", lambda: (
        WORLD_MODEL.access_status("bakery", 600)[0] and not WORLD_MODEL.access_status("bakery", 1200)[0]
        or (_ for _ in ()).throw(AssertionError())))
    check("purpose suitability", lambda: (
        WORLD_MODEL.suitability("bakery", purpose="food_retail")["score"] >= 4
        or (_ for _ in ()).throw(AssertionError())))
    check("frozen NPC adjacency preserved", lambda: (
        npc_transition_is_valid("bakery","village_green") and not npc_transition_is_valid("bakery","railway_halt")
        or (_ for _ in ()).throw(AssertionError())))

    g=Game(); before=copy.deepcopy(g.state)
    g.perform("move:village_road")
    assert g.state["location"]=="village_road"
    assert g.state["minute"]==before["minute"]+WORLD["bus_stop"]["travel_minutes"]
    assert g.view()["world_context"]["district"]["id"]=="village_core"
    checks.append("game integration and travel compatibility"); print("PASS game integration and travel compatibility")

    # Migration of an old v0.1.0-shaped state without Part 1 world state.
    old=copy.deepcopy(g.state); old.pop("world_model",None); g.state=old; g.migrate_state()
    assert g.state["world_model"]["schema_version"]==WORLD_MODEL.schema_version
    assert set(g.state["world_model"]["location_modifiers"]) >= set(WORLD)
    checks.append("old-save world migration"); print("PASS old-save world migration")

    # Runtime overlays are detached state and cannot mutate authored catalog data.
    g.state["world_model"]["supernatural_overlays"]["village_green"]={"test":"impossible_frost"}
    assert "supernatural_overlays" not in WORLD["village_green"]
    checks.append("runtime overlay isolation"); print("PASS runtime overlay isolation")

    print(f"Part 1 passes: {len(checks)}/{len(checks)}")
    return 0
if __name__=="__main__": raise SystemExit(main())
