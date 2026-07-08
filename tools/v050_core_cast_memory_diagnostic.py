#!/usr/bin/env python3
import json, tempfile
from pathlib import Path
from copy import deepcopy
from backend.core.game import Game, INITIAL_STATE
from backend.core.npc_model import NPC_MODEL
from backend.core.social_model import SOCIAL_MODEL
from backend.core.memory_model import MEMORY_MODEL
from backend.ai.provider import provider
checks=[]
def check(name,ok,detail=''):
    checks.append((name,bool(ok),detail)); print(('PASS' if ok else 'FAIL'),name,detail)
ids=set(NPC_MODEL.npcs)
check('six authored core NPCs',len(ids)==6,str(sorted(ids)))
check('all core NPCs in initial runtime',ids<=set(INITIAL_STATE['npcs']))
check('complete pairwise social web',len(SOCIAL_MODEL.edges)==15,str(len(SOCIAL_MODEL.edges)))
check('relationships cover core cast',ids<=set(INITIAL_STATE['relationships']))
check('knowledge runtime covers core cast',ids<=set(INITIAL_STATE['npc_knowledge']['npcs']))
g=Game(); g.state=deepcopy(INITIAL_STATE); g.migrate_state()
eid=MEMORY_MODEL.record(g.state,'conversation','Test conversation',actors=['asha'],witnesses=['asha'],location='village_shop',importance=3)
ctx=MEMORY_MODEL.context(g.state,'asha')
check('structured event stable id',eid.startswith('evt_') and any(e['id']==eid for e in g.state['memory_system']['events']))
check('witness memory reference',any(e['id']==eid for e in ctx['events']))
old=deepcopy(INITIAL_STATE)
for nid in ('asha','tom','ruth'):
    old['npcs'].pop(nid,None); old['relationships'].pop(nid,None); old['social_memory'].pop(nid,None); old['conversation_sessions'].pop(nid,None)
old.pop('memory_system',None)
g.state=old; g.migrate_state()
check('old-save core cast migration',ids<=set(g.state['npcs']))
check('old-save memory migration','memory_system' in g.state and ids<=set(g.state['memory_system']['npc_memory']))
check('fast model default configured',bool(provider.fast_model),provider.fast_model)
check('deep model configured',bool(provider.deep_model),provider.deep_model)
check('strategic routing differs by task',provider.model_for_task('town_mind')==provider.deep_model and provider.model_for_task('npc')==provider.fast_model)
failed=[n for n,ok,d in checks if not ok]
print(f"RESULT {len(checks)-len(failed)}/{len(checks)}")
raise SystemExit(1 if failed else 0)
