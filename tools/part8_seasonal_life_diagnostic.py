#!/usr/bin/env python3
from copy import deepcopy
import os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));os.environ["BELLWETHER_AI"]="0"
from backend.core.game import Game,INITIAL_STATE
from backend.core.seasonal_model import SEASONAL_MODEL,SEASONAL_PROFILES

def check(n,o): print(("PASS " if o else "FAIL ")+n); return bool(o)
r=[];g=Game();g.state=deepcopy(INITIAL_STATE);g.state["season"]={"id":"deep_winter","label":"Deep winter","temperature_range_c":[-3,8],"daylight":"very short days","character":"cold"}
r.append(check("seasonal runtime schema present","seasonal_life" in g.state))
SEASONAL_MODEL.refresh(g.state)
r.append(check("season selects authored ecology",g.state["seasonal_life"]["current_profile"]=="deep_winter" and "dormant" in g.state["seasonal_life"]["ecology"]["vegetation"]))
r.append(check("wildlife ambience responds to season","small birds" in g.state["ambient"]["wildlife"].lower()))
r.append(check("village rhythm responds to season","daylight" in g.state["ambient"]["village"].lower()))
g.state["weather"]["state"]="heavy_rain";SEASONAL_MODEL.refresh(g.state)
r.append(check("weather changes ecology activity level",g.state["seasonal_life"]["ecology"]["activity_level"]=="sheltered"))
r.append(check("location ecology context available","ecology" in SEASONAL_MODEL.location_context(g.state,"ashcroft_cottage")))
r.append(check("daily seasonal snapshot persists","1" in g.state["seasonal_life"]["day_snapshots"]))
g.advance(1500)
r.append(check("seasonal state advances with simulation",str(g.state["day"]) in g.state["seasonal_life"]["day_snapshots"]))
old=deepcopy(INITIAL_STATE);old.pop("seasonal_life",None);g.state=old;g.migrate_state();r.append(check("old-save seasonal-life migration","seasonal_life" in g.state))
canon=SEASONAL_PROFILES["deep_winter"]["vegetation"];g.state["seasonal_life"]["ecology"]["vegetation"]="impossible";r.append(check("runtime cannot mutate authored seasonal canon",SEASONAL_PROFILES["deep_winter"]["vegetation"]==canon))
print(f"Part 8 passes: {sum(r)}/{len(r)}");raise SystemExit(0 if all(r) else 1)
