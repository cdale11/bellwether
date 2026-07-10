from backend.core.game import Game
from backend.core.ai_player import AI_PLAYER

def check(name, ok):
    print(('PASS' if ok else 'FAIL'), name)
    return bool(ok)

results=[]
g=Game(); s=g.state; s['money']=30
s['location']='village_shop'
a={x['id'] for x in g.actions()}; results.append(check('starter produce public purchase path','economy:buy:village_shop:radish_bunch' in a))
g.perform('economy:buy:village_shop:radish_bunch')
results.append(check('starter produce reaches cooking ingredient store',s['player_activities']['garden']['harvest_store'].get('radish',0)>=2))
s['location']='bakery';g.perform('economy:buy:bakery:bread_loaf');s['location']='ashcroft_cottage'
a={x['id'] for x in g.actions()};results.append(check('starter recipe becomes public','content:cook:radish_toast' in a))
b=AI_PLAYER._state_digest(s);g.perform('content:cook:radish_toast');aft=AI_PLAYER._state_digest(s);d=AI_PLAYER._diff(b,aft)
ok,_=AI_PLAYER._certification_evidence('cooking','content:cook:radish_toast','Cook Radish and butter toast',b,aft,d,True);results.append(check('cooking certification observes real consequence',ok))
s['location']='north_woods';b=AI_PLAYER._state_digest(s);g.perform('hobby:forage');aft=AI_PLAYER._state_digest(s);d=AI_PLAYER._diff(b,aft)
ok,_=AI_PLAYER._certification_evidence('fishing_foraging','hobby:forage','Go Foraging',b,aft,d,True);results.append(check('foraging collection certification',ok))
b=AI_PLAYER._state_digest(s);g.perform('investigate:review');aft=AI_PLAYER._state_digest(s);d=AI_PLAYER._diff(b,aft)
results.append(check('informational review exempt from silent-no-effect warning',not AI_PLAYER._detect_anomalies(b,aft,'investigate:review',True,d)))
s['location']='bakery';s['money']=20;b=AI_PLAYER._state_digest(s);g.perform('economy:buy:bakery:bakery_breakfast');aft=AI_PLAYER._state_digest(s);d=AI_PLAYER._diff(b,aft)
results.append(check('bakery meal consequence visible to digest',bool(d)))
source=open('backend/core/ai_player.py').read();results.append(check('campaign effort budget present',"attempts']>=18" in source and "status']='deferred'" in source))
results.append(check('passive weather certification present',"Passive environment certification" in source and "_certification_evidence('weather_ecology'" in source))
js=open('frontend/static/js/game.js').read();results.append(check('campaign progress label disambiguated','Campaign progress:' in js and 'domains certified' in js))
version=open('VERSION').read().strip();results.append(check('release identity',version=='2.0.5'))
print(f"{sum(results)}/{len(results)} PASS")
raise SystemExit(0 if all(results) else 1)
