from copy import deepcopy
from backend.core.game import INITIAL_STATE
from backend.core.playstyle_pacing_model import PLAYSTYLE_PACING_MODEL
from backend.core.town_mind_model import TOWN_MIND_MODEL

def check(n,c): print(('PASS' if c else 'FAIL'),n); return bool(c)
def fresh(): return deepcopy(INITIAL_STATE)
r=[]
# five playstyle archetypes
s=fresh(); s['day']=8; s['investigation']['evidence']=['a']*8; r.append(check('investigator profile',PLAYSTYLE_PACING_MODEL.assess(s)['profile']=='investigator'))
h=fresh(); h['day']=8; h['player_life']['activity_history']=[{'activity':'garden'}]*20; h['property']['expansions']=['pantry_room']; r.append(check('homesteader profile',PLAYSTYLE_PACING_MODEL.assess(h)['profile']=='homesteader'))
e=fresh(); e['day']=8; e['player_businesses']['enterprises']={'x':{'cash':10,'health':70}}; r.append(check('entrepreneur profile',PLAYSTYLE_PACING_MODEL.assess(e)['profile']=='entrepreneur'))
so=fresh(); so['day']=8; so['relationships']['mara']['talks']=12; so['relationships']['mara']['affinity']=40; r.append(check('social profile',PLAYSTYLE_PACING_MODEL.assess(so)['profile']=='social'))
w=fresh(); w['day']=12; r.append(check('wanderer profile',PLAYSTYLE_PACING_MODEL.assess(w)['profile']=='wanderer'))
# pacing risk
r.append(check('stalled pacing detected',PLAYSTYLE_PACING_MODEL.assess(w)['pacing_risk']=='stalled'))
# strategy adapts to profile
h['day']=2; PLAYSTYLE_PACING_MODEL.assess(h); row=TOWN_MIND_MODEL.strategic_daily_tick(h); r.append(check('profile informs strategy',row and row['strategy']=='property_pressure'))
# resisted tactics accumulate failure and cause adaptation/retreat. monkey state protection through resistance domain protection
x=fresh(); x['day']=2; x['player_life']['activity_history']=[{'activity':'garden'}]*20; x['property']['expansions']=['pantry_room']; PLAYSTYLE_PACING_MODEL.assess(x)
x['resistance']['protected_domains']['property_pressure']=10
TOWN_MIND_MODEL.strategic_daily_tick(x); x['day']=3; TOWN_MIND_MODEL.strategic_daily_tick(x)
st=x['town_mind']['strategy']; r.append(check('failed tactic remembered',st['tactic_failures'].get('property_pressure',0)>=2))
x['day']=4; rr=TOWN_MIND_MODEL.strategic_daily_tick(x); r.append(check('deliberate retreat possible',rr and rr['effect']=='deliberate_retreat'))
r.append(check('hypothesis auditable',bool(st.get('hypothesis')) and st.get('hypothesis_confidence',0)>0))
r.append(check('strategy history carries hypothesis',bool(st.get('strategy_history')) and 'hypothesis' in st['strategy_history'][0]))
print(f'RESULT {sum(r)}/{len(r)}'); raise SystemExit(0 if all(r) else 1)
