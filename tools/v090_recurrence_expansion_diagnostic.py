#!/usr/bin/env python3
from copy import deepcopy
import os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT)); os.environ['BELLWETHER_AI']='0'
from backend.core.game import Game,INITIAL_STATE
from backend.core.recurrence_model import RECURRENCE_MODEL

def check(n,c): print(('PASS ' if c else 'FAIL ')+n); return bool(c)
r=[]
g=Game(); g.state=deepcopy(INITIAL_STATE); g.migrate_state(); s=g.state
s['day']=12; s['danger']['status']='dead'; s['danger']['terminal_reason']='death'; s['danger']['death']={'hazard_id':'night_road_collision'}; s['danger']['warnings_seen']=['riverbank_slip']
s['branch_state']['run_complete']=True; s['systemic_horror']['domain_counts']={'geography':3,'ecology':2}
s['player_identity']['dominant_traits']=['routine','inquiry']; s['player_life']['cottage_care']=80
s['relationships']['jonah'].update({'trust':6,'affinity':5,'familiarity':8}); s['relationships']['mara'].update({'trust':0,'affinity':0,'familiarity':0})
s['flags']['read_letter']=True; s['flags']['reached_cottage']=True
rec=RECURRENCE_MODEL.carry_forward(s)
r.append(check('schema v2',rec['schema_version']==2))
r.append(check('run advances',rec['run_index']==2 and rec['completed_runs'][-1]['run']==1))
r.append(check('fragments begin latent',len(rec['latent_fragments'])>=1 and len(rec['returned_fragments'])==0))
r.append(check('danger instinct persists',any(x.get('hazard_id')=='night_road_collision' for x in rec['instincts'])))
r.append(check('home anchoring derived','home' in rec['anchors'] and rec['anchors']['home']['strength']>=2))
r.append(check('story continuity stored as residue',any('read_letter' in x.get('flags',[]) for x in rec['story_residues'])))
r.append(check('npc echoes asymmetric','jonah' in rec['npc_echoes'] and 'mara' not in rec['npc_echoes']))
new=deepcopy(INITIAL_STATE); RECURRENCE_MODEL.apply_to_new_run(new,rec)
r.append(check('anchor changes awakening context',new['location']=='ashcroft_cottage'))
r.append(check('world still resets',new['day']==1 and not new['systemic_horror']['experienced']))
r.append(check('residue exposed without setting old flags',new['story_integration'].get('recurrence_residues') and not new['flags']['read_letter']))
first=RECURRENCE_MODEL.advance_day(new)
r.append(check('fragmented return releases bounded memory',len([x for x in first if x['speaker']=='Memory'])<=1 and len(new['recurrence']['returned_fragments'])==1))
again=RECURRENCE_MODEL.advance_day(new)
r.append(check('same day idempotent',again==[]))
new['day']=3; later=RECURRENCE_MODEL.advance_day(new)
r.append(check('later day can return another fragment',len([x for x in later if x['speaker']=='Memory'])<=1))
r.append(check('developer recurrence context bounded',set(RECURRENCE_MODEL.developer_context(new))=={'schema_version','run_index','anchors','latent_fragments','returned_fragments','npc_echoes','story_residues','awakening_history'}))
old={'schema_version':1,'run_index':2,'completed_runs':[],'fragments':[{'id':'routine','text':'x','origin_run':1}],'instincts':[],'npc_echoes':{},'transition_history':[]}
RECURRENCE_MODEL.migrate(old)
r.append(check('schema1 migration preserves visible fragment',old['schema_version']==2 and old['returned_fragments'][0]['id']=='routine'))
print(f'v0.9.0 passes: {sum(r)}/{len(r)}'); raise SystemExit(0 if all(r) else 1)
