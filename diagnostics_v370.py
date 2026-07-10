from backend.core.game import Game
from backend.core.emergent_situation_model import EMERGENT_SITUATION_MODEL as M

g=Game();s=g.state
ctx=M.context(s); checks=[]
def c(n,x):checks.append((n,bool(x)))
c('heterogeneous_context', all(k in ctx for k in ('weather','business_pressure','relationships','npc_projects','town_theories','recent_world_events','legal_primitives')))
bad={'interpretation':'A sufficiently long invented proposal that must fail.','primitive_ids':['invent_world_fact']}
c('reject_invented_primitive', not M.apply_proposal(s,bad,'test'))
good={'interpretation':'Delivery pressure and exhaustion may combine into shorter bakery hours and a need for practical help.','causal_links':['delivery pressure may worsen exhaustion','exhaustion may reduce opening hours'],'primitive_ids':['bakery_reduce_hours','jonah_seek_help','player_mediation_opening']}
c('accept_grounded_proposal',M.apply_proposal(s,good,'test'))
out=M.execute(s)
c('legal_execution',len(out)==3)
c('modifier_created','bakery_reduce_hours' in s.get('emergent_modifiers',{}))
c('opportunity_created',any(x.get('type')=='social_mediation' for x in s.get('emergent_opportunities',[])))
c('npc_nudge_created',any(x.get('npc')=='jonah' for x in s.get('emergent_npc_nudges',[])))
c('history_preserved',bool(M.public(s).get('history')))
for n,v in checks:print(('PASS' if v else 'FAIL'),n)
print(f'{sum(v for _,v in checks)}/{len(checks)}')
raise SystemExit(0 if all(v for _,v in checks) else 1)
