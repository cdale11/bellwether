from backend.core.game import Game
from backend.core.resistance_model import RESISTANCE_MODEL
from backend.core.town_mind_model import TOWN_MIND_MODEL

def main():
 g=Game(); s=g.state; s['day']=2; checks=[]
 def ck(n,c): checks.append((n,bool(c)))
 ck('state', 'readiness' in RESISTANCE_MODEL.migrate(s))
 ok,_,_=RESISTANCE_MODEL.perform(s,'resist:prepare_home'); ck('prepare',ok and RESISTANCE_MODEL.public(s)['readiness']>=8)
 ck('protection',RESISTANCE_MODEL.pressure_modifier(s,'property_pressure')<1)
 ok,_,_=RESISTANCE_MODEL.perform(s,'resist:document'); ck('document',ok)
 ok,_,_=RESISTANCE_MODEL.perform(s,'resist:seek_support'); ck('support',ok)
 s['horror_aftermath']['player']['strain']=30; ok,_,_=RESISTANCE_MODEL.perform(s,'resist:recover'); ck('recovery',ok and s['horror_aftermath']['player']['strain']==18)
 RESISTANCE_MODEL.migrate(s)['readiness']=20; ok,_,_=RESISTANCE_MODEL.perform(s,'resist:counter'); ck('counter',ok and RESISTANCE_MODEL.public(s)['readiness']==8)
 ck('actions',any(a[0]=='resist:prepare_home' for a in RESISTANCE_MODEL.actions(s)))
 ck('public_view','resistance_overview' in g.view()['state'])
 s['town_mind']['strategy']['last_pressure_day']=0; row=TOWN_MIND_MODEL.strategic_daily_tick(s); ck('town_integration',row is not None)
 ck('bounded_log',len(RESISTANCE_MODEL.public(s)['counterplay_log'])<=80)
 for n,c in checks: print(('PASS' if c else 'FAIL'),n)
 print(f"{sum(c for _,c in checks)}/{len(checks)} PASS")
 if not all(c for _,c in checks): raise SystemExit(1)
if __name__=='__main__': main()
