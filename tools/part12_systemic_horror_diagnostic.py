#!/usr/bin/env python3
from copy import deepcopy
import os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));os.environ['BELLWETHER_AI']='0'
from backend.core.game import Game,INITIAL_STATE
from backend.core.horror_model import HORROR_MODEL
def check(n,c): print(('PASS ' if c else 'FAIL ')+n); return bool(c)
g=Game();g.state=deepcopy(INITIAL_STATE);g.migrate_state();r=[]
r.append(check('horror schema validates',HORROR_MODEL.validate()))
r.append(check('fresh run has no eligible anomaly',HORROR_MODEL.eligible(g.state)==[]))
# establish learned normality and story gate
g.state['flags']['read_letter']=True;g.state['location']='village_green';g.state['player_life']['location_familiarity']['village_green']=6;g.state['player_life']['activity_history']=[{} for _ in range(8)];g.state['player_life']['location_familiarity']['bakery']=6;g.state['village_brain']['pulse_count']=20
r.append(check('learned normality exposes bounded anomaly','green_path_mismatch' in HORROR_MODEL.eligible(g.state)))
before=deepcopy(HORROR_MODEL.data);ok=g.maybe_apply_controlled_horror();r.append(check('eligible anomaly triggers',ok and 'green_path_mismatch' in g.state['systemic_horror']['experienced']))
r.append(check('anomaly creates world overlay','village_green' in g.state['world_model']['supernatural_overlays']))
r.append(check('legacy psychological consequence retained',g.state['psychological_state']['familiarity_disruptions']==1 and g.state['psychological_state']['unease']>0))
r.append(check('experienced anomaly cannot repeat','green_path_mismatch' not in HORROR_MODEL.eligible(g.state)))
ctx=g.view()['world_context'];r.append(check('active corruption visible in bounded world context',ctx.get('supernatural_overlay',{}).get('anomaly_id')=='green_path_mismatch'))
g.state['village_brain']['pulse_count']+=3;HORROR_MODEL.expire(g.state);r.append(check('temporary overlay expires','village_green' not in g.state['world_model']['supernatural_overlays']))
r.append(check('experienced history persists after overlay expiry','green_path_mismatch' in g.state['systemic_horror']['experienced']))
r.append(check('unknown anomaly rejected',HORROR_MODEL.apply(g.state,'invented_llm_anomaly') is None))
old=deepcopy(INITIAL_STATE);old.pop('systemic_horror',None);g2=Game();g2.state=old;g2.migrate_state();r.append(check('old-save horror migration','systemic_horror' in g2.state and 'active_overlays' in g2.state['systemic_horror']))
r.append(check('runtime cannot mutate authored horror canon',before==HORROR_MODEL.data))
print(f'Part 12 passes: {sum(r)}/{len(r)}');raise SystemExit(0 if all(r) else 1)
