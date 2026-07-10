from copy import deepcopy
from backend.core.game import INITIAL_STATE
from backend.core.narrative_expansion_model import NARRATIVE_EXPANSION_MODEL, SCENES
s=deepcopy(INITIAL_STATE); rt=NARRATIVE_EXPANSION_MODEL.migrate(s)
checks=[]
def c(n,x): checks.append((n,bool(x)))
c('scene_catalogue_depth',len(SCENES)>=9)
s['flags']['read_letter']=True
out=NARRATIVE_EXPANSION_MODEL.evaluate(s); c('arrival_scene',any(x['id']=='arrival_after_letter' for x in out))
c('once_only',not NARRATIVE_EXPANSION_MODEL.evaluate(s))
s['authored_story']['chapter']='witnesses'; s['relationships']['mara']['trust']=3
out=NARRATIVE_EXPANSION_MODEL.evaluate(s); c('mara_witness',any(x['id']=='witness_mara' for x in out))
c('jonah_gate_respected',not any(x['id']=='witness_jonah' for x in out))
s['relationships']['jonah']['trust']=3
out=NARRATIVE_EXPANSION_MODEL.evaluate(s); c('jonah_witness',any(x['id']=='witness_jonah' for x in out))
c('persistent_history',len(rt['history'])>=3)
c('public_spoiler_bounded','text' not in str(NARRATIVE_EXPANSION_MODEL.public(s)))
c('authority_boundary',all('requires' in x for x in SCENES.values()))
for n,x in checks: print(('PASS' if x else 'FAIL'),n)
print(f"{sum(x for _,x in checks)}/{len(checks)} PASS")
raise SystemExit(0 if all(x for _,x in checks) else 1)
