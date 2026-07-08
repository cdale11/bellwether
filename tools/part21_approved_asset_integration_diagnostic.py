from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/'frontend/static/assets/asset_manifest.json').read_text())
checks=[]
def check(name, ok):
 print(('PASS ' if ok else 'FAIL ')+name); checks.append(bool(ok))
for key in ('bus_stop','ashcroft_cottage'):
 e=manifest['scenes'].get(key,{}); p=ROOT/'frontend'/e.get('default','').lstrip('/')
 # URL begins static/... but root path is frontend/static/...
 p=ROOT/'frontend'/e.get('default','').lstrip('/')
 check(f'{key} scene manifest and file', bool(e) and p.exists())
for key in ('mara','jonah'):
 e=manifest['characters'].get(key,{}); p=ROOT/'frontend'/e.get('neutral','').lstrip('/')
 check(f'{key} portrait manifest and file', bool(e) and p.exists())
js=(ROOT/'frontend/static/js/game.js').read_text()
check('people here portrait resolver', 'npc-portrait' in js and 'assetManifest.characters' in js)
check('dynamic npc copy remains HTML driven', 'npc-presence-copy' in js and '${escapeHtml(n.name)}' in js and '${escapeHtml(n.activity)}' in js)
print(f'Approved asset integration passes: {sum(checks)}/{len(checks)}')
raise SystemExit(0 if all(checks) else 1)
