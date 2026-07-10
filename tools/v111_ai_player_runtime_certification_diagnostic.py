from pathlib import Path
import sys,time
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from backend.core.game import Game
from backend.core.ai_player import AIPlayerRunner,safe_actions
from backend.ai.async_runtime import AsyncAIRuntime
from backend.ai.provider import provider
checks=[]
def c(n,ok,d=''): checks.append((n,bool(ok),d))
c('version',(ROOT/'VERSION').read_text().strip()=='1.0.11')
g=Game(); acts=safe_actions(g); c('safe public actions',bool(acts) and all(not a['id'].startswith(('story:','ending:','horror:','recurrence:')) for a in acts))
r=AIPlayerRunner(); c('stop state initial',r.snapshot()['stop_state']=='stopped'); r.stop(); c('idle stop safe',r.snapshot()['stop_state']=='stopped')
rt=AsyncAIRuntime(); rt.submit('cert','ecology_review',1,('x',),lambda:{'ok':True},domain='ecology');
for _ in range(100):
 st=rt.status()
 if st['completed_waiting']:break
 time.sleep(.01)
st=rt.status(); c('queue telemetry','oldest_wait_s' in st and 'inference_accounting' in st); c('accounting started',st['inference_accounting']['calls_started']>=1)
c('provider telemetry',set(provider.telemetry())>={'busy','foreground_waiters','active'})
js=(ROOT/'frontend/static/js/game.js').read_text(); c('currency component','currencyMarkup' in js and 'currency-mark' in js); c('report version','v1.0.11_full_ai_player' in js)
fd=(ROOT/'backend/core/full_diagnostic.py').read_text(); c('coverage driven diagnostic','coverage-driven' in fd.lower() and 'coverage_save_reload' not in fd and 'coverage={k:False' in fd); c('seven day horizon','start_day+7' in fd); c('stop discard semantics','discarded completed choice' in (ROOT/'backend/core/ai_player.py').read_text())
for n,ok,d in checks: print(('PASS' if ok else 'FAIL'),n,d)
print(f'{sum(x[1] for x in checks)}/{len(checks)} PASS');raise SystemExit(0 if all(x[1] for x in checks) else 1)
