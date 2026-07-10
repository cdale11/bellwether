"""Focused deterministic certification for v3.0.0-rc2 content-density expansion."""
from copy import deepcopy
from backend.core.game import INITIAL_STATE
from backend.core.activity_model import CROPS, ACTIVITY_MODEL, HOBBY_DISCOVERIES
from backend.core.economy_model import ECONOMY_MODEL, ITEMS, PRODUCE_VALUES
from backend.core.content_model import CONTENT_MODEL, RECIPES
from backend.core.life_simulation_model import LIFE_SIMULATION_MODEL, PRESERVES

checks=[]
def check(name, ok):
    checks.append((name,bool(ok))); print(('PASS' if ok else 'FAIL'), name)

s=deepcopy(INITIAL_STATE); ACTIVITY_MODEL.migrate(s); ECONOMY_MODEL.migrate(s); CONTENT_MODEL.migrate_v040(s); LIFE_SIMULATION_MODEL.migrate(s)
check('crop catalogue expanded', all(x in CROPS for x in ('potato','kale','pea')) and len(CROPS)>=7)
check('seed economy integrated', all(x in ITEMS for x in ('potato_seed','kale_seed','pea_seed')) and all(x in PRODUCE_VALUES for x in ('potato','kale','pea')))
s['location']='village_shop'; s['money']=100
ok,msg=ECONOMY_MODEL.buy(s,'village_shop','potato_seed'); check('new seed public economy path', ok and s['player_activities']['garden']['seed_stock']['potato']>=3 and s['money']<100)
check('recipe catalogue expanded', len(RECIPES)>=11 and all(x in RECIPES for x in ('potato_hash','nettle_soup','trout_supper')))
s['location']='ashcroft_cottage'; s['player_activities']['hobbies']['collections']['foraged']['nettles']=2; s['economy']['household']['groceries']=3
acts=dict(CONTENT_MODEL.cooking_actions(s)); check('forage-to-cooking action exposed', 'content:cook:nettle_soup' in acts)
ok,msg,mins=CONTENT_MODEL.cook(s,'nettle_soup'); check('forage-to-cooking consumption', ok and s['player_activities']['hobbies']['collections']['foraged']['nettles']==0 and s['player_life']['meals']>=2)
s['player_activities']['hobbies']['collections']['fish']['brown_trout']=1; s['economy']['household']['groceries']=3
check('fish-to-cooking action exposed', 'content:cook:trout_supper' in dict(CONTENT_MODEL.cooking_actions(s)))
ok,msg,mins=CONTENT_MODEL.cook(s,'trout_supper'); check('fish-to-cooking consumption', ok and s['player_activities']['hobbies']['collections']['fish']['brown_trout']==0)
check('forage seasonal depth', bool(HOBBY_DISCOVERIES['foraged']['deep_winter']) and 'field_mushroom' in HOBBY_DISCOVERIES['foraged']['late_autumn'])
check('fish catalogue expanded', len(HOBBY_DISCOVERIES['fish'])>=6)
check('preservation catalogue expanded', len(PRESERVES)>=6 and all(x in PRESERVES for x in ('potato_store','kale_pickle','pea_relish')))
print(f"RESULT {sum(v for _,v in checks)}/{len(checks)}")
raise SystemExit(0 if all(v for _,v in checks) else 1)
