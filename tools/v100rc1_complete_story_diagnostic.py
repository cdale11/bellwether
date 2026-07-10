from copy import deepcopy
from backend.core.game import Game, INITIAL_STATE
from backend.core.story_model import STORY_MODEL, CHAPTERS

def ok(n,c):
 if not c: raise AssertionError(n)
 print('PASS',n)

g=Game(); s=g.state
ok('eight authored chapters',len(CHAPTERS)==8)
ok('starts at arrival',STORY_MODEL.public(s)['chapter']=='arrival')
# Force representative authoritative state, never debug story flags.
s['flags']['read_letter']=True
step=STORY_MODEL.advance_if_ready(s); ok('arrival gate',step and step['next']=='ordinary_life')
s['player_life']['activity_history']=[{'x':1}]*20
for k in list(s['player_life']['location_familiarity'])[:4]: s['player_life']['location_familiarity'][k]=8
step=STORY_MODEL.advance_if_ready(s); ok('ordinary-life gate',step and step['next']=='distributed_archive')
s['investigation']['evidence']=[f'e{i}' for i in range(14)]
mp=s['mystery_investigation']['mystery_progress']
for i,k in enumerate(mp): mp[k]['status']='deepening' if i<2 else 'active'
step=STORY_MODEL.advance_if_ready(s); ok('distributed archive gate',step and step['next']=='witnesses')
for i,r in enumerate(s['relationships'].values()): r['familiarity']=8; r['trust']=4 if i<3 else 0
step=STORY_MODEL.advance_if_ready(s); ok('witness gate',step and step['next']=='boundaries')
s['psychological_state']['familiarity_disruptions']=5
step=STORY_MODEL.advance_if_ready(s); ok('boundary gate',step and step['next']=='chorus_shape')
# enough evidence satisfies alternate convergence support
step=STORY_MODEL.advance_if_ready(s); ok('pattern gate',step and step['next']=='eleanor_method')
s['story_integration']['unlocked_beats']=[{'id':'a'},{'id':'b'}]
s['recurrence']['anchors']={'home':{'strength':1}}
step=STORY_MODEL.advance_if_ready(s); ok('Eleanor method gate',step and step['next']=='convergence')
step=STORY_MODEL.advance_if_ready(s); ok('convergence reaches eligibility',step and step['ending_eligible'])
ok('persistent revelations',len(s['authored_story']['revelations'])==8)
ok('public overview eligible',STORY_MODEL.public(s)['ending_eligible'])
# placeholder ending actions must not be exposed
s['location']='ashcroft_cottage'; s['branch_state']['endgame_unlocked']=True
acts={a['id'] for a in g.actions()}
ok('legacy placeholder endings remain removed',not any(x in {'ending:stay','ending:leave','ending:share','ending:keep'} for x in acts))
# migration
old=deepcopy(INITIAL_STATE); old.pop('authored_story',None); g2=Game(); g2.state=old; g2.migrate_state()
ok('old save migration','authored_story' in g2.state)
print('v1.0 RC1 complete story diagnostic: 13/13 PASS')
