from copy import deepcopy
from backend.core.game import INITIAL_STATE
from backend.core.social_obligation_model import SOCIAL_OBLIGATION_MODEL
from backend.ai.provider import AIProvider
s=deepcopy(INITIAL_STATE); checks=[]
def ck(n,v): checks.append((n,bool(v)))
rt=SOCIAL_OBLIGATION_MODEL.migrate(s)
rt['goals']['mara']={'id':'g1','npc':'mara','status':'active','capability':'stabilize_work','purpose':'Keep practical work stable while uncertainty grows','source_ids':['sf1']}
for i in range(3): SOCIAL_OBLIGATION_MODEL.record_intention_outcome(s,'mara',f'a{i}','work','mara_garden')
ck('executed actions become outcome evidence',rt['goals']['mara'].get('progress_evidence')==3)
ev=SOCIAL_OBLIGATION_MODEL.revise_goal_lifecycle(s,'mara')
ck('repeated aligned action progresses goal',ev and rt['goals']['mara']['status']=='progressed')
rt['goals']['jonah']={'id':'g2','npc':'jonah','status':'active','capability':'repair_relationship','purpose':'Repair a strained relationship through direct social effort','source_ids':['sf2']}
for i in range(4): SOCIAL_OBLIGATION_MODEL.record_intention_outcome(s,'jonah',f'b{i}','work','bakery')
ev=SOCIAL_OBLIGATION_MODEL.revise_goal_lifecycle(s,'jonah')
ck('persistent divergence triggers reconsideration',ev and rt['goals']['jonah']['status']=='reconsider')
p=AIProvider(); ck('single model default routing',p.fast_model==p.deep_model); ck('4096 default context',p.num_ctx==4096); ck('10m keep alive',p.keep_alive=='10m')
for n,v in checks: print(('PASS' if v else 'FAIL'),n)
print(f"{sum(v for _,v in checks)}/{len(checks)} PASS")
raise SystemExit(0 if all(v for _,v in checks) else 1)
