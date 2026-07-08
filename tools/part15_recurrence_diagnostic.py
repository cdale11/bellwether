#!/usr/bin/env python3
from copy import deepcopy
import os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));os.environ['BELLWETHER_AI']='0'
from backend.core.game import Game,INITIAL_STATE
from backend.core.recurrence_model import RECURRENCE_MODEL

def check(n,c): print(('PASS ' if c else 'FAIL ')+n); return bool(c)
r=[]; g=Game();g.state=deepcopy(INITIAL_STATE);g.migrate_state()
r.append(check('recurrence schema migrates',RECURRENCE_MODEL.migrate(g.state['recurrence'])['schema_version']==1))
r.append(check('fresh game begins first run',g.state['recurrence']['run_index']==1 and not g.state['recurrence']['completed_runs']))
# Construct a completed run with several sources of lossy memory.
g.state['danger']['status']='dead';g.state['danger']['terminal_reason']='death';g.state['danger']['death']={'hazard_id':'night_road_collision'};g.state['danger']['warnings_seen']=['riverbank_slip']
g.state['branch_state']['run_complete']=True
g.state['systemic_horror']['experienced']=[{'id':'x','domain':'geography'},{'id':'y','domain':'ecology'}]
g.state['player_identity']['dominant_traits']=['inquiry','routine']
g.state['relationships']['jonah']['trust']=5;g.state['relationships']['jonah']['warmth']=5
rec=RECURRENCE_MODEL.carry_forward(g.state)
r.append(check('completed run archived',len(rec['completed_runs'])==1 and rec['completed_runs'][0]['ended_by']=='death'))
r.append(check('new run index advances',rec['run_index']==2))
r.append(check('memory is bounded and lossy',0<len(rec['fragments'])<=3 and 'death' in [x['id'] for x in rec['fragments']]))
r.append(check('danger instinct survives recurrence',any(x.get('hazard_id')=='night_road_collision' for x in rec['instincts'])))
r.append(check('npc memory is asymmetric','jonah' in rec['npc_echoes'] and 'mara' not in rec['npc_echoes']))
new=deepcopy(INITIAL_STATE);RECURRENCE_MODEL.apply_to_new_run(new,rec)
r.append(check('new world state resets while recurrence persists',new['day']==1 and new['recurrence']['run_index']==2 and not new['systemic_horror']['experienced']))
r.append(check('instinct becomes bounded learned warning','night_road_collision' in new['danger']['warnings_seen']))
# Exercise actual Game new_run handoff.
g2=Game();g2.state=deepcopy(g.state);v=g2.perform('new_run')
r.append(check('terminal action creates recurrent run',v['state']['recurrence']['run_index']==2 and v['state']['danger']['status']=='alive'))
r.append(check('opening echoes are surfaced',any(m.get('speaker') in ('Narrator','Bellwether') for m in v['state']['history'][-4:])))
old=deepcopy(INITIAL_STATE);old.pop('recurrence',None);g3=Game();g3.state=old;g3.migrate_state();r.append(check('old-save recurrence migration','recurrence' in g3.state and g3.state['recurrence']['run_index']==1))
before=deepcopy(rec);RECURRENCE_MODEL.apply_to_new_run(deepcopy(INITIAL_STATE),rec);r.append(check('applying recurrence does not mutate archive',before==rec))
print(f'Part 15 passes: {sum(r)}/{len(r)}');raise SystemExit(0 if all(r) else 1)
