#!/usr/bin/env python3
from copy import deepcopy
import os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));os.environ["BELLWETHER_AI"]="0"
from backend.core.game import Game, INITIAL_STATE
from backend.core.knowledge_model import KNOWLEDGE_MODEL

def check(name,cond):
 print(('PASS ' if cond else 'FAIL ')+name); return bool(cond)

g=Game(); g.state=deepcopy(INITIAL_STATE); g.migrate_state(); results=[]
results.append(check('knowledge schema validates',KNOWLEDGE_MODEL.validate()))
results.append(check('authored initial knowledge present',bool(g.npc_knowledge_context('jonah'))))
results.append(check('unknown facts rejected',not g.learn_npc_fact('jonah','invented_llm_fact')))
results.append(check('catalogue fact learning works',g.learn_npc_fact('mara','bakery_morning_rhythm',.8)))
# Force fresh co-location and enough trust for transfer.
g.state['npcs']['jonah'].update(location='bakery',visible=True); g.state['npcs']['mara'].update(location='bakery',visible=True)
eid='jonah|mara'; g.state['npc_social_web'][eid]['state']['trust']=50
g.update_npc_social_web(); g.propagate_npc_knowledge()
results.append(check('encounter propagates bounded knowledge','bakery_morning_rhythm' in g.state['npc_knowledge']['npcs']['jonah']['beliefs'] or bool(g.state['npc_knowledge']['propagation_log'])))
results.append(check('propagation log records provenance',all({'source','target','fact_id','variant'}<=set(x) for x in g.state['npc_knowledge']['propagation_log'])))
results.append(check('shared topic hook integrated',bool(g.state['npc_social_web'][eid]['shared_topics'])))
results.append(check('knowledge context is text-resolved',all('text' in x and 'confidence' in x for x in g.npc_knowledge_context('mara'))))
# Low trust sensitive fact is withheld.
g2=Game(); g2.state=deepcopy(INITIAL_STATE); g2.migrate_state(); g2.learn_npc_fact('mrs_ellis','railway_halt_avoided',.9); eid2='jonah|mrs_ellis'; g2.state['npc_social_web'][eid2]['state']['trust']=-50
g2.state['npcs']['jonah'].update(location='village_road',visible=True); g2.state['npcs']['mrs_ellis'].update(location='village_road',visible=True); g2.update_npc_social_web(); g2.propagate_npc_knowledge()
results.append(check('sensitive knowledge respects trust gate','railway_halt_avoided' not in g2.state['npc_knowledge']['npcs']['jonah']['beliefs']))
# Migration
old=deepcopy(INITIAL_STATE); old.pop('npc_knowledge',None); g3=Game(); g3.state=old; g3.migrate_state()
results.append(check('old-save knowledge migration','npc_knowledge' in g3.state and 'npcs' in g3.state['npc_knowledge']))
# Canon isolation
before=deepcopy(KNOWLEDGE_MODEL.facts); g.learn_npc_fact('jonah','green_workday_custom'); results.append(check('runtime cannot mutate authored fact canon',before==KNOWLEDGE_MODEL.facts))
print(f'Part 10 passes: {sum(results)}/{len(results)}'); raise SystemExit(0 if all(results) else 1)
