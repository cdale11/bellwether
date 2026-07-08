#!/usr/bin/env python3
from copy import deepcopy
import os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));os.environ["BELLWETHER_AI"]="0"
from backend.core.game import Game,INITIAL_STATE
from backend.core.job_model import JOB_MODEL,JOBS
def check(n,o):print(("PASS " if o else "FAIL ")+n);return bool(o)
r=[];g=Game();g.state=deepcopy(INITIAL_STATE)
r.append(check("fresh game has zero garden seed stock",all(v==0 for v in g.state["player_activities"]["garden"]["seed_stock"].values())))
g.state["location"]="ashcroft_cottage";g.state["player_activities"]["garden"]["soil_prepared"]=True
acts={a[0] for a in __import__('backend.core.activity_model',fromlist=['ACTIVITY_MODEL']).ACTIVITY_MODEL.available_garden_actions(g.state)}
r.append(check("empty inventory exposes no sow actions",not any(a.startswith("garden:sow:") for a in acts)))
before=list(g.state["player_activities"]["garden"]["plots"]);g.perform("garden:sow:radish")
r.append(check("direct sow without seed is rejected",g.state["player_activities"]["garden"]["plots"]==before))
g.state["location"]="village_shop";g.state["minute"]=600;g.perform("economy:buy:village_shop:radish_seed");r.append(check("purchased seeds enter garden inventory",g.state["player_activities"]["garden"]["seed_stock"]["radish"]==3))
g.state["location"]="ashcroft_cottage";g.perform("garden:sow:radish");r.append(check("sowing consumes one owned seed",g.state["player_activities"]["garden"]["seed_stock"]["radish"]==2 and g.state["player_activities"]["garden"]["plots"][0] is not None))
g=Game();g.state=deepcopy(INITIAL_STATE);g.state["location"]="bakery";g.state["minute"]=480
acts={a[0] for a in JOB_MODEL.available_actions(g.state)};r.append(check("job can be discovered at workplace","job:apply:bakery_helper" in acts))
g.perform("job:apply:bakery_helper");r.append(check("application creates persistent employment",g.state["jobs"]["employment"]["bakery_helper"]["active"]))
b=g.state["money"];g.perform("job:work:bakery_helper");r.append(check("completed shift pays wage",g.state["money"]==b+JOBS["bakery_helper"]["wage"]))
r.append(check("wage enters economy ledger",any(x["kind"]=="wage" for x in g.state["economy"]["ledger"])))
shifts=g.state["jobs"]["total_shifts"];g.perform("job:work:bakery_helper");r.append(check("duplicate same-day shift blocked",g.state["jobs"]["total_shifts"]==shifts))
old=deepcopy(INITIAL_STATE);old.pop("jobs",None);g.state=old;g.migrate_state();r.append(check("old-save jobs migration","jobs" in g.state))
canon=JOBS["bakery_helper"]["wage"];g.state["jobs"]["work_reputation"]=99;r.append(check("runtime work state cannot mutate job canon",JOBS["bakery_helper"]["wage"]==canon))
print(f"Part 6 passes: {sum(r)}/{len(r)}");raise SystemExit(0 if all(r) else 1)
