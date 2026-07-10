from copy import deepcopy
from backend.core.game import Game, INITIAL_STATE
from backend.core.failure_recovery_model import FAILURE_RECOVERY_MODEL
from backend.core.danger_model import DANGER_MODEL
from backend.core.horror_model import HORROR_MODEL

def game():
 g=Game.__new__(Game);g.state=deepcopy(INITIAL_STATE);g._overview_cache_key=None;g._overview_cache=None;g.migrate_state();return g
checks=[]
def check(name,ok,detail):checks.append((name,bool(ok),detail))
g=game();base=FAILURE_RECOVERY_MODEL.evaluate_adaptive_pressure(g.state);check('baseline_pressure',base['band'] in {'stable','watchful'},base)
g.state['money']=0;g.state['danger']['injuries']={'sprained_ankle':{'severity':1,'recovery_days':2,'acquired_day':1,'treated':False}};g.state['horror_aftermath']['player']['strain']=80
stressed=FAILURE_RECOVERY_MODEL.evaluate_adaptive_pressure(g.state);check('adaptive_pressure_rises',stressed['pressure']>base['pressure'],stressed)
g.state['inventory']=['sturdy boots'];g.state['danger']['warnings_seen']=['quarry_loose_stone'];sev,prep=FAILURE_RECOVERY_MODEL.mitigate(g.state,'quarry_loose_stone',2);check('preparation_mitigates',sev==1 and prep['score']>=2,(sev,prep))
h=game();aid=next(iter(HORROR_MODEL.anomalies));a=HORROR_MODEL.anomalies[aid];h.state['location']=a['location'];ev=HORROR_MODEL.apply(h.state,aid);check('bounded_horror_apply',bool(ev) and HORROR_MODEL.location_context(h.state,a['location']) is not None,ev and ev['id'])
rt=FAILURE_RECOVERY_MODEL.migrate(g.state);check('diagnostic_history',bool(rt['adaptive']['daily_history']),rt['adaptive']['daily_history'])
print('Bellwether v1.4.0 Adaptive Horror and Failure Depth Diagnostic')
for n,ok,d in checks:print(('PASS' if ok else 'FAIL'),n,'|',d)
print(f'{sum(x[1] for x in checks)}/{len(checks)} passed')
raise SystemExit(0 if all(x[1] for x in checks) else 1)
