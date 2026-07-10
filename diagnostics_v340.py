from copy import deepcopy
from backend.core.game import Game
from backend.core.memory_model import MEMORY_MODEL
from backend.core.interpretation_model import INTERPRETATION_MODEL

g=Game(); s=g.state
ids=[]
ids.append(MEMORY_MODEL.record(s,'work','The player repaired the cottage immediately after an unsettling churchyard observation.',actors=['player'],location='ashcroft_cottage',importance=3,tags=['coping','home']))
ids.append(MEMORY_MODEL.record(s,'conversation','After another disturbing event, the player visited Mara but did not disclose the discovery.',actors=['player','mara'],location='mara_garden',importance=4,tags=['relationship','concealment']))
ids.append(MEMORY_MODEL.record(s,'observation','The player compared written parish records before accepting conflicting testimony.',actors=['player'],location='churchyard',importance=4,tags=['investigation','records']))
result={'hypotheses':[{'claim':'The player may use practical work and home routines to contain uncertainty rather than confronting fear directly.','confidence':.71,'supporting_evidence':[ids[0],ids[1]],'contradicting_evidence':[ids[2]],'possible_test':'Present mild uncertainty away from home and observe whether the player retreats into cottage work.','status':'active'}]}
checks=[]
def ck(name,ok): checks.append((name,bool(ok))); print(('PASS' if ok else 'FAIL'),name)
ck('evidence_packet_uses_authoritative_ids', all(x['id'].startswith('evt_') for x in INTERPRETATION_MODEL.evidence_packet(s)))
ck('interpretation_applies',INTERPRETATION_MODEL.apply_review(s,'town_mind',result,'test-model'))
h=INTERPRETATION_MODEL.public_summary(s,'town_mind')['hypotheses'][0]
ck('claim_preserved', 'practical work' in h['claim'])
ck('support_validated',h['supporting_evidence']==ids[:2])
ck('contradiction_preserved',h['contradicting_evidence']==[ids[2]])
bad=deepcopy(result); bad['hypotheses'][0]['supporting_evidence']=['invented_event']
ck('invented_evidence_rejected',not INTERPRETATION_MODEL.apply_review(s,'chorus',bad,'test-model'))
ck('observers_separate',not INTERPRETATION_MODEL.public_summary(s,'chorus')['hypotheses'])
from backend.core.town_mind_model import TOWN_MIND_MODEL
TOWN_MIND_MODEL.observe_player(s)
ck('town_mind_consumes_interpretation','interpreted_theory' in s['town_mind']['strategy'])
ck('possible_test_exposed',bool(s['town_mind']['strategy']['interpreted_theory']['possible_test']))
assert all(ok for _,ok in checks)
print(f'v3.4.0 interpretation foundation: {sum(ok for _,ok in checks)}/{len(checks)}')
