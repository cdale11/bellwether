from copy import deepcopy
from backend.core.game import Game
from backend.core.npc_project_model import NPC_PROJECT_MODEL

g=Game();s=g.state;s['diagnostic_mode']=True
rt=NPC_PROJECT_MODEL.migrate(s)
checks=[]
def ck(n,x):checks.append((n,bool(x)))
ck('separate_project_state',all(k not in rt['projects'] for k in ('town_mind','chorus')))
ctx=NPC_PROJECT_MODEL.reasoning_context(s,'mara');ck('legal_attempts_bounded',len(ctx['legal_attempts'])==4)
r={'belief':'Weather alone may not explain the flowering near the cottage.','question':'Does the same pattern occur away from Ashcroft ground?','next_attempt':'inspect_own_garden','reason':'A comparison can separate location from weather.','disclosure':'selective'}
ck('llm_reasoning_applies',NPC_PROJECT_MODEL.apply_reasoning(s,'mara',r,'test'))
ck('llm_cannot_mutate_observation',not NPC_PROJECT_MODEL.apply_reasoning(s,'mara',{'belief':'x','question':'x','next_attempt':'invent_bones'},'test'))
s['day']=2;ev=NPC_PROJECT_MODEL.advance_day(s);ck('engine_executes_legal_attempt',len(ev)==1 and ev[0]['attempt']=='inspect_own_garden')
ck('engine_supplies_observation','ordinary variation' in ev[0]['observation'])
r2={'belief':'Weather alone is unlikely; location may matter.','question':'Is the irregularity strongest near the cottage boundary?','next_attempt':'inspect_ashcroft_edge','reason':'The comparison weakened the weather-only theory.','disclosure':'uncertain'}
ck('belief_revision_applies',NPC_PROJECT_MODEL.apply_reasoning(s,'mara',r2,'test'))
ck('revision_history_preserved',len(rt['projects']['mara']['revision_history'])==1)
ck('disclosure_is_non_authoritative',rt['projects']['mara']['disclosure']=='uncertain' and 'flags' in s)
for n,v in checks:print(('PASS' if v else 'FAIL'),n)
print(f"NPC EPISTEMIC PROJECTS: {sum(v for _,v in checks)}/{len(checks)}")
raise SystemExit(0 if all(v for _,v in checks) else 1)
