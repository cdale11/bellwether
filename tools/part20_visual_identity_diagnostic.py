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
ok('asset manifest validates', manifest['version']=='0.3.5' and isinstance(manifest['scenes'],dict))

# v0.3.5 certification: validate the art the manifest actually declares, rather than a stale
# pre-integration reference path that is neither referenced nor part of the accepted package.
def packaged(url):
    return isinstance(url, str) and url.startswith('/static/') and (ROOT/'frontend/static'/url.removeprefix('/static/')).exists()
scene_art = [v.get('default') for v in manifest.get('scenes', {}).values()]
portrait_art = [url for variants in manifest.get('characters', {}).values() for url in variants.values()]
ok('approved art packaged', bool(scene_art) and bool(portrait_art) and all(packaged(u) for u in scene_art + portrait_art))
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
