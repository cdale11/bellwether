from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
css=(ROOT/'frontend/static/css/game.css').read_text()
js=(ROOT/'frontend/static/js/game.js').read_text()
html=(ROOT/'frontend/templates/index.html').read_text()
checks={
'version':(ROOT/'VERSION').read_text().strip()=='1.0.6',
'horror stage dataset':'dataset.horrorStage' in js,
'pressure visual variable':'--horror-pressure' in js and '--horror-pressure' in css,
'weather layers':all(x in html for x in ('rain-layer','snow-layer','mist-layer')),
'daypart treatment':'data-daypart="evening"' in css and 'data-daypart="night"' in css,
'season treatment':'data-season*="winter"' in css and 'data-season*="summer"' in css,
'horror progression':all(x in css for x in ('data-horror-stage="subtle"','data-horror-stage="uneasy"','data-horror-stage="disturbed"','data-horror-stage="severe"')),
'reduced motion':'prefers-reduced-motion:reduce' in css,
'mobile scene first':'@media(max-width:620px)' in css and 'height:62vh' in css,
'no js animation timer':'requestAnimationFrame' not in js,
}
for k,v in checks.items(): print(('PASS' if v else 'FAIL'),k)
print(f"{sum(checks.values())}/{len(checks)} PASS")
raise SystemExit(0 if all(checks.values()) else 1)
