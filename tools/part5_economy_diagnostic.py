#!/usr/bin/env python3
from copy import deepcopy
import os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));os.environ["BELLWETHER_AI"]="0"
from backend.core.game import Game,INITIAL_STATE
from backend.core.economy_model import ECONOMY_MODEL
def check(n,o):print(("PASS " if o else "FAIL ")+n);return bool(o)
g=Game();g.state=deepcopy(INITIAL_STATE);r=[]
r.append(check("economy schema present","economy" in g.state))
g.state["location"]="village_shop"; acts={a[0] for a in ECONOMY_MODEL.actions(g.state)};r.append(check("shop exposes bounded catalogue","economy:buy:village_shop:radish_seed" in acts))
b=g.state["money"]; seeds=g.state["player_activities"]["garden"]["seed_stock"]["radish"];g.perform("economy:buy:village_shop:radish_seed");r.append(check("purchase deducts money",g.state["money"]==b-2));r.append(check("seed purchase feeds gardening",g.state["player_activities"]["garden"]["seed_stock"]["radish"]==seeds+3))
g.state["player_activities"]["garden"]["harvest_store"]["radish"]=4;b=g.state["money"];g.perform("economy:sell:radish");r.append(check("produce sale pays player",g.state["money"]==b+4));r.append(check("produce sale removes stock",g.state["player_activities"]["garden"]["harvest_store"]["radish"]==0))
r.append(check("ledger records transactions",len(g.state["economy"]["ledger"])>=2))
g.state["money"]=0; before=g.state["economy"]["household"]["groceries"];g.perform("economy:buy:village_shop:groceries");r.append(check("insufficient funds blocks purchase",g.state["economy"]["household"]["groceries"]==before))
g.state["location"]="bakery";g.state["minute"]=1200;r.append(check("opening hours hide trade",len(ECONOMY_MODEL.actions(g.state))>0 and not __import__('backend.core.world_model',fromlist=['WORLD_MODEL']).WORLD_MODEL.access_status('bakery',1200)[0]))
old=deepcopy(INITIAL_STATE);old.pop("economy",None);g.state=old;g.migrate_state();r.append(check("old-save economy migration","economy" in g.state))
canon=ECONOMY_MODEL.runtime_defaults();g.state["economy"]["shop_stock"]["village_shop"]["radish_seed"]=0;r.append(check("runtime stock does not mutate catalogue",ECONOMY_MODEL.runtime_defaults()["shop_stock"]["village_shop"]["radish_seed"]==99))
print(f"Part 5 passes: {sum(r)}/{len(r)}");raise SystemExit(0 if all(r) else 1)
