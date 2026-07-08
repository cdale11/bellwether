#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
checks=[]
def ok(name, cond):
    checks.append((name,bool(cond))); print(('PASS' if cond else 'FAIL'),name)
manifest=json.loads((ROOT/'frontend/static/assets/asset_manifest.json').read_text())
html=(ROOT/'frontend/templates/index.html').read_text()
js=(ROOT/'frontend/static/js/game.js').read_text()
css=(ROOT/'frontend/static/css/game.css').read_text()
ok('asset manifest validates', manifest['version']=='0.3.0-part2-dev' and isinstance(manifest['scenes'],dict))
ok('approved art packaged', (ROOT/'frontend/static/assets/scenes/ashcroft_cottage_garden/approved_visual_reference.png').exists())
ok('scene art stage integrated', 'id="scene-art"' in html and 'scene-atmosphere' in html)
ok('state aware scene resolver present', 'applyVisualState' in js and 'slugifyLocation' in js)
ok('missing art fallback preserved', "stage.classList.remove('has-art')" in js)
ok('semantic warm palette present', '--cream:' in css and 'color-scheme:light' in css)
ok('weather atmosphere treatments present', all(x in css for x in ['light_rain','heavy_rain','storm','snow','mist']))
ok('night treatment present', 'data-daypart="night"' in css)
ok('reduced motion support present', 'prefers-reduced-motion:reduce' in css)
ok('side stories retained in journal', "block('Side Stories',s.quests.side)" in js)
ok('asset bible packaged', (ROOT/'content/visual/ASSET_BIBLE.md').exists())
passed=all(v for _,v in checks)
print(f'Part 2 visual passes: {sum(v for _,v in checks)}/{len(checks)}')
raise SystemExit(0 if passed else 1)
