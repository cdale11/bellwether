#!/usr/bin/env python3
from copy import deepcopy
import os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));os.environ["BELLWETHER_AI"]="0"
from backend.core.game import Game,INITIAL_STATE
from backend.core.event_model import EVENT_MODEL,EVENTS
from backend.core.job_model import JOB_MODEL

def check(n,o):print(("PASS " if o else "FAIL ")+n);return bool(o)
r=[];g=Game();g.state=deepcopy(INITIAL_STATE)
r.append(check("event runtime schema present","dynamic_events" in g.state and "active" in g.state["dynamic_events"]))
ok,msg=EVENT_MODEL.start(g.state,"late_delivery",duration_minutes=30)
r.append(check("event activation persists",ok and "late_delivery" in g.state["dynamic_events"]["active"]))
r.append(check("event creates world overlay",any(x.startswith("event:late_delivery:") for x in g.state["world_model"]["location_modifiers"]["village_shop"])))
r.append(check("delivery event changes shop supply",g.state["economy"]["shop_stock"]["village_shop"]["groceries"]<=1))
r.append(check("location exposes active event context",EVENT_MODEL.location_context(g.state,"village_shop")[0]["id"]=="late_delivery"))
g.advance(40)
r.append(check("event expires through simulation time","late_delivery" not in g.state["dynamic_events"]["active"]))
r.append(check("event cleanup removes world overlay",not any(x.startswith("event:late_delivery:") for x in g.state["world_model"]["location_modifiers"]["village_shop"])))
r.append(check("delivery completion restocks affected goods",g.state["economy"]["shop_stock"]["village_shop"]["groceries"]>=8))
g=Game();g.state=deepcopy(INITIAL_STATE);g.state["location"]="bakery";g.state["minute"]=480;JOB_MODEL.apply(g.state,"bakery_helper");EVENT_MODEL.start(g.state,"bakery_oven_repair")
r.append(check("event blocks affected job action",not any(a[0]=="job:work:bakery_helper" for a in JOB_MODEL.available_actions(g.state))))
b=g.state["money"];g.perform("job:work:bakery_helper");r.append(check("server rejects stale blocked shift",g.state["money"]==b and g.state["jobs"]["total_shifts"]==0))
g=Game();g.state=deepcopy(INITIAL_STATE);EVENT_MODEL.start(g.state,"green_workday")
r.append(check("NPC activity responds to event","workday" in g.state["npcs"]["mara"]["activity"]))
old=deepcopy(INITIAL_STATE);old.pop("dynamic_events",None);g.state=old;g.migrate_state();r.append(check("old-save dynamic-event migration","dynamic_events" in g.state))
canon=EVENTS["late_delivery"]["duration_minutes"];g.state["dynamic_events"]["counter"]=999;r.append(check("runtime events cannot mutate authored event canon",EVENTS["late_delivery"]["duration_minutes"]==canon))
print(f"Part 7 passes: {sum(r)}/{len(r)}");raise SystemExit(0 if all(r) else 1)
