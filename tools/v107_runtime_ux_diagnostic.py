from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
js=(ROOT/'frontend/static/js/game.js').read_text()
css=(ROOT/'frontend/static/css/game.css').read_text()
checks={
 'version':(ROOT/'VERSION').read_text().strip()=='1.0.7',
 'pacing dismissal':"setTimeout(()=>banner.classList.add('hidden'),1400)" in js,
 'bounded fallback copy':'The Village Moves On' in js,
 'events renderer':'function renderEventsDiag' in js,
 'npc renderer':'function renderNpcDiag' in js,
 'investigation renderer':'function renderInvestigationDiag' in js,
 'human numeric formatting':'function humanNumber' in js,
 'raw state preserved':'Copy JSON' in js,
 'contrast correction':'v1.0.7 — Developer diagnostics readability' in css,
 'active diagnostic tab':'.developer-tabs button.active' in css,
}
for name,ok in checks.items(): print(f"{'PASS' if ok else 'FAIL'}  {name}")
failed=[k for k,v in checks.items() if not v]
print(f"\n{len(checks)-len(failed)}/{len(checks)} checks passed")
raise SystemExit(1 if failed else 0)
