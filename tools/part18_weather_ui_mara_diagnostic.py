#!/usr/bin/env python3
import os, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT)); os.environ["BELLWETHER_AI"]="0"
from backend.core.game import Game
from backend.ai.repair import LABEL, weather

def check(name, cond):
    print(("PASS " if cond else "FAIL ")+name)
    if not cond: raise AssertionError(name)

g=Game(); g.state["location"]="ashcroft_cottage"
g.state["flags"]["read_letter"]=True; g.state["flags"]["mara_intro_available"]=True; g.migrate_state()
acts=g.actions()
check("Mara visible after side-story unlock", g.state["npcs"]["mara"]["visible"] is True)
check("Mara talk action appears when co-located", any(a["id"]=="talk:mara" for a in acts))
check("snow weather state registered", "snow" in LABEL)
check("storm weather state registered", "storm" in LABEL)
g.state["weather"]={"state":"clear","label":"Clear","temperature_c":5,"wind":"light"}
check("snow parser accepted", weather({"state":"snow"},g.state)["state"]=="snow")
check("storm parser accepted", weather({"state":"storm"},g.state)["state"]=="storm")
g.state["weather"]["state"]="snow"
check("snow has environment effect", bool(g.weather_environment_effect()))
g.state["weather"]["state"]="storm"
check("storm has environment effect", bool(g.weather_environment_effect()))
print("Weather/UI/Mara passes: 8/8")
