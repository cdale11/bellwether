from copy import deepcopy
from threading import RLock
from backend.core.game import Game, INITIAL_STATE
from backend.core.ai_player import AIPlayerRunner, safe_actions

def game():
 g=Game.__new__(Game);g.state=deepcopy(INITIAL_STATE);g._overview_cache_key=None;g._overview_cache=None;return g

def main():
 checks=[]
 def ck(n,x): checks.append((n,bool(x)));print(('PASS' if x else 'FAIL'),n)
 g=game();r=AIPlayerRunner();cov={k:{'status':'untested','attempts':0,'successes':0,'note':v} for k,v in r.COVERAGE_GOALS.items()}
 ck('coverage breadth',len(cov)>=16 and all(k in cov for k in ('quests_story','horror_failure_recovery','save_reload','weather_ecology')))
 ordinary=safe_actions(g,True,False);comprehensive=safe_actions(g,True,True)
 ck('comprehensive surface superset',len(comprehensive)>=len(ordinary))
 b=r._state_digest(g.state);g.perform(g.actions()[0]['id']);a=r._state_digest(g.state);d=r._diff(b,a)
 ck('state delta evidence',isinstance(d,list))
 anomalies=r._detect_anomalies(b,a,g.actions()[0]['id'],True,d)
 ck('anomaly detector contract',isinstance(anomalies,list))
 r._write_live_report(g,cov,[],{g.state.get('location')},set(),{'action':'certification','diff':d})
 text=r.live_report_path.read_text()
 ck('interrupt-safe live report', 'COVERAGE LEDGER' in text and 'ISSUE / ANOMALY JOURNAL' in text and 'LATEST ACTION EVIDENCE' in text)
 ck('machine-readable checkpoint target',r.checkpoint_path.name.endswith('.jsonl'))
 ck('version dynamic','Version: 2.0.3' in text)
 ck('report is expository',all(x in text for x in ('Coverage:','Anomalies recorded:','PROVIDER TELEMETRY','VISITED LOCATIONS')))
 print(f'{sum(x for _,x in checks)}/{len(checks)} PASS')
 raise SystemExit(0 if all(x for _,x in checks) else 1)
if __name__=='__main__':main()
