#!/usr/bin/env python3
from copy import deepcopy
import os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT)); os.environ["BELLWETHER_AI"]="0"
from backend.core.game import Game, INITIAL_STATE
from backend.core.world_runtime_model import WORLD_RUNTIME_MODEL

def check(name, ok):
    print(("PASS" if ok else "FAIL")+": "+name); return bool(ok)

g=Game(); g.state=deepcopy(INITIAL_STATE); g.migrate_state(); s=g.state
results=[]
results.append(check("world runtime exists", "world_runtime" in s and s["world_runtime"]["schema_version"]==1))
s["weather"]["state"]="heavy_rain"
for _ in range(18): WORLD_RUNTIME_MODEL.advance(s,80)
results.append(check("wet weather persists as tendency", s["world_runtime"]["tendencies"]["wet_period"]>.5))
results.append(check("river responds to accumulated weather", s["world_runtime"]["location_conditions"]["riverside_path"]["river"] in {"rising","high"}))
s["location"]="riverside_path"; note=WORLD_RUNTIME_MODEL.observation(s,"riverside_path")
results.append(check("player-visible ecological observation", bool(note) and "river" in note.lower()))
WORLD_RUNTIME_MODEL.record_day(s,1)
results.append(check("weather history persists", len(s["world_runtime"]["weather_history"])==1))
old=deepcopy(s["world_runtime"]); g.migrate_state()
results.append(check("migration preserves runtime", g.state["world_runtime"]["weather_history"]==old["weather_history"]))
results.append(check("economy signal exposed", "delivery_disruption" in s["world_runtime"]["economy_signals"]))
raise SystemExit(0 if all(results) else 1)
