#!/usr/bin/env python3
from copy import deepcopy
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.core.game import Game, INITIAL_STATE
from backend.core.procedural_arc_model import PROCEDURAL_ARC_MODEL, ARC_TEMPLATES
from backend.core.memory_model import MEMORY_MODEL
from backend.core.cognition_model import COGNITION_MODEL

def check(name,cond): print(("PASS" if cond else "FAIL")+" | "+name); return bool(cond)
out=[]; g=Game(); s=g.state; root=PROCEDURAL_ARC_MODEL.migrate(s)
out.append(check('arc substrate exists',set(['active','history','proposal_count','accepted_count','rejected_count'])<=set(root)))
out.append(check('legal bounded candidate catalogue',len(ARC_TEMPLATES)>=5 and all(t['stages'] for t in ARC_TEMPLATES)))
out.append(check('illegal template rejected',PROCEDURAL_ARC_MODEL.start(s,'invented_arc') is None))
row=PROCEDURAL_ARC_MODEL.start(s,ARC_TEMPLATES[0]['id'],'test')
out.append(check('legal arc starts persistently',bool(row) and row in root['active']))
due=PROCEDURAL_ARC_MODEL.due_stages(s)
out.append(check('first stage due from legal template',bool(due) and due[0][2]['id']==ARC_TEMPLATES[0]['stages'][0]['id']))
s['location']=row['location']; acts=PROCEDURAL_ARC_MODEL.available_player_actions(s)
out.append(check('active arc exposes bounded local player involvement',bool(acts) and acts[0][0].startswith('arc:help:')))
peid=PROCEDURAL_ARC_MODEL.involve_player(s,row['id'],MEMORY_MODEL,COGNITION_MODEL)
out.append(check('player involvement becomes structured witnessed memory',bool(peid) and row.get('player_involved') is True))
arc,t,stage=due[0]; eid=PROCEDURAL_ARC_MODEL.apply_stage(s,arc,t,stage,MEMORY_MODEL,COGNITION_MODEL)
out.append(check('stage creates structured memory event',bool(eid) and any(e['id']==eid and 'procedural_arc' in e['tags'] for e in s['memory_system']['events'])))
out.append(check('stage creates bounded NPC concern',bool(s['npc_cognition']['npcs']['asha']['concerns'])))
# Advance calendar directly to test causal progression without AI/runtime time cost.
s['day']=10
while row in root['active']:
    due=PROCEDURAL_ARC_MODEL.due_stages(s)
    if not due: break
    for args in due: PROCEDURAL_ARC_MODEL.apply_stage(s,*args,MEMORY_MODEL,COGNITION_MODEL)
out.append(check('multi-stage arc resolves into history',row not in root['active'] and any(h['id']==row['id'] for h in root['history'])))
# Migration
old=deepcopy(INITIAL_STATE); old.pop('procedural_arcs',None); g2=Game(); g2.state=old; g2.migrate_state()
out.append(check('old save migration','procedural_arcs' in g2.state))
# Arc system must not mutate objective truth merely by starting.
g3=Game(); before=(deepcopy(g3.state['flags']),deepcopy(g3.state['weather']),g3.state['money'])
PROCEDURAL_ARC_MODEL.start(g3.state,ARC_TEMPLATES[1]['id'],'test')
out.append(check('arc proposal cannot mutate objective truth',(g3.state['flags'],g3.state['weather'],g3.state['money'])==before))
# Compact context must stay bounded.
ctx=PROCEDURAL_ARC_MODEL.compact_context(s)
out.append(check('compact strategic context',len(str(ctx))<5000 and len(ctx.get('recent_world_events',[]))<=3))
print(f"RESULT {sum(out)}/{len(out)}"); raise SystemExit(0 if all(out) else 1)
