from backend.core.game import Game
from backend.core.player_business_model import PLAYER_BUSINESS_MODEL
checks=[]
def ck(n,v): checks.append((n,bool(v))); print(('PASS' if v else 'FAIL'),n)
g=Game();s=g.state;g.migrate_state();ck('migration','player_businesses' in s)
s['money']=300;s['location']='village_green';s['player_activities']['garden']['harvest_store']['radish']=5
ck('startup_action','business:start:produce_stall' in dict(PLAYER_BUSINESS_MODEL.actions(s)))
ok,_,_=PLAYER_BUSINESS_MODEL.perform(s,'business:start:produce_stall');ck('startup',ok and s['money']==272)
ok,_,_=PLAYER_BUSINESS_MODEL.perform(s,'business:operate:produce_stall');ck('manual_operation',ok and s['player_activities']['garden']['harvest_store']['radish']==2)
s['location']='workshop_yard';ck('workspace_gate','business:start:repair_workshop' not in dict(PLAYER_BUSINESS_MODEL.actions(s)))
s['property']['leases']['workshop_lease']={'daily_rent':2};ck('workspace_unlock','business:start:repair_workshop' in dict(PLAYER_BUSINESS_MODEL.actions(s)))
s['location']='village_green';ok,_,_=PLAYER_BUSINESS_MODEL.perform(s,'business:mode:produce_stall');ck('mode_switch',ok and s['player_businesses']['enterprises']['produce_stall']['mode']=='manager_operated')
ok,_,_=PLAYER_BUSINESS_MODEL.perform(s,'business:hire:produce_stall');ck('manager_hire',ok and s['player_businesses']['enterprises']['produce_stall']['staff']==1)
s['day']=2;r=PLAYER_BUSINESS_MODEL.daily_tick(s);ck('daily_accounting',bool(r) and r[0]['business']=='produce_stall')
ck('economy_ledger',any(x.get('kind','').startswith('player_business_') for x in s['economy']['ledger']))
g.state=s;ck('public_view','player_business_overview' in g.view()['state'])
print(f"RESULT {sum(v for _,v in checks)}/{len(checks)}")
raise SystemExit(0 if all(v for _,v in checks) else 1)
