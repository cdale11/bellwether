"""Tiered QA runner for Bellwether RC6.
Fast smoke and targeted regression tiers run independently of the authoritative game.
Long Village Play remains a separate milestone soak.
"""
from pathlib import Path
from threading import RLock, Thread
import subprocess, sys, time, json, zipfile
ROOT=Path(__file__).resolve().parents[2]
DIAG=ROOT/'diagnostics'

SMOKE=[
 'diagnostics/v3_0_rc5_ui_ux_certification.py',
 'diagnostics/diagnostic_v3_rc2_content_density.py',
 'diagnostics/v3_0_rc4_playstyle_strategy_certification.py',
]
TARGETED=[
 'diagnostics/v2_3_0_transport_certification.py',
 'diagnostics/v2_4_0_npc_lives_certification.py',
 'diagnostics/v250_relationship_family_certification.py',
 'diagnostics/v2_6_0_town_consciousness_certification.py',
 'diagnostics/v2_9_0_narrative_certification.py',
 'diagnostics/v2_10_0_story_consciousness_certification.py',
 'diagnostics/v2_11_0_systemic_horror_integration_certification.py',
 'diagnostics/v3_0_rc3_dialogue_expression_certification.py',
]
class QARunner:
 def __init__(self):
  self.lock=RLock(); self.status={'running':False,'tier':None,'progress':0,'phase':'Idle','results':[],'report':'No QA tier has run yet.'}
 def snapshot(self):
  with self.lock:return json.loads(json.dumps(self.status))
 def start(self,tier):
  with self.lock:
   if self.status['running']:return False
   suite=SMOKE if tier=='smoke' else TARGETED if tier=='targeted' else None
   if suite is None:return False
   self.status={'running':True,'tier':tier,'progress':0,'phase':'Preparing','results':[],'report':''}
  Thread(target=self._run,args=(tier,suite),daemon=True,name=f'bellwether-qa-{tier}').start();return True
 def _run(self,tier,suite):
  rows=[]; started=time.time()
  for i,rel in enumerate(suite):
   path=ROOT/rel
   with self.lock:self.status['phase']=f'Running {path.name}';self.status['progress']=round(100*i/max(1,len(suite)))
   if not path.exists(): rows.append({'test':rel,'ok':False,'code':127,'tail':'missing diagnostic'});continue
   p=subprocess.run([sys.executable,str(path)],cwd=ROOT,text=True,capture_output=True,timeout=180,env={**__import__('os').environ,'PYTHONPATH':str(ROOT)})
   text=(p.stdout+'\n'+p.stderr).strip(); rows.append({'test':rel,'ok':p.returncode==0,'code':p.returncode,'tail':'\n'.join(text.splitlines()[-12:])})
   with self.lock:self.status['results']=rows[:];self.status['progress']=round(100*(i+1)/len(suite))
  passed=sum(r['ok'] for r in rows); version=(ROOT/'VERSION').read_text().strip(); elapsed=time.time()-started
  lines=[f'BELLWETHER {tier.upper()} QA',f'Version: {version}',f'Result: {passed}/{len(rows)} diagnostics passed',f'Elapsed: {elapsed:.1f}s','']
  for r in rows:lines += [f"{'PASS' if r['ok'] else 'FAIL'} | {r['test']}",r['tail'],'']
  report='\n'.join(lines); DIAG.mkdir(exist_ok=True);(DIAG/f'latest_{tier}_qa.txt').write_text(report,encoding='utf-8')
  with self.lock:self.status.update({'running':False,'progress':100,'phase':'Complete','results':rows,'report':report})
 def bundle(self):
  DIAG.mkdir(exist_ok=True); out=DIAG/'Bellwether_QA_Bundle.zip'
  with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
   for name in ['VERSION','README.md']:
    p=ROOT/name
    if p.exists():z.write(p,name)
   for p in DIAG.glob('latest_*'):
    if p.is_file():z.write(p,f'diagnostics/{p.name}')
   for p in [DIAG/'diagnostic_ai_player_report.txt',DIAG/'diagnostic_ai_player_live_report.txt',DIAG/'diagnostic_ai_player_live.jsonl']:
    if p.exists():z.write(p,f'diagnostics/{p.name}')
  return out
QA_RUNNER=QARunner()
