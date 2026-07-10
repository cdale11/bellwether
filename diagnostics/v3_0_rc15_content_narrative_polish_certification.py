from pathlib import Path
import ast, json
ROOT=Path(__file__).resolve().parents[1]
checks=[]
def check(name, ok, detail=''):
    checks.append((name,bool(ok),detail)); print(('PASS' if ok else 'FAIL'),name,detail)
version=(ROOT/'VERSION').read_text().strip(); check('release_identity',version=='3.0.0-rc15',version)
arc=(ROOT/'backend/core/procedural_arc_model.py').read_text()
check('procedural_help_labels','Offer to help with:' not in arc and 'Help Jonah with the bakery backlog' in arc)
check('concise_arc_titles','Bakery under pressure' in arc and 'The churchyard record discrepancy' in arc)
game=(ROOT/'backend/core/game.py').read_text()
check('natural_greeting_labels','Exchange a Few Words with' not in game and 'Greet {npc' in game)
content=(ROOT/'backend/core/content_model.py').read_text()
check('recipe_specific_outcomes',content.count("cooking_prose")>=2 and 'pan-fry the trout' in content and 'mushrooms darken the stew' in content)
for f in list((ROOT/'backend').rglob('*.py')): ast.parse(f.read_text(encoding='utf-8'))
check('python_parse',True)
for f in (ROOT/'content').rglob('*.json'): json.loads(f.read_text(encoding='utf-8'))
check('content_json',True)
# player-facing source hygiene
bad=[]
for base in ('backend','content','frontend'):
    for f in (ROOT/base).rglob('*'):
        if f.is_file() and f.suffix in {'.py','.json','.js','.html'}:
            t=f.read_text(encoding='utf-8',errors='ignore').lower()
            if 'lorem ipsum' in t: bad.append(str(f))
check('no_placeholder_prose',not bad,','.join(bad))
print(f"SUMMARY {sum(x[1] for x in checks)}/{len(checks)}")
raise SystemExit(0 if all(x[1] for x in checks) else 1)
