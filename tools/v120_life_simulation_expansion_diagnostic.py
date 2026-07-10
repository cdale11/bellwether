from copy import deepcopy
from backend.core.game import Game, INITIAL_STATE
from backend.core.life_simulation_model import LIFE_SIMULATION_MODEL

g=Game.__new__(Game); g.state=deepcopy(INITIAL_STATE); g._overview_cache_key=None; g._overview_cache=None; g.migrate_state()
checks=[]
def ck(n,v): checks.append((n,bool(v))); print(('PASS' if v else 'FAIL'),n)
ck('life simulation state', 'life_simulation' in g.state)
# ordinary social interaction is public and relationship-bearing
g.state['location']='bakery'; g.state['npcs']['jonah']['location']='bakery'; acts={a['id'] for a in g.actions()}
ck('ordinary social action public','social:greet:jonah' in acts)
before=g.state['relationships']['jonah']['familiarity']; g.perform('social:greet:jonah'); ck('social action changes relationship',g.state['relationships']['jonah']['familiarity']>before)
# preservation loop
g.state['location']='ashcroft_cottage'; g.state['player_activities']['garden']['harvest_store']['radish']=5; g.state['economy']['household']['groceries']=2
acts={a['id'] for a in g.actions()}; ck('preservation action visible','lifesim:preserve:pickled_radish' in acts); g.perform('lifesim:preserve:pickled_radish'); ck('pantry preserve persisted',g.state['life_simulation']['pantry']['preserves'].get('pickled_radish',0)==2)
# community loop at legal weekly window
g.state['location']='village_green'; g.state['day']=6; g.state['minute']=600; acts={a['id'] for a in g.actions()}; ck('community action visible','lifesim:community:green_workday' in acts); g.perform('lifesim:community:green_workday'); ck('community standing progresses',g.state['life_simulation']['community']['participation']>=2)
# hobby mastery is derived from persistent hobby state
g.state['player_activities']['hobbies']['sessions']['birdwatching']=12; g.state['player_activities']['skills']['birdwatching']=22; mastery=LIFE_SIMULATION_MODEL.refresh_hobby_mastery(g.state); ck('hobby mastery rank',mastery['birdwatching']['rank']=='practised')
# public overview and save migration
v=g.view(); ck('life overview public','life_simulation_overview' in v['state']); snap=deepcopy(g.state); h=Game.__new__(Game);h.state=snap;h._overview_cache_key=None;h._overview_cache=None;h.migrate_state();ck('save migration preserves life state',h.state['life_simulation']['community']['participation']==g.state['life_simulation']['community']['participation'])
print(f'{sum(v for _,v in checks)}/{len(checks)} PASS'); raise SystemExit(0 if all(v for _,v in checks) else 1)
