from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
css=(ROOT/'frontend/static/css/game.css').read_text()
js=(ROOT/'frontend/static/js/game.js').read_text()
checks=[]
def check(name, ok):
    checks.append((name,bool(ok))); print(('PASS' if ok else 'FAIL'),name)
check('status panel exists', "if(type==='status')" in js)
check('weatherproofing surfaced', '<b>Weatherproofing</b>' in js)
check('status cards have safer minimum width', '#panel-modal .stat-grid{grid-template-columns:repeat(auto-fit,minmax(180px,1fr))' in css)
check('status card uses label-value grid', 'grid-template-columns:minmax(0,1fr) auto' in css)
check('numeric values do not split vertically', 'white-space:nowrap' in css and '#panel-modal .stat-grid>div>span' in css)
check('narrow phone fallback is one column', '@media(max-width:460px){#panel-modal .stat-grid{grid-template-columns:1fr}' in css)
check('panel blocks horizontal overflow', '#panel-modal .panel-content{min-width:0;overflow-x:hidden}' in css)
check('skills table fixed layout', '#panel-modal .diag-table{table-layout:fixed}' in css)
print(f"RESULT {sum(x for _,x in checks)}/{len(checks)}")
raise SystemExit(0 if all(x for _,x in checks) else 1)
