#!/usr/bin/env python3
from copy import deepcopy
import json
from backend.core.game import Game, INITIAL_STATE
from backend.core.social_consequence_model import SOCIAL_CONSEQUENCE_MODEL
checks=[]
def check(n,o,d=''): checks.append((n,bool(o),d)); print(('PASS' if o else 'FAIL'),n,d)
g=Game(); g.state=deepcopy(INITIAL_STATE); g.migrate_state()
sc=g.state['social_consequences']
check('social consequence substrate exists',sc['schema_version']==1)
check('all core NPC slots exist',set(g.state['npcs'])<=set(sc['by_npc']))
for text,typ in [("I promise I'll bring the apples tomorrow.",'promise'),("I'm sorry for what I said.",'apology'),("Would you like to walk with me?",'invitation'),("Could you help me?",'request'),("You're a useless liar.",'insult')]:
    row=SOCIAL_CONSEQUENCE_MODEL.extract_explicit_player_act(text); check('extract '+typ,row and row[0]==typ,str(row))
check('ordinary chat not mechanized',SOCIAL_CONSEQUENCE_MODEL.extract_explicit_player_act('The rain seems lighter today.') is None)
aid=SOCIAL_CONSEQUENCE_MODEL.record_act(g.state,'jonah','promise','The player promised to return.',True)
ctx=SOCIAL_CONSEQUENCE_MODEL.context(g.state,'jonah')
check('promise persists and retrieves',aid and ctx['open_commitments'] and ctx['open_commitments'][-1]['id']==aid)
SOCIAL_CONSEQUENCE_MODEL.record_act(g.state,'jonah','insult','The player insulted Jonah.',True)
check('grievance opens',len(SOCIAL_CONSEQUENCE_MODEL.context(g.state,'jonah')['open_grievances'])==1)
check('apology resolves grievance',bool(SOCIAL_CONSEQUENCE_MODEL.resolve_grievance(g.state,'jonah','explicit apology')) and not SOCIAL_CONSEQUENCE_MODEL.context(g.state,'jonah')['open_grievances'])
old=deepcopy(INITIAL_STATE); old.pop('social_consequences',None); g.state=old; g.migrate_state()
check('old save migration',g.state['social_consequences']['schema_version']==1)
check('JSON serializable',bool(json.dumps(g.state['social_consequences'])))
failed=[n for n,o,d in checks if not o]
print(f'RESULT {len(checks)-len(failed)}/{len(checks)}')
raise SystemExit(1 if failed else 0)
