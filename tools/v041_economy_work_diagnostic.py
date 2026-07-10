#!/usr/bin/env python3
from copy import deepcopy
from backend.core.game import INITIAL_STATE
from backend.core.economy_model import ECONOMY_MODEL
from backend.core.job_model import JOB_MODEL

def check(name, cond):
 print(('PASS' if cond else 'FAIL'), name)
 if not cond: raise AssertionError(name)

s=deepcopy(INITIAL_STATE)
# simulate v0.4.0-shaped state
s['economy'].pop('market',None); s['economy']['schema_version']=1
s['jobs']['schema_version']=1
ECONOMY_MODEL.migrate(s); JOB_MODEL.migrate(s)
check('old state migrates market', 'market' in s['economy'] and s['economy']['schema_version']==2)
check('old state migrates jobs', s['jobs']['schema_version']==2 and 'career_history' in s['jobs'])

s['location']='village_shop'; before=s['money']; ok,msg=ECONOMY_MODEL.buy(s,'village_shop','tea')
check('purchase is authoritative', ok and s['money']<before and s['economy']['ledger'][-1]['kind']=='purchase')

s['player_activities']['garden']['harvest_store']['lettuce']=4
s['economy']['market']['produce_demand']['lettuce']=1.5
before=s['money']; ok,msg=ECONOMY_MODEL.sell_produce(s,'lettuce')
check('produce demand affects sale', ok and s['money']-before>=8)

s['day']=2; snap=ECONOMY_MODEL.daily_tick(s)
check('daily market tick persists', snap is not None and s['economy']['market']['last_tick_day']==2)
check('daily tick idempotent', ECONOMY_MODEL.daily_tick(s) is None)

s['location']='bakery'; s['minute']=480; s['day']=2
ok,msg=JOB_MODEL.apply(s,'bakery_helper'); check('job application works',ok)
for day in range(2,7):
 s['day']=day; s['minute']=480
 ok,msg,mins,wage=JOB_MODEL.work(s,'bakery_helper')
 check(f'shift {day} works',ok)
check('wage progression unlocks', JOB_MODEL.current_wage(s,'bakery_helper')==8)
check('reliability grows', s['jobs']['employment']['bakery_helper']['reliability']>50)
ok,msg=JOB_MODEL.leave(s,'bakery_helper'); check('voluntary resignation persists',ok and not s['jobs']['employment']['bakery_helper']['active'])

print('v0.4.1 economy/work diagnostic: 15/15 PASS')
