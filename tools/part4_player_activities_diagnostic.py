#!/usr/bin/env python3
from copy import deepcopy
import os, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT)); os.environ["BELLWETHER_AI"]="0"
from backend.core.game import Game, INITIAL_STATE
from backend.core.activity_model import ACTIVITY_MODEL

def check(name, ok):
    print(("PASS " if ok else "FAIL ")+name); return bool(ok)

g=Game(); g.state=deepcopy(INITIAL_STATE); g.state["location"]="ashcroft_cottage"
results=[]
results.append(check("activity schema present", "player_activities" in g.state))
acts={a[0] for a in ACTIVITY_MODEL.available_garden_actions(g.state)}
results.append(check("unprepared garden offers preparation", "garden:prepare" in acts))
g.perform("garden:prepare")
results.append(check("preparation persists", g.state["player_activities"]["garden"]["soil_prepared"]))
g.state["player_activities"]["garden"]["seed_stock"]["radish"]=1
acts={a[0] for a in ACTIVITY_MODEL.available_garden_actions(g.state)}
results.append(check("prepared garden offers crop choice", any(x.startswith("garden:sow:") for x in acts)))
g.perform("garden:sow:radish")
p=g.state["player_activities"]["garden"]["plots"][0]
results.append(check("sowing creates persistent crop", p and p["crop_id"]=="radish"))
before=p["growth"]; g.advance(120); results.append(check("crop growth advances with time", p["growth"]>before))
g.state["player_activities"]["garden"]["moisture"]=5; before=p["growth"]; g.advance(120); dry_gain=p["growth"]-before
g.perform("garden:water"); before=p["growth"]; g.advance(120); wet_gain=p["growth"]-before
results.append(check("watering affects growth rate", wet_gain>dry_gain))
g.state["player_activities"]["garden"]["weeds"]=80; g.perform("garden:tend")
results.append(check("tending reduces weeds", g.state["player_activities"]["garden"]["weeds"]<80))
p["growth"]=p["growth_required"]; g.perform("garden:harvest")
results.append(check("harvest moves produce to store", g.state["player_activities"]["garden"]["harvest_store"].get("radish",0)>0))
old=deepcopy(INITIAL_STATE); old.pop("player_activities",None); g.state=old; g.migrate_state()
results.append(check("old-save activity migration", "player_activities" in g.state))
results.append(check("legacy garden progress retained", "garden_progress" in g.state["location_state"]["ashcroft_cottage"]))
print(f"Part 4 passes: {sum(results)}/{len(results)}")
raise SystemExit(0 if all(results) else 1)
