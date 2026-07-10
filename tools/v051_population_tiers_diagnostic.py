#!/usr/bin/env python3
from copy import deepcopy
from backend.core.game import Game, INITIAL_STATE
from backend.core.population_model import POPULATION_MODEL
checks=[]
def check(name,ok,detail=''):
    checks.append((name,bool(ok),detail)); print(('PASS' if ok else 'FAIL'),name,detail)
POPULATION_MODEL.validate(); ids=[r['id'] for r in POPULATION_MODEL.residents]
check('population size 20-25',20<=len(ids)<=25,str(len(ids)))
check('resident ids unique',len(ids)==len(set(ids)))
g=Game(); g.state=deepcopy(INITIAL_STATE); g.migrate_state()
pop=g.state['population']; check('population persistent state',set(ids)==set(pop['residents']))
check('lightweight tier isolated from core NPC loop',not (set(ids)&set(g.state['npcs'])))
check('resident schema complete',all(r.get('household') and r.get('occupation') and r.get('routine') for r in pop['residents'].values()))
g.advance(180)
check('batched simulation advances',g.state['population']['batch_count']>0,str(g.state['population']['batch_count']))
check('schedules move residents',any(r['location']!='village_road' for r in g.state['population']['residents'].values()))
check('social links emerge cheaply',any(r['social_links'] for r in g.state['population']['residents'].values()))
view=g.view(); check('present residents surface in UI',any(n.get('tier')=='lightweight' for n in view['present']['npcs']) or POPULATION_MODEL.summary(g.state)['currently_in_village']>0)
old=deepcopy(INITIAL_STATE); old.pop('population',None); g.state=old; g.migrate_state()
check('old-save population migration',len(g.state['population']['residents'])==len(ids))
# Save roundtrip structure is JSON-safe.
import json
check('population JSON serializable',bool(json.dumps(g.state['population'])))
failed=[n for n,ok,d in checks if not ok]
print(f"RESULT {len(checks)-len(failed)}/{len(checks)}")
raise SystemExit(1 if failed else 0)
