#!/usr/bin/env python3
from copy import deepcopy
from backend.core.game import Game, INITIAL_STATE
from backend.core.horror_aftermath_model import HORROR_AFTERMATH_MODEL
from backend.core.memory_model import MEMORY_MODEL
from backend.core.cognition_model import COGNITION_MODEL

def check(name, cond):
    if not cond: raise AssertionError(name)
    print('PASS', name)

g=Game(); s=g.state
HORROR_AFTERMATH_MODEL.migrate(s)
check('aftermath state migrates', 'horror_aftermath' in s)
s['location']='village_green'; s['npcs']['mrs_ellis']['location']='village_green'
a={'id':'test_anomaly','location':'village_green','domain':'geography','summary':'A familiar path appeared wrong.'}
r=HORROR_AFTERMATH_MODEL.register_anomaly(s,a,list(s['npcs']),MEMORY_MODEL,COGNITION_MODEL)
check('legal co-location witnesses recorded', 'mrs_ellis' in r['witnesses'])
check('remote npc not made witness', all(s['npcs'][x]['location']=='village_green' for x in r['witnesses']))
check('structured memory event created', any(e['id']==r['event_id'] for e in s['memory_system']['events']))
check('npc strain persists', s['horror_aftermath']['npc_aftermath']['mrs_ellis']['strain']>0)
check('temporary place avoidance persists', s['horror_aftermath']['npc_aftermath']['mrs_ellis']['avoid_locations']['village_green']>s['day'])
strain=s['horror_aftermath']['player']['strain']; unease=s['psychological_state']['unease']=20
check('ordinary recovery activity applies', HORROR_AFTERMATH_MODEL.note_recovery_activity(s,'tea'))
check('recovery reduces strain', s['horror_aftermath']['player']['strain']<strain)
check('recovery reduces unease boundedly', 0<=s['psychological_state']['unease']<20)
before=s['horror_aftermath']['npc_aftermath']['mrs_ellis']['strain']; HORROR_AFTERMATH_MODEL.daily_recovery(s)
check('npc recovery progresses with days', s['horror_aftermath']['npc_aftermath']['mrs_ellis']['strain']<before)
ctx=HORROR_AFTERMATH_MODEL.developer_context(s)
check('developer context exposes aftermath', 'npc_aftermath' in ctx and 'player' in ctx)
# Objective truth guard: aftermath cannot add evidence or facts.
check('aftermath does not create investigation evidence', not s.get('investigation',{}).get('evidence',[]))
print('v0.8.3 horror aftermath diagnostic: 12/12 PASS')
