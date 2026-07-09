#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
checks=[]
def check(name,cond): checks.append((name,bool(cond))); print(('PASS' if cond else 'FAIL'),name)
html=(ROOT/'frontend/templates/index.html').read_text(); js=(ROOT/'frontend/static/js/game.js').read_text(); css=(ROOT/'frontend/static/css/game.css').read_text(); app=(ROOT/'backend/app.py').read_text()
check('old Village Mind player control removed','Village Mind' not in html)
check('developer/settings access and console preserved','id="dev-button"' in html and 'developer-modal' in html and 'openDeveloperConsole()' in html)
check('five shallow action categories',all(x in js for x in ['People','Activities','Explore','Investigate','Travel']))
check('dedicated information panels',all(f"openPanel('{x}')" in html for x in ['journal','map','inventory','relationships','notebook','home']))
check('scene stage and environment line','scene-stage' in html and 'environment-line' in html)
check('responsive mobile breakpoint','@media(max-width:620px)' in css)
check('relationship numbers hidden from player rendering','Familiarity ${' not in js and 'relationshipDescription' in js)
check('expanded developer endpoint','/api/developer-status' in app and all(x in app for x in ['dynamic_events','anomaly_history','investigation','economy','recurrence']))
check('frontend remains API driven',"fetch('/api/state')" in js and "fetch('/api/action'" in js)
check('part version marked', (ROOT/'VERSION').read_text().strip().startswith(('0.3.0-part','0.3.5','0.4.','0.5.','0.6.','0.7.','0.8.','0.9.','1.0')))
print(f"Part 19 / v0.3 Part 1 passes: {sum(x[1] for x in checks)}/{len(checks)}")
raise SystemExit(0 if all(x[1] for x in checks) else 1)
