from copy import deepcopy
from backend.core.game import INITIAL_STATE
from backend.core.playstyle_pacing_model import PLAYSTYLE_PACING_MODEL
from backend.ai.async_runtime import ASYNC_AI_RUNTIME

def ck(n,c): print(('PASS' if c else 'FAIL'),n); return bool(c)
def fresh(): return deepcopy(INITIAL_STATE)
r=[]
# Seven requested tempo/playstyle archetypes.
cases=[]
s=fresh(); s['day']=8; s['investigation']['evidence']=['e']*8; cases.append(('investigator',s))
s=fresh(); s['day']=8; s['player_life']['activity_history']=[{'activity':'garden'}]*20; s['property']['expansions']=['pantry_room']; cases.append(('homesteader',s))
s=fresh(); s['day']=8; s['player_businesses']['enterprises']={'stall':{'cash':20,'health':70}}; cases.append(('entrepreneur',s))
s=fresh(); s['day']=8; s['relationships']['mara']['talks']=15; s['relationships']['mara']['affinity']=15; cases.append(('social',s))
s=fresh(); s['day']=8; s['relationships']['mara']['talks']=3; s['relationships']['mara']['affinity']=80; cases.append(('romance_focused',s))
s=fresh(); s['day']=12; s['player_life']['activity_history']=[{'activity':'routine'}]*10; s['branch_state']['avoidance']=6; cases.append(('avoidant',s))
s=fresh(); s['day']=12; cases.append(('wanderer',s))
for expected,state in cases: r.append(ck(expected+' profile',PLAYSTYLE_PACING_MODEL.assess(state)['profile']==expected))
# Tempo risks remain observational and do not mutate authored story.
stalled=fresh(); stalled['day']=16; before=deepcopy(stalled['authored_story']); out=PLAYSTYLE_PACING_MODEL.assess(stalled)
r.append(ck('stalled tempo detected',out['pacing_risk']=='stalled'))
r.append(ck('pacing observer preserves story authority',stalled['authored_story']==before))
# Runtime status contract expected by developer UI.
bg=ASYNC_AI_RUNTIME.status()
r.append(ck('AI runtime status has numeric counters',all(isinstance(bg.get(k),int) for k in ('queued','running','completed_waiting'))))
r.append(ck('AI runtime status exposes jobs and events',isinstance(bg.get('jobs'),list) and isinstance(bg.get('recent_events'),list)))
print(f'RESULT {sum(r)}/{len(r)}'); raise SystemExit(0 if all(r) else 1)
