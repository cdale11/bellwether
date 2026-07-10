#!/usr/bin/env python3
from copy import deepcopy
from backend.core.game import Game
from backend.core.content_model import CONTENT_MODEL

def check(name, ok):
 print(('PASS' if ok else 'FAIL')+': '+name); return bool(ok)

g=Game(); s=g.state; s['location']='ashcroft_cottage'; s['flags']['read_letter']=True
CONTENT_MODEL.migrate_v040(s)
results=[]
results.append(check('v0.4 daily-life state migrates', 'daily_life' in s['content_progression']))
a=CONTENT_MODEL.home_actions(s); results.append(check('cottage routines exposed', len(a)>=4))
ok,msg,m=CONTENT_MODEL.home_action(s,'air_rooms'); results.append(check('home routine changes persistent comfort', ok and m==15 and s['content_progression']['daily_life']['comfort']>20))
CONTENT_MODEL.note_activity(s,'garden'); CONTENT_MODEL.note_activity(s,'cooked'); summary=CONTENT_MODEL.close_day(s)
results.append(check('daily routine closes with variety and streak', summary['variety']>=3 and summary['routine_streak']==1))
CONTENT_MODEL.migrate_v040(s); results.append(check('migration idempotent', len(s['content_progression']['daily_life']['day_log'])==1))
print(f"v0.4.0 ordinary-life diagnostic: {sum(results)}/{len(results)}")
raise SystemExit(0 if all(results) else 1)
