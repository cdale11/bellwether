#!/usr/bin/env python3
from copy import deepcopy
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.core.game import Game, INITIAL_STATE
from backend.core.cognition_model import COGNITION_MODEL
from backend.core.memory_model import MEMORY_MODEL

def check(name,cond):
    print(("PASS" if cond else "FAIL")+" | "+name); return bool(cond)

g=Game(); s=g.state; out=[]
root=COGNITION_MODEL.migrate(s,list(s['npcs']))
out.append(check('cognition state exists for full core cast',set(root['npcs'])==set(s['npcs'])))
out.append(check('belief types bounded',not COGNITION_MODEL.add_belief(s,'jonah','canon_magic','x')))
out.append(check('subjective belief accepted',COGNITION_MODEL.add_belief(s,'jonah','suspicion','The newcomer may be avoiding the green.',.45,'observation','test')))
out.append(check('belief provenance retained',COGNITION_MODEL.context(s,'jonah')['beliefs'][0]['source_type']=='observation'))
old_conf=COGNITION_MODEL.context(s,'jonah')['beliefs'][0]['confidence']
COGNITION_MODEL.add_belief(s,'jonah','suspicion','The newcomer may be avoiding the green.',.45,'observation','test2')
out.append(check('duplicate proposition reinforces rather than duplicates',len(COGNITION_MODEL.context(s,'jonah')['beliefs'])==1 and COGNITION_MODEL.context(s,'jonah')['beliefs'][0]['confidence']>old_conf))
out.append(check('belief revision logged',COGNITION_MODEL.revise_belief(s,'jonah','The newcomer may be avoiding the green.',.2,'contradictory observation','evt_x') and bool(s['npc_cognition']['npcs']['jonah']['revision_log'])))
eid=MEMORY_MODEL.record(s,'observation','Mara saw the player tending the cottage garden.',actors=['mara'],location='ashcroft_cottage',witnesses=['mara'],importance=3)
out.append(check('witness can ingest event',COGNITION_MODEL.ingest_event(s,'mara',eid)))
out.append(check('non-witness cannot ingest event',not COGNITION_MODEL.ingest_event(s,'jonah',eid)))
out.append(check('goals and concerns persist',COGNITION_MODEL.add_concern(s,'mara','The neglected garden needs attention.',.7,eid) and COGNITION_MODEL.set_goal(s,'mara','Check the cottage garden again.','short',.7)))
ctx=COGNITION_MODEL.context(s,'mara')
out.append(check('bounded retrieval shape',set(ctx)=={'beliefs','impressions','concerns','unresolved_questions','short_term_goals','ambitions'} and len(ctx['beliefs'])<=6))
# Migration from v0.7.0-style state.
old=deepcopy(INITIAL_STATE); old.pop('npc_cognition',None); g2=Game(); g2.state=old; g2.migrate_state()
out.append(check('old save migration','npc_cognition' in g2.state and set(g2.state['npc_cognition']['npcs'])==set(g2.state['npcs'])))
# Cognition must not mutate objective weather/story.
before=(deepcopy(s['weather']),deepcopy(s['flags']))
COGNITION_MODEL.add_belief(s,'ruth','rumour','The weather will change because the village wants it.',.8,'hearsay')
out.append(check('subjective cognition cannot mutate objective state',(s['weather'],s['flags'])==before))
print(f"RESULT {sum(out)}/{len(out)}")
raise SystemExit(0 if all(out) else 1)
