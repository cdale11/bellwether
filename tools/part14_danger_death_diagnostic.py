#!/usr/bin/env python3
from copy import deepcopy
import os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));os.environ['BELLWETHER_AI']='0'
from backend.core.game import Game,INITIAL_STATE
from backend.core.danger_model import DANGER_MODEL
def check(n,c): print(('PASS ' if c else 'FAIL ')+n); return bool(c)
g=Game();g.state=deepcopy(INITIAL_STATE);g.migrate_state();r=[]
r.append(check('danger schema validates',DANGER_MODEL.validate()))
r.append(check('fresh player alive',g.state['danger']['status']=='alive' and not g.state['danger']['injuries']))
g.state['location']='riverside_path';g.state['village_brain']['supernatural_pressure']=4;g.state['systemic_horror']['experienced']=['a'];g.state['village_brain']['pulse_count']=10
r.append(check('causal hazard becomes eligible','riverbank_slip' in DANGER_MODEL.eligible(g.state)))
r.append(check('first exposure produces warning not injury',g.evaluate_danger() is False and 'riverbank_slip' in g.state['danger']['warnings_seen'] and not g.state['danger']['injuries']))
g.state['village_brain']['pulse_count']=20;r.append(check('repeated risk can injure',g.evaluate_danger() and 'sprained_ankle' in g.state['danger']['injuries']))
r.append(check('injury creates visible treatment action',any(a['id']=='danger:treat' for a in g.view()['actions'])))
r.append(check('treatment changes injury state',g.treat_injury() and g.state['danger']['injuries']['sprained_ankle']['treated']))
# fatality requires accumulated vulnerability and unwarned severe hazard
g2=Game();g2.state=deepcopy(INITIAL_STATE);g2.migrate_state();g2.state['location']='village_road';g2.state['village_brain']['supernatural_pressure']=10;g2.state['systemic_horror']['experienced']=['a','b'];g2.state['danger']['risk']=6;g2.state['village_brain']['pulse_count']=20
e=DANGER_MODEL.apply(g2.state,'night_road_collision');r.append(check('severe causal hazard can terminate run',e['fatal'] and g2.state['danger']['status']=='dead' and g2.state['branch_state']['run_complete']))
r.append(check('terminal state blocks ordinary actions',g2.actions()==[{'id':'new_run','label':'Begin another run','kind':'story'}]))
r.append(check('invented hazard rejected',DANGER_MODEL.apply(g.state,'invented_hazard') is None))
old=deepcopy(INITIAL_STATE);old.pop('danger',None);g3=Game();g3.state=old;g3.migrate_state();r.append(check('old-save danger migration','danger' in g3.state and g3.state['danger']['status']=='alive'))
before=deepcopy(DANGER_MODEL.hazards);DANGER_MODEL.apply(g.state,'riverbank_slip');r.append(check('runtime danger cannot mutate authored catalogue',before==DANGER_MODEL.hazards))
print(f'Part 14 passes: {sum(r)}/{len(r)}');raise SystemExit(0 if all(r) else 1)
