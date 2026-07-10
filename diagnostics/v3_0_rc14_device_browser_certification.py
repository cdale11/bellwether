from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
js=(ROOT/'frontend/static/js/game.js').read_text()
css=(ROOT/'frontend/static/css/game.css').read_text()
html=(ROOT/'frontend/templates/index.html').read_text()
checks=[]
def check(name,ok):
    checks.append((name,bool(ok))); print(('PASS' if ok else 'FAIL'),name)
check('modal focus trap','trapModalFocus' in js and "e.key!=='Tab'" in js)
check('focus restoration','lastFocusedElement.focus()' in js)
check('modal accessible open helper','openModalAccessible' in js and "#talk-input" in js)
check('coarse pointer targets','@media(pointer:coarse)' in css and 'min-height:48px' in css)
check('safe area support','safe-area-inset-bottom' in css and 'safe-area-inset-left' in css)
check('dynamic viewport support','100dvh' in css)
check('landscape short viewport','orientation:landscape' in css and 'max-height:560px' in css)
check('narrow viewport fallback','@media(max-width:460px)' in css)
check('keyboard focus visible','focus-visible' in css)
check('semantic navigation labels','aria-label="Action categories"' in html and 'aria-label="Game information"' in html)
print(f"RESULT {sum(x[1] for x in checks)}/{len(checks)}")
raise SystemExit(0 if all(x[1] for x in checks) else 1)
