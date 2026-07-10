from copy import deepcopy
from pathlib import Path
from backend.core.game import Game, INITIAL_STATE
from backend.core.ai_player import AIPlayerRunner
from backend.core.player_status_model import PLAYER_STATUS_MODEL
ROOT=Path(__file__).resolve().parents[1]

def game():
 g=Game.__new__(Game);g.state=deepcopy(INITIAL_STATE);g._overview_cache_key=None;g._overview_cache=None;return g

def main():
 checks=[]
 def ck(n,x): checks.append((n,bool(x)));print(('PASS' if x else 'FAIL'),n)
 # Reproduce the exact formerly crashing full-diagnostic contract.
 g=game();food=deepcopy(g.state);PLAYER_STATUS_MODEL.migrate(food)['hunger']=70;food.setdefault('economy',{}).setdefault('household',{})['bread_loaf']=1
 ok,_,_=PLAYER_STATUS_MODEL.perform(food,'status:eat:bread')
 ck('full diagnostic player status dependency',ok and PLAYER_STATUS_MODEL.migrate(food)['hunger']<=44)
 src=(ROOT/'backend/core/full_diagnostic.py').read_text();ck('full diagnostic import present','from backend.core.player_status_model import PLAYER_STATUS_MODEL' in src)
 r=AIPlayerRunner(); b=r._state_digest(g.state); g.perform(g.actions()[0]['id']); a=r._state_digest(g.state); d=r._diff(b,a)
 cert,reason=r._certification_evidence('action_contract',g.actions()[0]['id'],g.actions()[0].get('label',''),b,a,d,True)
 ck('domain certification contract',isinstance(cert,bool) and isinstance(reason,str) and bool(reason))
 cov={k:{'status':'untested','attempts':3,'acted':0,'successes':0,'last_gap':'','last_evidence':'','note':v} for k,v in r.COVERAGE_GOALS.items()}
 reason=r._coverage_reason('cooking',cov['cooking']);ck('attempted versus acted explanation','planning attempts' in reason and 'no semantically relevant' in reason)
 cov['cooking'].update(acted=2,last_gap='needs cooking action with ingredient/product/status consequence');reason=r._coverage_reason('cooking',cov['cooking']);ck('uncertified gap explanation','certification contract not met' in reason and 'ingredient/product/status' in reason)
 r._write_live_report(g,cov,[],{g.state.get('location')},set(),{'action':'v204-certification','diff':d});text=r.live_report_path.read_text()
 ck('expository live coverage','planning_attempts=' in text and 'relevant_actions=' in text and 'WHY:' in text and 'CONTRACT:' in text)
 css=(ROOT/'frontend/static/css/game.css').read_text();ck('developer console bounded scrolling','.developer-card .diagnostic-launch' in css and 'max-height:34vh' in css and '.developer-card .developer-content' in css)
 js=(ROOT/'frontend/static/js/game.js').read_text();ck('v204 export filenames','Bellwether_v2.0.4_overnight_AI_soak_report.txt' in js and 'Bellwether_v2.0.4_full_ai_player_diagnostic_report.txt' in js)
 ck('release identity',(ROOT/'VERSION').read_text().strip()=='2.0.4')
 print(f'{sum(x for _,x in checks)}/{len(checks)} PASS')
 raise SystemExit(0 if all(x for _,x in checks) else 1)
if __name__=='__main__':main()
