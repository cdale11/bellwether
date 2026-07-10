from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
html=(ROOT/'frontend/templates/index.html').read_text()
js=(ROOT/'frontend/static/js/game.js').read_text()
css=(ROOT/'frontend/static/css/game.css').read_text()
checks={
'location prose not duplicated in left rail':'id="environment-line"' not in html and 'id="environment-line-overlay"' in html,
'compact clickable people':'compact-person' in js and 'openNpcPanel' in js,
'npc focus modal':'id="npc-modal"' in html and 'npc-focus' in css,
'action tray bounded overlay':'position:fixed' in css[css.find('/* v1.0.5'):],
'narration hierarchy':'narration-line' in js and '.dialogue .narration-line' in css,
'diagnostic health strip':'health-strip' in js and '.health-strip' in css,
'living world dashboard':'renderSimulationDiag' in js,
'ai runtime dashboard':'renderAiDiag' in js,
'raw json preserved':"['raw','Raw State']" in js and 'Copy JSON' in js,
'editable shortcut safety':'isContentEditable' in js,
'mobile npc layout':'@media(max-width:620px)' in css and '.npc-focus{grid-template-columns:90px 1fr}' in css,
}
for k,v in checks.items(): print(('PASS' if v else 'FAIL'),k)
print(f"{sum(checks.values())}/{len(checks)} PASS")
raise SystemExit(0 if all(checks.values()) else 1)
