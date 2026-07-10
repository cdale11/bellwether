from copy import deepcopy
from backend.core.game import Game
from backend.core.purpose_model import PURPOSE_MODEL
from backend.core.social_obligation_model import SOCIAL_OBLIGATION_MODEL
from backend.ai.provider import provider

g=Game(); s=g.state
# seed a grounded social fact and goal for Jonah
from backend.core.causal_history_model import CAUSAL_HISTORY_MODEL
f=CAUSAL_HISTORY_MODEL.add_social_fact(s,'responsibility','jonah','village','Bakery strain has made reliability matter.',[],'diagnostic')
ok=SOCIAL_OBLIGATION_MODEL.apply_goal(s,'jonah',{'purpose':'Stabilize bakery work before confidence falls further.','capability':'stabilize_work','reason':'Current strain makes practical reliability important.','source_ids':[f['id']]},'diagnostic')
cands=[{'id':'work','kind':'work','destination':'bakery'},{'id':'rest','kind':'rest','destination':'bakery'}]
r=PURPOSE_MODEL.rank_candidates('jonah',cands,s)
checks={
'goal_applied':ok,
'goal_changes_ranking':r[0]['id']=='work' and any('self_goal:stabilize_work'==x for x in r[0]['purpose_score']['reasons']),
'goal_in_context':PURPOSE_MODEL.context('jonah',s,cands).get('self_generated_goal',{}).get('capability')=='stabilize_work',
'keep_alive_10m':provider.keep_alive=='10m',
}
for k,v in checks.items(): print(('PASS' if v else 'FAIL'),k)
print(f"{sum(checks.values())}/{len(checks)}")
raise SystemExit(0 if all(checks.values()) else 1)
