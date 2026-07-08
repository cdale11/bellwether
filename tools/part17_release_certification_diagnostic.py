#!/usr/bin/env python3
"""Part 17 final integration and release certification invariants."""
from copy import deepcopy
import json, os, py_compile, random, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT)); os.environ['BELLWETHER_AI']='0'
from backend.core.game import Game, INITIAL_STATE
from backend.core.danger_model import DANGER_MODEL

def check(name, cond): print(('PASS ' if cond else 'FAIL ')+name); return bool(cond)
r=[]
# Package/source integrity.
errors=[]; count=0
for root in ('backend','tools'):
 for p in (ROOT/root).rglob('*.py'):
  if '__pycache__' in p.parts: continue
  count+=1
  try: py_compile.compile(str(p),doraise=True)
  except Exception as e: errors.append(f'{p}: {e}')
r.append(check('all project Python compiles',not errors and count>=50))
json_ok=True
for p in (ROOT/'content').rglob('*.json'):
 try: json.loads(p.read_text(encoding='utf-8'))
 except Exception: json_ok=False
r.append(check('all authored JSON catalogues parse',json_ok))
r.append(check('launch script executable',bool((ROOT/'run.sh').stat().st_mode & 0o111)))
# Action contract across ordinary, injured, dialogue, and terminal states.
g=Game(); g.state=deepcopy(INITIAL_STATE); g.migrate_state()
def action_contract(game): return bool(game.actions()) and all({'id','label','kind'} <= set(a) for a in game.view()['actions'])
r.append(check('ordinary visible action schema complete',action_contract(g)))
g.state['location']='riverside_path'; g.state['village_brain']['supernatural_pressure']=4; g.state['systemic_horror']['experienced']=['a']; g.state['village_brain']['pulse_count']=10; g.evaluate_danger(); g.state['village_brain']['pulse_count']=20; g.evaluate_danger()
r.append(check('injury treatment action has complete schema',action_contract(g) and any(a['id']=='danger:treat' and a['kind']=='life' for a in g.view()['actions'])))
gd=Game(); gd.state=deepcopy(INITIAL_STATE); gd.migrate_state(); gd.state['location']='village_road'; gd.state['village_brain']['supernatural_pressure']=10; gd.state['systemic_horror']['experienced']=['road_repetition']; gd.state['systemic_horror']['domain_counts']={'geography':1}; gd.state['danger']['risk']=6; gd.state['village_brain']['pulse_count']=20; DANGER_MODEL.apply(gd.state,'night_road_collision')
r.append(check('terminal action schema complete',gd.actions()==[{'id':'new_run','label':'Begin another run','kind':'story'}]))
v=gd.perform('new_run'); r.append(check('death-to-recurrence handoff playable',v['state']['danger']['status']=='alive' and v['state']['recurrence']['run_index']==2 and action_contract(gd)))
# Random visible-action fuzz: player can only choose what the UI exposes.
rng=random.Random(1702); fuzz_ok=True
for run in range(2):
 gf=Game()
 for _ in range(180):
  try:
   acts=gf.view()['actions'];
   if not acts or any(not {'id','label','kind'} <= set(a) for a in acts): fuzz_ok=False; break
   a=rng.choice(acts)
   if a['id'].startswith('free_talk:'): gf.free_talk(a['id'].split(':',1)[1],'Morning. How are you?')
   else: gf.perform(a['id'])
  except Exception:
   fuzz_ok=False; break
r.append(check('visible-action fuzz play remains valid',fuzz_ok))
# Save-state round trip through JSON serialization and migration.
gs=Game(); gs.state=deepcopy(INITIAL_STATE); gs.migrate_state(); gs.state['money']=37; gs.state['recurrence']['run_index']=3
roundtrip=json.loads(json.dumps(gs.state)); gs2=Game(); gs2.state=roundtrip; gs2.migrate_state()
r.append(check('full state JSON round-trip and migration',gs2.state['money']==37 and gs2.state['recurrence']['run_index']==3))
# Frozen baseline interfaces remain present.
required=('world_model','npc_lives','npc_social_web','npc_knowledge','mystery_investigation','systemic_horror','player_identity','danger','recurrence','content_progression','player_activities','economy','jobs','dynamic_events','seasonal_life')
r.append(check('all Parts 1-16 state substrates coexist',all(k in gs2.state for k in required)))
# Part 6 seed invariant retained at final release.
gseed=Game(); gseed.state=deepcopy(INITIAL_STATE); gseed.migrate_state(); gseed.state['location']='ashcroft_cottage';
from backend.core.activity_model import ACTIVITY_MODEL
acts=ACTIVITY_MODEL.available_garden_actions(gseed.state)
r.append(check('fresh garden cannot sow unowned seeds',not any(a.startswith('garden:sow:') for a,_ in acts)))
# Version and no dev suffix.
version=(ROOT/'VERSION').read_text().strip(); r.append(check('release lineage valid',version.startswith(('0.2.','0.3.'))))
print(f'Part 17 passes: {sum(r)}/{len(r)}')
raise SystemExit(0 if all(r) else 1)
