from pathlib import Path
import json, tempfile
from backend.core.game import Game, WORLD
root=Path(__file__).resolve().parents[1]
checks=[]
def ok(name, cond): checks.append((name,bool(cond))); print(('PASS' if cond else 'FAIL'),name)

g=Game()
ok('version is 1.0', (root/'VERSION').read_text().strip()=='1.0')
ok('developer control preserved', 'id="dev-button"' in (root/'frontend/templates/index.html').read_text())
ok('fresh reset endpoint preserved', '/api/reset-fresh' in (root/'backend/app.py').read_text())
ok('browser reload semantics documented', 'browser reload reconnects' in (root/'README.md').read_text().lower())
ok('generic village rhythm fallback removed', 'The village keeps its own quiet rhythm.' not in (root/'frontend/static/js/game.js').read_text())
ok('location descriptions complete', all(v.get('description','').strip() for v in WORLD.values()))
# consecutive prose dedupe
before=len(g.state['history']); g.add('Test','same'); g.add('Test','same'); ok('consecutive message dedupe',len(g.state['history'])==before+1)
# world event dedupe
g.record_world_event('same event','test'); g.record_world_event('same event','test'); ok('consecutive world event dedupe',sum(x.get('text')=='same event' for x in g.state['world_events'])==1)
# fresh reset is not recurrence
old=g.state.get('recurrence',{}).get('run_index',1); out=g.reset_fresh(); ok('fresh reset returns playable view',out.get('ok') and out['view']['actions']); ok('fresh reset has no recurrence increment',g.state.get('recurrence',{}).get('run_index',1)==1)
# memory bounds migration
g.state['encounters']=[{'key':str(i)} for i in range(100)]; g.state['ai_events']=[{'x':i} for i in range(200)]; g.state['social_memory']['jonah']=[str(i) for i in range(100)]; g.migrate_state(); ok('encounter history bounded',len(g.state['encounters'])<=30); ok('ai event history bounded',len(g.state['ai_events'])<=100); ok('social memory bounded',len(g.state['social_memory']['jonah'])<=40)
# story/endings/postgame models still public
v=g.view()['state']; ok('story overview preserved','authored_story_overview' in v); ok('ending overview preserved','ending_families_overview' in v); ok('postgame overview preserved','postgame_overview' in v)
failed=[n for n,c in checks if not c]
print(f'{len(checks)-len(failed)}/{len(checks)} PASS')
raise SystemExit(1 if failed else 0)
