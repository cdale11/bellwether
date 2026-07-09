from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
provider=(ROOT/'backend/ai/provider.py').read_text()
js=(ROOT/'frontend/static/js/game.js').read_text()
html=(ROOT/'frontend/templates/index.html').read_text()
version=(ROOT/'VERSION').read_text().strip()
checks={
 'version': version=='1.0.3',
 'strategic_timeout_env': 'BELLWETHER_STRATEGIC_AI_TIMEOUT","120"' in provider,
 'fast_timeout_env': 'BELLWETHER_BOUNDED_AI_TIMEOUT","75"' in provider,
 'single_bounded_attempt': 'tries_override=1,timeout_override=bounded_timeout' in provider,
 'strategic_roles': 'director in {"town_mind", "procedural_arc", "recurrence_strategy", "horror_strategy"}' in provider,
 'progressive_quick_actions': "const urgent=actions.filter" in js and "const social=actions.filter" in js,
 'generic_tick_filter': "^Another small errand|^Footsteps and wheels|^A delivery has been made" in js,
 'command_hierarchy_copy': 'Immediate choices appear first' in html,
 'portable_save_preserved': '/api/save-file' in (ROOT/'backend/app.py').read_text() and '/api/load-file' in (ROOT/'backend/app.py').read_text(),
 'developer_access_preserved': 'openDeveloperConsole()' in html,
}
for k,v in checks.items(): print(('PASS' if v else 'FAIL'),k)
print(f"{sum(checks.values())}/{len(checks)} checks passed")
raise SystemExit(0 if all(checks.values()) else 1)
