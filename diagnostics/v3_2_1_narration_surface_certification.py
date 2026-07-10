from pathlib import Path
root=Path(__file__).resolve().parents[1]
js=(root/'frontend/static/js/game.js').read_text()
html=(root/'frontend/templates/index.html').read_text()
checks={
'narrator strip exists':'id="narrator-strip"' in html,
'narrator messages partitioned':"narratorMsgs=rawMsgs.filter" in js,
'narrator excluded from dialogue':"rawMsgs.filter(l=>!/^narrator$/i.test" in js,
'conversation exchange priority preserved':"dialogueMsgs=exchangeMsgs.length?exchangeMsgs" in js,
'narrator strip can show':"ns.classList.remove('hidden')" in js,
'narrator strip can hide':"ns.classList.add('hidden')" in js,
}
for k,v in checks.items(): print(('PASS' if v else 'FAIL'),k)
raise SystemExit(0 if all(checks.values()) else 1)
