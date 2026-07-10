#!/usr/bin/env python3
from copy import deepcopy
from backend.core.game import Game, INITIAL_STATE
from backend.core.population_model import POPULATION_MODEL
from backend.core.society_model import SOCIETY_MODEL

g=Game.__new__(Game);g.state=deepcopy(INITIAL_STATE);g._overview_cache_key=None;g._overview_cache=None;g.migrate_state()
checks=[]
def ck(n,x): checks.append((n,bool(x)));print(('PASS' if x else 'FAIL'),n)
ck('population_seeded',len(POPULATION_MODEL.migrate(g.state)['residents'])>=20)
for d in range(1,15):
 g.state['day']=d;g.state['minute']=720;POPULATION_MODEL.advance_batch(g.state);SOCIETY_MODEL.advance_day(g.state,POPULATION_MODEL)
s=SOCIETY_MODEL.migrate(g.state)
ck('households',bool(s['households']))
ck('employment_accounting',sum(s['employment'][k] for k in ('employed','seeking','retired','students'))==len(POPULATION_MODEL.migrate(g.state)['residents']))
ck('weekly_snapshots',len(s['weekly_snapshots'])>=2)
ck('social_metrics',s['social']['strong_ties']>=0 and s['social']['isolated']>=0)
ck('migration_pressure_bounded',0<=s['migration']['pressure']<=1)
ck('years_elapsed',s['years_elapsed']>0)
r=next(iter(POPULATION_MODEL.migrate(g.state)['residents']));before=s['social']['encounters'];SOCIETY_MODEL.note_encounter(g.state,r);ck('resident_encounter',s['social']['encounters']==before+1)
ck('public_surface',bool(SOCIETY_MODEL.public(g.state).get('employment')))
print(f'{sum(x for _,x in checks)}/{len(checks)} passed')
raise SystemExit(0 if all(x for _,x in checks) else 1)
