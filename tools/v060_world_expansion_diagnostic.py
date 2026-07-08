from backend.core.world_model import WORLD_MODEL
from backend.core.game import Game
from backend.core.activity_model import ACTIVITY_MODEL
from backend.core.danger_model import DANGER_MODEL

checks=[]
def check(name, cond):
 checks.append((name,bool(cond))); print(('PASS' if cond else 'FAIL'), name)

expanded={'field_lane','calder_farm','north_woods','old_quarry','quarry_caves'}
check('world has fourteen authored locations', len(WORLD_MODEL.locations)==14)
check('all five expansion locations present', expanded <= set(WORLD_MODEL.locations))
check('cottage can route to caves', WORLD_MODEL.shortest_player_route('ashcroft_cottage','quarry_caves') is not None)
check('expansion graph is bidirectionally NPC-adjacent', all(a in WORLD_MODEL.npc_neighbors(b) for a in expanded for b in WORLD_MODEL.npc_neighbors(a)))
g=Game(); g.migrate_state()
check('migration adds all location familiarity keys', set(WORLD_MODEL.locations) <= set(g.state['player_life']['location_familiarity']))
check('migration adds all location state keys', set(WORLD_MODEL.locations) <= set(g.state['location_state']))
check('migration adds all world modifier keys', set(WORLD_MODEL.locations) <= set(g.state['world_model']['location_modifiers']))
g.state['location']='north_woods'; acts={a for a,_ in ACTIVITY_MODEL.available_hobby_actions(g.state)}
check('woods support birdwatching and foraging', {'hobby:birdwatch','hobby:forage'} <= acts)
g.state['location']='old_quarry'; check('quarry exposes ordinary-life actions', any(a['id']=='life:study_stone' for a in g.actions()))
g.state['location']='quarry_caves'; check('caves expose investigation', any(a['id']=='investigate:observe' for a in g.actions()))
check('danger catalogue includes expansion hazards', {'quarry_loose_stone','cave_disorientation'} <= set(DANGER_MODEL.hazards))
check('world data validates', WORLD_MODEL.validate() is True)
print(f'v0.6.0 world expansion diagnostic: {sum(v for _,v in checks)}/{len(checks)} PASS')
raise SystemExit(0 if all(v for _,v in checks) else 1)
