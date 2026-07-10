from copy import deepcopy
from backend.core.game import INITIAL_STATE
from backend.core.systemic_horror_integration_model import SYSTEMIC_HORROR_INTEGRATION_MODEL as M
checks=[]
def ck(n,x): checks.append((n,bool(x)))
s=deepcopy(INITIAL_STATE); rt=M.migrate(s); ck('migration',rt['schema_version']==1)
s['day']=2; s['village_brain']['supernatural_pressure']=30; s['town_mind']['strategy']['active_strategy']='routine_pressure'
r=M.daily_tick(s); ck('day2_consequence',bool(r)); ck('history',len(rt['consequence_history'])==1); ck('bounded_severity',0<=rt['severity']<=5)
# property personalization
p=deepcopy(INITIAL_STATE); p['day']=2; p['village_brain']['supernatural_pressure']=50; p['town_mind']['strategy']['active_strategy']='property_pressure'; p['property']['owned']={'x':{}}
before=p['player_status']['cottage']['condition']; row=M.daily_tick(p); ck('property_target',row['target']=='home'); ck('recoverable_wear',p['player_status']['cottage']['condition']<before and p['player_status']['cottage']['condition']>=before-1.5)
# resistance absorption
q=deepcopy(p); q['systemic_horror_integration']=M.runtime_defaults(); q['day']=3; q['resistance']['protected_domains']['property_pressure']=5
before=q['player_status']['cottage']['condition']; row=M.daily_tick(q); ck('resistance_absorbs',row['effect']=='pressure_absorbed' and q['player_status']['cottage']['condition']==before)
# canon untouched
z=deepcopy(INITIAL_STATE); z['day']=2; z['village_brain']['supernatural_pressure']=80; before=deepcopy(z['authored_story']); M.daily_tick(z); ck('canon_unchanged',z['authored_story']==before)
ck('public_authority','authored truth' in M.public(z)['authority']); ck('public_surface',M.public(z)['phase'] in ('dormant','encroaching','personalized','acute'))
for n,x in checks: print(('PASS' if x else 'FAIL'),n)
print(f'{sum(x for _,x in checks)}/{len(checks)} PASS')
raise SystemExit(0 if all(x for _,x in checks) else 1)
