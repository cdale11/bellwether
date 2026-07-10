from copy import deepcopy
from backend.core.game import INITIAL_STATE
from backend.core.interpretation_model import INTERPRETATION_MODEL
s=deepcopy(INITIAL_STATE)
mem=s['memory_system']; mem['events']=[
 {'id':'evt_a','day':1,'type':'conversation','summary':'Player confided in Mara','actors':['player','mara'],'witnesses':['mara'],'location':'ashcroft_cottage','tags':[],'importance':2},
 {'id':'evt_b','day':1,'type':'conversation','summary':'Player spoke privately to Jonah','actors':['player','jonah'],'witnesses':['jonah'],'location':'bakery','tags':[],'importance':2},
 {'id':'evt_c','day':2,'type':'observation','summary':'Player investigated a bell anomaly','actors':['player'],'witnesses':[],'location':'churchyard','tags':['anomaly','bell'],'importance':4},
]
mem['npc_memory']['mara']['event_refs']=['evt_a']; mem['npc_memory']['jonah']['event_refs']=['evt_b']
checks=[]
def ck(n,v): checks.append((n,bool(v)))
ck('six observer spaces',len(INTERPRETATION_MODEL.OBSERVERS)==6)
ck('mara private evidence', [x['id'] for x in INTERPRETATION_MODEL.visible_events(s,'mara')]==['evt_a'])
ck('jonah private evidence', [x['id'] for x in INTERPRETATION_MODEL.visible_events(s,'jonah')]==['evt_b'])
ck('chorus anomaly evidence','evt_c' in [x['id'] for x in INTERPRETATION_MODEL.visible_events(s,'chorus')])
ck('npc leakage blocked', not INTERPRETATION_MODEL.apply_review(s,'mara',{'hypotheses':[{'claim':'The player secretly trusts Jonah more.','confidence':.7,'supporting_evidence':['evt_b']}]},'test'))
ck('npc grounded theory accepted', INTERPRETATION_MODEL.apply_review(s,'mara',{'hypotheses':[{'claim':'The player may trust Mara with private uncertainty.','confidence':.7,'supporting_evidence':['evt_a'],'possible_test':'Notice whether they return after another unsettling event.'}]},'test'))
ck('observer separation', not INTERPRETATION_MODEL.public_summary(s,'jonah')['hypotheses'] and bool(INTERPRETATION_MODEL.public_summary(s,'mara')['hypotheses']))
for n,v in checks: print(('PASS' if v else 'FAIL'),n)
print(f'{sum(v for _,v in checks)}/{len(checks)}')
raise SystemExit(0 if all(v for _,v in checks) else 1)
