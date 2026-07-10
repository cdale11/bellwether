#!/usr/bin/env python3
from copy import deepcopy
import json, os, py_compile, random, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT)); os.environ['BELLWETHER_AI']='0'
from backend.core.game import Game, INITIAL_STATE, WORLD

def ck(name, cond): print(('PASS ' if cond else 'FAIL ')+name); return bool(cond)
r=[]
r.append(ck('final version identity',(ROOT/'VERSION').read_text().strip()=='3.0.0'))
errs=[]
for base in ('backend','diagnostics','tools'):
 for p in (ROOT/base).rglob('*.py'):
  if '__pycache__' not in p.parts:
   try: py_compile.compile(str(p),doraise=True)
   except Exception as e: errs.append((str(p),str(e)))
r.append(ck('all Python compiles',not errs))
r.append(ck('all JSON parses',all((lambda p: (json.loads(p.read_text(encoding='utf-8')) is not None))(p) for p in (ROOT/'content').rglob('*.json'))))
# Every globally exposed investigation action must execute in every authored world location.
inv_ok=True
for loc in WORLD:
 for mode in ('observe','search'):
  try:
   g=Game(); g.state=deepcopy(INITIAL_STATE); g.migrate_state(); g.state['location']=loc
   g.state['player_life']['attentiveness']=10
   ids={a['id'] for a in g.view()['actions']}
   aid=f'investigate:{mode}'
   if aid not in ids: inv_ok=False; break
   g.perform(aid)
  except Exception as e:
   print('DETAIL investigation failure',loc,mode,repr(e)); inv_ok=False; break
r.append(ck('investigation actions valid across expanded world',inv_ok))
# deterministic visible-action fuzz
rng=random.Random(1702); fuzz=True
for run in range(2):
 g=Game()
 for _ in range(180):
  try:
   acts=g.view()['actions']
   if not acts or any(not {'id','label','kind'}<=set(a) for a in acts): fuzz=False; break
   a=rng.choice(acts)
   if a['id'].startswith('free_talk:'): g.free_talk(a['id'].split(':',1)[1],'Morning. How are you?')
   else: g.perform(a['id'])
  except Exception as e:
   print('DETAIL fuzz failure',a.get('id'),repr(e)); fuzz=False; break
r.append(ck('visible action fuzz remains valid',fuzz))
# full JSON roundtrip + migration
s=deepcopy(INITIAL_STATE); g=Game(); g.state=s; g.migrate_state(); g.state['money']=37; g.state['recurrence']['run_index']=3
blob=json.dumps(g.state); g2=Game(); g2.state=json.loads(blob); g2.migrate_state()
r.append(ck('full state JSON roundtrip and migration',g2.state['money']==37 and g2.state['recurrence']['run_index']==3))
# README/install identity
readme=(ROOT/'README.md').read_text(encoding='utf-8')
r.append(ck('README final identity','# Bellwether v3.0.0' in readme and 'final certification release' in readme.lower()))
r.append(ck('launch script executable',bool((ROOT/'run.sh').stat().st_mode & 0o111)))
print(f'FINAL RESULT {sum(r)}/{len(r)}')
raise SystemExit(0 if all(r) else 1)
