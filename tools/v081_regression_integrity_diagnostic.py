from pathlib import Path
import json, re

ROOT = Path(__file__).resolve().parents[1]
checks=[]
def check(name, ok):
    checks.append((name,bool(ok)))
    print(('PASS' if ok else 'FAIL'), name)

html=(ROOT/'frontend/templates/index.html').read_text()
js=(ROOT/'frontend/static/js/game.js').read_text()
app=(ROOT/'backend/app.py').read_text()
version=(ROOT/'VERSION').read_text().strip()

check('version lineage is v0.8.1 or later', tuple(map(int,version.split('.'))) >= (0,8,1))
check('developer/settings button exists', 'id="dev-button"' in html and 'Developer / Settings' in html)
check('developer/settings button is not hidden by default', 'id="dev-button" class="dev-only hidden"' not in html)
check('developer console remains packaged', 'id="developer-modal"' in html and 'openDeveloperConsole()' in html)
check('developer console no longer rejects normal button access', "openDeveloperConsole(){if(!devMode())return" not in js)
check('developer status endpoint remains available', '@app.get("/api/developer-status")' in app)
for route in ['/api/state','/api/action','/api/talk','/api/save','/api/load','/api/new-game']:
    check(f'core API route preserved: {route}', route in app)
ids=re.findall(r'id=["\']([^"\']+)', html)
check('no duplicate static HTML ids', len(ids)==len(set(ids)))
for rel in [
    'docs/Bellwether_Canonical_World_and_Story_Bible_v1.txt',
    'docs/Bellwether_Coding_and_Implementation_Philosophy_v1.txt',
    'docs/Bellwether_Design_Constitution.txt',
    'docs/Bellwether_LLM_Role_Authority_and_Constraint_Specification_v1.txt',
]: check(f'authoritative context packaged: {Path(rel).name}', (ROOT/rel).exists())
cat=json.loads((ROOT/'content/investigation/mystery_catalogue.json').read_text())
# tolerate dict/list schema while asserting the v0.8 expansion is not accidentally collapsed
mysteries=cat.get('mysteries',{}) if isinstance(cat,dict) else {}
check('full mystery expansion retained', len(mysteries) >= 7)
check('run.sh executable', bool((ROOT/'run.sh').stat().st_mode & 0o111))
failed=[n for n,ok in checks if not ok]
if failed:
    raise SystemExit(f'v0.8.1 regression integrity diagnostic FAILED: {failed}')
print(f'v0.8.1 regression integrity diagnostic: {len(checks)}/{len(checks)} PASS')
