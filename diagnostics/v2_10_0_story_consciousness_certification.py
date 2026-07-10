from copy import deepcopy
from backend.core.game import INITIAL_STATE
from backend.core.story_consciousness_integration_model import STORY_CONSCIOUSNESS_INTEGRATION_MODEL as M
s=deepcopy(INITIAL_STATE); checks=[]
def ck(n,x): checks.append((n,bool(x)))
rt=M.migrate(s); ck('migration',rt['schema_version']==1)
s['day']=2; row=M.daily_tick(s); ck('day2_response',bool(row)); ck('history',len(rt['history'])==1)
ck('authority', 'cannot create' in M.public(s)['authority'])
# ordinary-life avoidance produces distraction
s2=deepcopy(INITIAL_STATE); s2['day']=2; s2['player_life']['activity_history']=[{}]*20
r=M.daily_tick(s2); ck('ordinary_distraction',r['posture']=='distract')
# deep story produces confrontation
s3=deepcopy(INITIAL_STATE); s3['day']=2; s3['authored_story']['chapter']='eleanor_method'
r=M.daily_tick(s3); ck('late_story_confront',r['posture']=='confront')
# signal tracking is idempotent
M.record_authored_signal(s,'x','arrival'); M.record_authored_signal(s,'x','arrival'); ck('signal_idempotent',len(rt['signals'])==1)
# no canon mutation
before=deepcopy(s3['authored_story']); M.daily_tick(s3); ck('canon_unchanged',s3['authored_story']==before)
ck('public_surface',M.public(s).get('posture') in ('normalize','distract','isolate','contradict','confront','observe'))
ck('bounded_strength',1<=M.public(s)['response_strength']<=3)
for n,x in checks: print(('PASS' if x else 'FAIL'),n)
print(f"{sum(x for _,x in checks)}/{len(checks)} PASS")
raise SystemExit(0 if all(x for _,x in checks) else 1)
