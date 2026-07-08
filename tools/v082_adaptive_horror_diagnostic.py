#!/usr/bin/env python3
from copy import deepcopy
from backend.core.game import INITIAL_STATE
from backend.core.horror_model import HORROR_MODEL
from backend.core.player_identity_model import PLAYER_IDENTITY_MODEL

checks=[]
def check(name, ok):
    checks.append((name,bool(ok))); print(('PASS' if ok else 'FAIL'), name)

s=deepcopy(INITIAL_STATE); HORROR_MODEL.migrate(s)
check('migration creates adaptive state', 'adaptive' in s['systemic_horror'])
check('catalogue remains authored and unchanged in authority', len(HORROR_MODEL.anomalies)>=7)
# Different player profiles must produce different emphasis without inventing domains.
s['player_identity']=PLAYER_IDENTITY_MODEL.runtime_defaults(); s['player_identity']['coping_style']='connection'; s['player_identity']['traits']['social']=70
a=HORROR_MODEL.refresh_adaptive_profile(s); check('social profile emphasizes social vulnerability domains', a['preferred_domains'][:2]==['memory','information'])
s['player_identity']['coping_style']='pattern_seeking'; s['player_identity']['traits']['social']=0; s['player_identity']['traits']['inquiry']=70
a=HORROR_MODEL.refresh_adaptive_profile(s); check('investigative profile emphasizes information/geography', a['preferred_domains'][:2]==['information','geography'])
# Choice can only return eligible IDs.
s['location']='village_green'; s['flags']['read_letter']=True; s['player_life']['location_familiarity']['village_green']=10
c=HORROR_MODEL.eligible(s); chosen=HORROR_MODEL.choose(s,c)
check('adaptive chooser returns only eligible authored anomaly', chosen in c and chosen in HORROR_MODEL.anomalies)
# Quiet periods suppress selection.
HORROR_MODEL.set_quiet_period(s,8,'test'); check('quiet period suppresses eligible horror', HORROR_MODEL.choose(s,c) is None)
check('quiet suppression is auditable', s['systemic_horror']['adaptive']['suppressed_count']>=1)
# Applying never mutates unrelated authoritative resources.
s['systemic_horror']['adaptive']['quiet_until_pulse']=0; money=s.get('money'); inv=deepcopy(s.get('inventory'))
e=HORROR_MODEL.apply(s,chosen); check('legal anomaly applies', bool(e)); check('horror cannot alter money', s.get('money')==money); check('horror cannot alter inventory', s.get('inventory')==inv)
check('post anomaly recovery window created', s['systemic_horror']['adaptive']['quiet_until_pulse']>s['village_brain']['pulse_count'])
check('selection log is bounded and inspectable', isinstance(s['systemic_horror']['adaptive']['selection_log'],list))
check('developer context excludes hidden canon prose', 'preferred_domains' in HORROR_MODEL.developer_context(s) and 'text' not in HORROR_MODEL.developer_context(s))
# Unknown anomaly remains rejected.
check('unknown anomaly rejected', HORROR_MODEL.apply(s,'invented_horror') is None)
failed=[n for n,v in checks if not v]
print(f'\n{len(checks)-len(failed)}/{len(checks)} passed')
raise SystemExit(1 if failed else 0)
