#!/usr/bin/env python3
from copy import deepcopy
import os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));os.environ['BELLWETHER_AI']='0'
from backend.core.game import Game,INITIAL_STATE
from backend.core.economy_model import ECONOMY_MODEL
from backend.core.job_model import JOB_MODEL
checks=[]
def check(n,x):checks.append(bool(x));print(('PASS ' if x else 'FAIL ')+n)
g=Game();g.state=deepcopy(INITIAL_STATE);ECONOMY_MODEL.migrate(g.state);m=g.state['economy']['market'];b=m['businesses']['bakery']
check('business health state',all(k in b for k in ('health','cash_reserve','staffing','supply','demand','trend')))
check('supply routes state',set(m['supply_routes'])=={'wholesale','farm','hardware','flour'})
g.state['day']=2;g.state['weather']['state']='storm';ECONOMY_MODEL.daily_tick(g.state);check('disruption lowers supply',m['supply_routes']['flour']<1.0)
b['health']=30;check('business strain changes employment wage',ECONOMY_MODEL.job_modifier(g.state,'bakery_helper')['wage_factor']<1)
b['health']=10;check('critical business can suspend hiring',not ECONOMY_MODEL.job_modifier(g.state,'bakery_helper')['available'])
b['health']=30;g.state['location']='bakery';g.state['money']=20;before=b['health'];ok,_=ECONOMY_MODEL.support_business(g.state,'bakery',5);check('player can support strained business',ok and b['health']>before and g.state['money']==15)
g.state['day']=3;ECONOMY_MODEL.daily_tick(g.state);check('market history records village change',len(m['history'])>=2 and 'business_health' in m['history'][-1])
check('village outlook computed',m['village_outlook'] in {'stable','uneasy','fragile'})
print(f'v1.1.0 economy/village-change diagnostic: {sum(checks)}/{len(checks)} PASS');raise SystemExit(0 if all(checks) else 1)
