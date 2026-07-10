from pathlib import Path
import re
checks=[]
def check(n,c): checks.append((n,bool(c))); print(('PASS' if c else 'FAIL'),n)
prov=Path('backend/ai/provider.py').read_text()
ai=Path('backend/core/ai_player.py').read_text()
app=Path('backend/app.py').read_text()
html=Path('frontend/templates/index.html').read_text()
js=Path('frontend/static/js/game.js').read_text()
check('4B preferred before 2B', prov.index('qwen3.5:4b') < prov.index('qwen3.5:2b'))
check('2B fallback present', 'qwen3.5:2b' in prov)
check('single discovered model default', 'self.deep_model = deep_override or self.fast_model' in prov)
check('isolated overnight mode preserved', 'mutate_live=False' in app and 'isolated_overnight_qa' in ai)
check('live village mode endpoint', '/api/ai-player/start-live' in app and 'mutate_live=True' in app)
check('live mode authoritative object', 'test_game=game;test_lock=game_lock' in ai)
check('UI exposes both modes', 'Run 7-Day Overnight AI Playtest' in html and 'Let AI Play the Village' in html)
check('live state warning', 'changes the live game state' in js)
print(f'{sum(x[1] for x in checks)}/{len(checks)}')
raise SystemExit(0 if all(x[1] for x in checks) else 1)
