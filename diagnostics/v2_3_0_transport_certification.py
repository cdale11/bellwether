from copy import deepcopy
from backend.core.game import Game
from backend.core.transport_model import TRANSPORT_MODEL

def check(name, ok):
 print(('PASS' if ok else 'FAIL'), name); return bool(ok)

g=Game(); s=g.state; results=[]
TRANSPORT_MODEL.migrate(s); s['money']=2000; s['location']='village_shop'
results.append(check('purchase bicycle', TRANSPORT_MODEL.perform(s,'transport:buy:bicycle')[0]))
results.append(check('purchase motorbike', TRANSPORT_MODEL.perform(s,'transport:buy:motorbike')[0]))
results.append(check('ownership persists', {'bicycle','motorbike'}<=set(s['transport']['owned'])))
TRANSPORT_MODEL.perform(s,'transport:select:bicycle'); origin='village_shop'; target=next(iter(__import__('backend.core.game',fromlist=['WORLD']).WORLD[origin]['exits'].values()))
from backend.core.game import WORLD
walk=deepcopy(s); walk['transport']['active']='walk'; bike=deepcopy(s); bike['transport']['active']='bicycle'
from backend.core.travel_model import TRAVEL_MODEL
wp=TRAVEL_MODEL.plan(walk,origin,target,WORLD); bp=TRAVEL_MODEL.plan(bike,origin,target,WORLD); bp['minutes']=max(3,round(bp['minutes']*TRANSPORT_MODEL.journey_modifier(bike)['multiplier']))
results.append(check('bicycle travel advantage', bp['minutes']<wp['minutes']))
f0=s['transport']['owned']['motorbike']['fuel']; TRANSPORT_MODEL.perform(s,'transport:select:motorbike'); TRANSPORT_MODEL.complete_journey(s,10)
results.append(check('fuel consumed', s['transport']['owned']['motorbike']['fuel']<f0))
c0=s['transport']['owned']['motorbike']['condition']; TRANSPORT_MODEL.complete_journey(s,10)
results.append(check('condition wear', s['transport']['owned']['motorbike']['condition']<c0))
s['location']='workshop_yard'; s['transport']['owned']['motorbike']['condition']=50; results.append(check('service action exposed', any(a[0]=='transport:service:motorbike' for a in TRANSPORT_MODEL.actions(s))))
results.append(check('service restores condition', TRANSPORT_MODEL.perform(s,'transport:service:motorbike')[0] and s['transport']['owned']['motorbike']['condition']==100))
results.append(check('public overview', TRANSPORT_MODEL.public(s)['cargo_capacity']>2))
results.append(check('economy ledger integration', any(x.get('kind','').startswith('transport_') for x in s['economy']['ledger'])))
print(f"RESULT {sum(results)}/{len(results)}")
raise SystemExit(0 if all(results) else 1)
