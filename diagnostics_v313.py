from copy import deepcopy
from threading import RLock
from pathlib import Path
from backend.core.ai_player import AIPlayerRunner
from backend.core.game import Game

checks=[]
def check(name, ok):
    checks.append((name,bool(ok))); print(('PASS' if ok else 'FAIL'), name)

r=AIPlayerRunner()
class Dummy:
    def __init__(self):
        self.state={'day':1,'minute':480,'location':'ashcroft_cottage','presentation_ledger':{'entries':[{'entry_id':'x1','text':'SOCIAL metadata on its own line.'}]}}
    def time_label(self): return '08:00'

g=Dummy(); seen=set(); findings=r._semantic_findings(g,seen)
check('semantic boilerplate detector', any(x['type']=='player_visible_ai_boilerplate' for x in findings))
check('semantic detector deduplicates seen entries', not r._semantic_findings(g,seen))
coverage={k:{'status':'untested','attempts':0,'acted':0,'successes':0,'deferrals':0,'last_gap':'','last_evidence':'','note':v} for k,v in r.COVERAGE_GOALS.items()}
r._update(days=7,days_completed=1,day_summaries=[{'day':1,'actions':4,'goals':['movement'],'locations':['village_green'],'findings':0}],action_counts={'travel:village_green':2})
text='\n'.join(r._report_lines(g,coverage,[],{'ashcroft_cottage','village_green'},{'travel:village_green'},'TEST'))
check('report executive summary', 'EXECUTIVE SUMMARY' in text and 'DEVELOPER PRIORITIES' in text)
check('report day summaries', 'DAY-BY-DAY CAMPAIGN SUMMARY' in text and 'Day 1' in text)
check('report action diversity', 'ACTION DIVERSITY' in text and 'travel:village_green' in text)
source=Path('backend/core/ai_player.py').read_text()
check('isolated state clone before overnight thread', 'test_game.state=deepcopy(game.state)' in source and 'args=(test_game,test_lock,days)' in source)
html=Path('frontend/templates/index.html').read_text(); js=Path('frontend/static/js/game.js').read_text()
check('web report viewer', 'View Live/Final Report' in html and 'viewOvernightReport' in js and 'overnight-report-text' in html)
check('seven day API contract', 'AI_PLAYER.start_live(game,game_lock,7)' in Path('backend/app.py').read_text())
print(f"{sum(v for _,v in checks)}/{len(checks)} PASS")
raise SystemExit(0 if all(v for _,v in checks) else 1)
