from copy import deepcopy
from backend.core.game import Game
from backend.core.presentation_ledger_model import PRESENTATION_LEDGER_MODEL
from backend.core.procedural_arc_model import PROCEDURAL_ARC_MODEL

g=Game(); checks=[]
def ck(n,v): checks.append((n,bool(v))); print(('PASS' if v else 'FAIL'),n)
base=len(PRESENTATION_LEDGER_MODEL.migrate(g.state)['entries']);g.add('Narrator','Backlog certification line.')
rows=PRESENTATION_LEDGER_MODEL.migrate(g.state)['entries'];ck('presentation append',len(rows)==base+1 and rows[-1]['text']=='Backlog certification line.')
ck('presentation context',all(k in rows[-1] for k in ('day','minute','location','speaker','run_id')))
# history remains bounded independently while backlog retains all committed text
for i in range(130):g.add('Test',f'unique line {i}')
ck('backlog outlives rolling scene history',len(g.state['history'])==120 and len(rows)>120)
# procedural lifecycle: start -> offer -> follow-up visibility -> final resolution action
s=g.state;s['location']='bakery';arc=PROCEDURAL_ARC_MODEL.start(s,'bakery_workload','test');PROCEDURAL_ARC_MODEL.apply_stage(s,arc,next(t for t in __import__('backend.core.procedural_arc_model',fromlist=['ARC_TEMPLATES']).ARC_TEMPLATES if t['id']=='bakery_workload'),next(t for t in __import__('backend.core.procedural_arc_model',fromlist=['ARC_TEMPLATES']).ARC_TEMPLATES if t['id']=='bakery_workload')['stages'][0],__import__('backend.core.game',fromlist=['MEMORY_MODEL']).MEMORY_MODEL,__import__('backend.core.game',fromlist=['COGNITION_MODEL']).COGNITION_MODEL)
acts=dict(PROCEDURAL_ARC_MODEL.available_player_actions(s));help_id=next((k for k in acts if k.startswith('arc:help:')),None);ck('procedural offer reachable',bool(help_id))
if help_id: PROCEDURAL_ARC_MODEL.involve_player(s,arc['id'],__import__('backend.core.game',fromlist=['MEMORY_MODEL']).MEMORY_MODEL,__import__('backend.core.game',fromlist=['COGNITION_MODEL']).COGNITION_MODEL)
acts=dict(PROCEDURAL_ARC_MODEL.available_player_actions(s));ck('procedural follow-up reachable',any(k.startswith('arc:followup:') for k in acts))
# move to penultimate stage and ensure explicit completion action
arc['stage_index']=1;acts=dict(PROCEDURAL_ARC_MODEL.available_player_actions(s));ck('procedural completion action reachable',any(k.startswith('arc:resolve:') for k in acts))
print(f'{sum(v for _,v in checks)}/{len(checks)} PASS')
raise SystemExit(0 if all(v for _,v in checks) else 1)
