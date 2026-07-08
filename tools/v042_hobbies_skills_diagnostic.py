#!/usr/bin/env python3
from copy import deepcopy
from backend.core.game import Game, INITIAL_STATE
from backend.core.activity_model import ACTIVITY_MODEL

def check(name, cond):
 print(('PASS' if cond else 'FAIL'), name)
 if not cond: raise AssertionError(name)

s=deepcopy(INITIAL_STATE); s['player_activities'].pop('hobbies',None); s['player_activities']['skills'].pop('fishing',None)
ACTIVITY_MODEL.migrate(s)
check('old activity state migrates', 'hobbies' in s['player_activities'] and 'fishing' in s['player_activities']['skills'])
check('river exposes outdoor hobbies', {'hobby:birdwatch','hobby:forage','hobby:fish','hobby:sketch'} <= {x for x,_ in (lambda st:(st.update(location='riverside_path') or ACTIVITY_MODEL.available_hobby_actions(st)))(s)})
g=Game(); g.state=deepcopy(INITIAL_STATE); g.state['location']='riverside_path'; g.state['season']['id']='early_autumn'; g.migrate_state()
before=g.state['minute']; g.perform_hobby_activity('hobby:birdwatch')
check('birdwatch consumes time', g.state['minute']>before)
check('birdwatch persists session', g.state['player_activities']['hobbies']['sessions']['birdwatching']==1)
check('birdwatch advances skill', g.state['player_activities']['skills']['birdwatching']>0)
g.perform_hobby_activity('hobby:forage')
check('foraging persists produce', sum(g.state['player_activities']['hobbies']['collections']['foraged'].values())>0)
g.perform_hobby_activity('hobby:fish')
check('fishing session persists', g.state['player_activities']['hobbies']['sessions']['fishing']==1)
g.state['location']='churchyard'; g.perform_hobby_activity('hobby:history')
check('history note persists', 'churchyard_masons_marks' in g.state['player_activities']['hobbies']['collections']['history_notes'])
g.state['location']='village_green'; g.perform_hobby_activity('hobby:sketch')
check('sketch persists', len(g.state['player_activities']['hobbies']['collections']['sketches'])==1)
check('activity history integration', any(x['activity'].startswith('hobby_') for x in g.state['player_life']['activity_history']))
check('hobby actions remain location bounded', 'hobby:fish' not in {x for x,_ in ACTIVITY_MODEL.available_hobby_actions(g.state)})
print('v0.4.2 hobbies/skills diagnostic: 11/11 PASS')
