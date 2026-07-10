from copy import deepcopy
from backend.core.game import INITIAL_STATE
from backend.core.npc_life_model import NPC_LIFE_MODEL
from backend.core.population_model import POPULATION_MODEL
from backend.core.social_model import SOCIAL_MODEL
s=deepcopy(INITIAL_STATE); POPULATION_MODEL.migrate(s); rt=NPC_LIFE_MODEL.migrate(s)
checks=[]
def c(n,x): checks.append((n,bool(x)))
c('persistent_runtime', 'npc_autonomous_lives' in s)
c('core_goals', bool(rt['core_goals']))
c('resident_lives', len(rt['resident_lives'])>=20)
s['day']=2; ev=NPC_LIFE_MODEL.advance_day(s); c('daily_progress', any(g['progress']>0 for g in rt['core_goals'].values()))
c('idempotent_day', NPC_LIFE_MODEL.advance_day(s)==[])
nid=next(iter(rt['core_goals'])); before=rt['core_goals'][nid]['progress']; c('player_influence', NPC_LIFE_MODEL.influence(s,nid,'helped',2) and rt['core_goals'][nid]['progress']==before+2)
c('bounded_events', len(rt['life_events'])<=160)
c('social_web_preserved', bool(s.get('npc_social_web')))
c('population_preserved', len(s['population']['residents'])>=20)
c('public_surface', NPC_LIFE_MODEL.public(s)['resident_life_count']>=20)
for n,ok in checks: print(('PASS' if ok else 'FAIL'),n)
print(f'{sum(x for _,x in checks)}/{len(checks)} PASS')
raise SystemExit(0 if all(x for _,x in checks) else 1)
