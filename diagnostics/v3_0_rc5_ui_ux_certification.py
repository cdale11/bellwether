from pathlib import Path
R=Path(__file__).resolve().parents[1]
js=(R/'frontend/static/js/game.js').read_text()
css=(R/'frontend/static/css/game.css').read_text()
html=(R/'frontend/templates/index.html').read_text()
checks={
'loading detail surface':'loading-detail' in html and 'Local AI can take a little while' in js,
'action HTTP error handling':'Action could not be completed' in js and 'if(!r.ok)' in js,
'conversation failure handling':'Conversation failed' in js,
'coarse pointer targets':'@media(pointer:coarse)' in css and 'min-height:48px' in css,
'keyboard focus visibility':'focus-visible' in css,
'reduced motion weather':'prefers-reduced-motion:reduce' in css and 'weather-sweep' in css,
'horror atmosphere staged':'atmosphere-uneasy' in js and 'atmosphere-acute' in js,
'weather atmosphere staged':'data-weather="rain"' in css and 'data-weather="storm"' in css,
'mobile developer tabs scroll':'developer-tabs{flex-wrap:nowrap;overflow-x:auto' in css,
'developer settings preserved':'openDeveloperConsole()' in html,
}
for k,v in checks.items(): print(('PASS' if v else 'FAIL'),k)
print(f"RC5 UI/UX certification: {sum(checks.values())}/{len(checks)} PASS")
raise SystemExit(0 if all(checks.values()) else 1)
