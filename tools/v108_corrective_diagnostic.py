from pathlib import Path
root=Path(__file__).resolve().parents[1]
checks=[]
def c(name,ok): checks.append((name,bool(ok)))
js=(root/'frontend/static/js/game.js').read_text()
html=(root/'frontend/templates/index.html').read_text()
rt=(root/'backend/ai/async_runtime.py').read_text()
game=(root/'backend/core/game.py').read_text()
c('version',(root/'VERSION').read_text().strip()=='1.0.8')
c('narrator_strip','narrator-strip' in html and "narr=msgs.filter" in js)
c('realtime_pacing','setInterval(async()=>' in js and '/api/pacing-status' in js)
c('copy_fallback','copyTextRobust' in js and 'execCommand' in js)
c('full_diagnostic','Run Full Game Diagnosis' in html and '/api/diagnostic/full/start' in js)
c('scheduler_metrics','job_merged_before_inference' in rt and 'job_request_deferred_running' in rt and 'wasted_after_inference' in rt)
c('procedural_visibility','procedural_opportunities' in game)
c('fictional_currency','¤' in js)
for n,ok in checks: print(('PASS' if ok else 'FAIL'),n)
print(f'{sum(ok for _,ok in checks)}/{len(checks)} PASS')
raise SystemExit(0 if all(ok for _,ok in checks) else 1)
