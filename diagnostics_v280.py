from copy import deepcopy
from backend.core.game import INITIAL_STATE
from backend.core.village_evolution_model import VILLAGE_EVOLUTION_MODEL
s=deepcopy(INITIAL_STATE)
checks=[]
def ck(n,v): checks.append((n,bool(v)))
rt=VILLAGE_EVOLUTION_MODEL.migrate(s);ck('migration_safe',rt['schema_version']==1 and len(rt['resident_status'])>=20)
s['day']=28;s['society']['migration']['pressure']=.8
ev=VILLAGE_EVOLUTION_MODEL.advance_day(s);ck('departure_materialises',any(x['kind']=='departure' for x in ev));ck('resident_preserved',len(s['population']['residents'])>=20);ck('summary_departure',rt['summary']['departures']==1)
# closure path
s2=deepcopy(INITIAL_STATE);s2['day']=14;s2['economy']['market']['businesses']['bakery']['health']=5
ev2=VILLAGE_EVOLUTION_MODEL.advance_day(s2);ck('closure_recorded',any(x['kind']=='business_closure' for x in ev2));ck('venture_registry',VILLAGE_EVOLUTION_MODEL.migrate(s2)['ventures']['bakery']['status']=='closed')
# land evolution
s3=deepcopy(INITIAL_STATE);s3['day']=56
ev3=VILLAGE_EVOLUTION_MODEL.advance_day(s3);ck('land_change',any(x['kind']=='land_use_change' for x in ev3));ck('public_surface','recent_events' in VILLAGE_EVOLUTION_MODEL.public(s3))
ck('event_history',len(VILLAGE_EVOLUTION_MODEL.migrate(s3)['events'])>0)
ck('version',open('VERSION').read().strip()=='2.8.0')
for n,v in checks: print(('PASS' if v else 'FAIL'),n)
print(f'{sum(v for _,v in checks)}/{len(checks)} PASS')
raise SystemExit(0 if all(v for _,v in checks) else 1)
