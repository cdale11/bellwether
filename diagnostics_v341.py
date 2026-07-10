from backend.core.action_surface import annotate
from backend.core.interpretation_model import INTERPRETATION_MODEL
checks=[]
def ck(n,v): checks.append((n,bool(v)))
a=annotate([{'id':'social:meal:mara','kind':'social','label':'Share a meal with Mara'}])[0]
ck('social_food_subject_remains_conversation',a['category']=='people' and a['intent']=='conversation')
s={'day':4,'memory_system':{'events':[{'id':'evt_a','summary':'Worked after fear'},{'id':'evt_b','summary':'Investigated despite fear'}]}}
r={'hypotheses':[{'claim':'The player may use work to regulate uncertainty.','confidence':.68,'supporting_evidence':['evt_a'],'contradicting_evidence':['evt_b'],'possible_test':'interrupt a routine'}]}
ck('review_applies',INTERPRETATION_MODEL.apply_review(s,'town_mind',r,'test-model'))
p=INTERPRETATION_MODEL.public_summary(s,'town_mind')
ck('revision_ledger_exposed',len(p.get('revision_ledger',[]))==1)
ck('contradiction_preserved',p['hypotheses'][0]['contradicting_evidence']==['evt_b'])
ck('test_preserved',p['hypotheses'][0]['possible_test']=='interrupt a routine')
js=open('frontend/static/js/game.js').read()
ck('ready_provider_treated_healthy',"['ready','healthy'].includes(d.provider?.state)" in js)
ck('ai_self_test_ui','runAiSelfTest' in js)
app=open('backend/app.py').read(); ck('ai_self_test_endpoint','/api/ai/self-test' in app)
print(f"v3.4.1 certification: {sum(v for _,v in checks)}/{len(checks)}")
for n,v in checks: print(('PASS' if v else 'FAIL'),n)
raise SystemExit(0 if all(v for _,v in checks) else 1)
