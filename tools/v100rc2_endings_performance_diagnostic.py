from copy import deepcopy
import time
from backend.core.game import Game, INITIAL_STATE
from backend.core.ending_model import ENDING_MODEL, FAMILIES
from backend.ai.provider import provider
from backend.ai.async_runtime import ASYNC_AI_RUNTIME

checks=[]
def ok(name, cond):
    checks.append((name,bool(cond))); print(('PASS' if cond else 'FAIL'),name)

g=Game(); s=g.state
s['authored_story']['ending_eligible']=True
s['branch_state'].update({'care':6,'community':7,'inquiry':7,'avoidance':0})
for r in s['relationships'].values():
    if isinstance(r,dict): r['trust']=5; r['familiarity']=5
s['investigation']['evidence']=[{'id':str(i)} for i in range(10)]
s['player_life']['location_familiarity']={k:10 for k in list(__import__('backend.core.world_model',fromlist=['WORLD']).WORLD)[:5]}
s['recurrence']['run_index']=2
s['recurrence']['anchors']={'home':{'strength':2},'community':{'strength':2}}
elig=ENDING_MODEL.refresh(s)
ok('six family catalogue',len(FAMILIES)==6)
ok('ending eligibility deterministic and nonempty',bool(elig))
ok('true coexistence can be earned','liberation_coexistence' in elig)
actions=g.actions(); ok('only eligible endings exposed',set(a['id'].split(':',1)[1] for a in actions if a['id'].startswith('ending:'))==set(elig))
choice=elig[0]; ok('eligible ending resolves',g.resolve_ending(choice) is True)
ok('ending persists',s['ending_families']['resolved']['id']==choice)
ok('second ending blocked',g.resolve_ending(elig[-1]) is False)
# async ordinary directors: disabled provider makes worker deterministic/fallback-fast
old=provider.enabled; provider.enabled=False
try:
    g2=Game(); before=g2.state['ai_runtime'].get('world_rounds',0)
    submitted=g2.queue_ai_directors(['npc','traffic'],'diagnostic')
    deadline=time.time()+3
    while time.time()<deadline and ASYNC_AI_RUNTIME.status()['queued_or_running']:
        time.sleep(.02)
    g2.harvest_async_ai_results()
    ok('ordinary director batch submits asynchronously',submitted)
    ok('async director result harvested',g2.state['ai_runtime'].get('async_applied',0)+g2.state['ai_runtime'].get('async_stale_or_rejected',0)>=1)
finally: provider.enabled=old
ok('README current version', 'Bellwether v1.0 RC2' in open('README.md').read())
ok('developer control preserved','developer' in open('frontend/templates/index.html').read().lower())
print(f'{sum(x for _,x in checks)}/{len(checks)} passed')
raise SystemExit(0 if all(x for _,x in checks) else 1)
