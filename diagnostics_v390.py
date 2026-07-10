from backend.core.action_surface import annotate
from backend.core.game import Game
from backend.core.causal_history_model import CAUSAL_HISTORY_MODEL
from backend.core.emergent_situation_model import EMERGENT_SITUATION_MODEL
checks=[]
def ck(n,v):checks.append((n,bool(v)))
# Explicit subcategory contract audit across representative action families.
sample=[
 {'id':'social:meal:mara','label':'Share a meal with Mara','kind':'social'},
 {'id':'animals:feed','label':'Feed the Cottage Animals','kind':'life','category':'home'},
 {'id':'animals:buy_feed','label':'Buy Animal Feed','kind':'economy','category':'work'},
 {'id':'arc:help:x','label':'Help with bakery backlog','kind':'life'},
 {'id':'sleep','label':'Sleep Until Morning','kind':'life'},
 {'id':'content:repair:roof','label':'Repair: Roof','kind':'life'},
 {'id':'investigate:search','label':'Examine the Area Closely','kind':'investigate'},
]
a={x['id']:x for x in annotate(sample)}
ck('social_meal_is_conversation',a['social:meal:mara']['intent']=='conversation')
ck('animal_care_intent',a['animals:feed']['intent']=='animal_care')
ck('animal_purchase_intent',a['animals:buy_feed']['intent']=='animal_supplies')
ck('procedural_help_intent',a['arc:help:x']['intent']=='community_help')
ck('sleep_rest_intent',a['sleep']['intent']=='rest')
ck('repair_maintenance_intent',a['content:repair:roof']['intent']=='maintenance')
ck('investigation_category',a['investigate:search']['category']=='investigate')
g=Game(); ck('game_initializes',bool(g.state))
# Causal persistence: emergent consequence becomes provenance and social fact.
r={'primitive_ids':['mara_misread_distance','player_mediation_opening'],'interpretation':'Bakery strain and recent distance plausibly create social uncertainty and a mediation opening.','causal_links':['strain -> distance','distance -> uncertainty']}
ck('proposal_accepted',EMERGENT_SITUATION_MODEL.apply_proposal(g.state,r,'test'))
out=EMERGENT_SITUATION_MODEL.execute(g.state)
rt=CAUSAL_HISTORY_MODEL.migrate(g.state)
ck('emergent_executes',len(out)==2)
ck('social_fact_persists',len(rt['social_facts'])>=2)
ck('provenance_links_persist',len(rt['links'])>=2 and all(x.get('causes') for x in rt['links']))
for n,v in checks:print(('PASS' if v else 'FAIL'),n)
print(f'{sum(v for _,v in checks)}/{len(checks)}')
raise SystemExit(0 if all(v for _,v in checks) else 1)
