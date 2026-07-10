from copy import deepcopy
from backend.core.game import INITIAL_STATE
from backend.core.town_mind_model import TOWN_MIND_MODEL

def check(name,cond):
 print(('PASS' if cond else 'FAIL'),name); return bool(cond)

def fresh():
 s=deepcopy(INITIAL_STATE); TOWN_MIND_MODEL.migrate(s); return s

results=[]
s=fresh(); results.append(check('migration',TOWN_MIND_MODEL.migrate(s)['schema_version']==2))
results.append(check('day1 restraint',TOWN_MIND_MODEL.strategic_daily_tick(s) is None))
s['day']=2; r=TOWN_MIND_MODEL.strategic_daily_tick(s); results.append(check('day2 response',bool(r)))
results.append(check('pressure logged',len(s['town_mind']['strategy']['pressure_log'])==1))
results.append(check('once per day',TOWN_MIND_MODEL.strategic_daily_tick(s) is None))
# Property playstyle must be observed and pressure existing state, not invent canon.
p=fresh(); p['day']=2; p['property']['leases']['meadow_lease']={'daily_rent':1}; before=p['property']['rent_arrears']; rr=TOWN_MIND_MODEL.strategic_daily_tick(p)
results.append(check('property strategy',rr and rr['strategy']=='property_pressure'))
results.append(check('property consequence',p['property']['rent_arrears']==before+1))
# Enterprise pressure
b=fresh(); b['day']=2; b['player_businesses']['enterprises']['produce_stall']={'cash':30,'health':70}; rb=TOWN_MIND_MODEL.strategic_daily_tick(b)
results.append(check('enterprise strategy',rb and rb['strategy']=='enterprise_pressure'))
results.append(check('business consequence',b['player_businesses']['enterprises']['produce_stall']['health']==69))
# Inquiry should reduce mystery leverage relative to avoidance.
i=fresh(); i['day']=2; i['investigation']['evidence']=['a','b','c','d','e','f']; i['player_identity']['traits']['inquiry']=70; TOWN_MIND_MODEL.observe_player(i)
results.append(check('observations inspect inquiry',i['town_mind']['strategy']['observations']['inquiry']>=6))
results.append(check('developer context auditable',bool(TOWN_MIND_MODEL.developer_context(i).get('observations'))))
print(f"RESULT {sum(results)}/{len(results)}")
raise SystemExit(0 if all(results) else 1)
