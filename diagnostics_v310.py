from copy import deepcopy
from backend.core.game import Game
from backend.core.causal_history_model import CAUSAL_HISTORY_MODEL
from backend.core.social_obligation_model import SOCIAL_OBLIGATION_MODEL
from backend.core.npc_project_model import NPC_PROJECT_MODEL

g=Game();s=g.state; checks=[]
def ck(n,v): checks.append((n,bool(v)));print(('PASS' if v else 'FAIL'),n)
f=CAUSAL_HISTORY_MODEL.add_social_fact(s,'suspicion','mara','player','Mara suspects the player is withholding part of an unsettling discovery.',['evt_test'],'diagnostic')
ctx=SOCIAL_OBLIGATION_MODEL.context_for(s,'mara');ck('social_fact_becomes_goal_evidence',f['id'] in {x['id'] for x in ctx['social_facts']})
res={'purpose':'Find a careful way to test whether the player is withholding something important.','capability':'seek_information','reason':'The suspicion matters, but direct accusation could damage trust.','source_ids':[f['id']]}
ck('grounded_goal_accepted',SOCIAL_OBLIGATION_MODEL.apply_goal(s,'mara',res,'diagnostic'))
ck('goal_persistent',SOCIAL_OBLIGATION_MODEL.migrate(s)['goals']['mara']['purpose'].startswith('Find a careful'))
bad=deepcopy(res);bad['source_ids']=['invented_fact'];ck('invented_goal_evidence_rejected',not SOCIAL_OBLIGATION_MODEL.apply_goal(s,'mara',bad,'diagnostic'))
o=SOCIAL_OBLIGATION_MODEL.create_obligation(s,'jonah','village','stabilize_work','Jonah feels responsible for stabilizing bakery supply.',['sit_test'],'diagnostic',days=1)
ck('obligation_created',o and o['status']=='active')
s['day']+=2;events=SOCIAL_OBLIGATION_MODEL.daily_tick(s);ck('overdue_obligation_has_consequence',events and o['status']=='overdue' and any(x.get('kind')=='resentment' for x in s['causal_history']['social_facts']))
NPC_PROJECT_MODEL.migrate(s)['projects']['mara']={'belief':'Something is inconsistent.','question':'What explains it?','status':'active'}
pctx=NPC_PROJECT_MODEL.reasoning_context(s,'mara');ck('goal_feeds_project_reasoning',pctx.get('social_context',{}).get('capability')=='seek_information')
ck('keep_alive_default_5m',__import__('backend.ai.provider',fromlist=['provider']).provider.keep_alive=='5m')
print(f"RESULT {sum(v for _,v in checks)}/{len(checks)}")
raise SystemExit(0 if all(v for _,v in checks) else 1)
