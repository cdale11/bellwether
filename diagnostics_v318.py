from pathlib import Path
import ast
root=Path(__file__).parent
src=(root/'backend/core/ai_player.py').read_text()
checks={
'version':(root/'VERSION').read_text().strip()=='3.18.0',
'observer_sample':'_village_observer_sample' in src,
'observer_findings':'_village_observer_findings' in src,
'state_growth':'observer_state_growth' in src,
'runaway_detection':'observer_runaway_' in src,
'report_surface':'VILLAGE OBSERVER / SOAK ANALYSIS' in src,
'bounded_samples':'obs=obs[-360:]' in src,
'syntax':True,
}
try: ast.parse(src)
except SyntaxError: checks['syntax']=False
for k,v in checks.items(): print(('PASS' if v else 'FAIL'),k)
raise SystemExit(0 if all(checks.values()) else 1)
