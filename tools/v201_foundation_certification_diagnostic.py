"""v2.0.1 focused foundation certification: public action contracts and player-visible ordinary-life loops."""
from copy import deepcopy
from pathlib import Path
from backend.core.game import Game
from backend.core.player_status_model import PLAYER_STATUS_MODEL
from backend.core.quest_model import QUEST_MODEL

ROOT=Path(__file__).resolve().parents[1]
checks=[]
def check(name,ok,detail=''):
    checks.append((name,bool(ok),detail)); print(('PASS' if ok else 'FAIL'),name,('| '+detail) if detail else '')

g=Game()
g.state['location']='ashcroft_cottage'
ps=PLAYER_STATUS_MODEL.migrate(g.state); ps['hunger']=70
g.state.setdefault('economy',{}).setdefault('household',{})['bread_loaf']=1
aids={a['id'] for a in g.actions()}
check('bread action player-visible','status:eat:bread' in aids)
before=ps['hunger']; g.perform('status:eat:bread'); after=PLAYER_STATUS_MODEL.migrate(g.state)['hunger']
check('bread consumption changes authoritative hunger',after<before and g.state['economy']['household']['bread_loaf']==0,f'{before:.1f}->{after:.1f}')

# Repair is a staged, location-bound state machine.
r=Game(); r.state['location']='ashcroft_cottage'; c=PLAYER_STATUS_MODEL.migrate(r.state)['cottage']; c['condition']=60; r.state['economy']['household']['repair_supplies']=1
check('repair inspect exposed','status:repair:inspect' in {a['id'] for a in r.actions()})
r.perform('status:repair:inspect'); check('repair prepare follows inspect',c['active_repair']=='inspected' and 'status:repair:prepare' in {a['id'] for a in r.actions()})
r.perform('status:repair:prepare'); check('repair work follows preparation',c['active_repair']=='prepared' and r.state['economy']['household']['repair_supplies']==0)
before_cond=c['condition']; r.perform('status:repair:work'); check('repair improves persistent condition',c['condition']>before_cond and c['active_repair'] is None,f'{before_cond:.1f}->{c["condition"]:.1f}')
remote=deepcopy(r.state); remote['location']='village_green'; remote['player_status']['cottage']['active_repair']='prepared'; before_remote=remote['player_status']['cottage']['condition']; ok,msg,mins=PLAYER_STATUS_MODEL.perform(remote,'status:repair:work')
check('remote repair rejected',not ok and mins==0 and remote['player_status']['cottage']['condition']==before_remote,msg)

# Fishing must be both legal on the public surface and mutate carried inventory on a successful deterministic catch.
f=Game(); f.state['location']='riverside_path'; f.state['day']=1; rt=f.state['player_activities']; rt['hobbies']['sessions']['fishing']=0; rt['skills']['fishing']=20
check('fishing action player-visible','hobby:fish' in {a['id'] for a in f.actions()})
inv_before=len(f.state.get('inventory',[])); f.perform('hobby:fish'); check('successful fishing writes inventory',len(f.state.get('inventory',[]))==inv_before+1,str(f.state.get('inventory',[])[-1:]));

# Quest reward exactly-once contract.
q=Game(); q0=q.state['quests']['main'][0]['id']; m0=q.state.get('money',0); first=QUEST_MODEL.complete(q.state,'main',q0); m1=q.state.get('money',0); second=QUEST_MODEL.complete(q.state,'main',q0); m2=q.state.get('money',0)
check('quest reward transaction exactly once',first and first.get('reward_applied') and second and not second.get('newly_completed') and m1==m2,f'{m0}->{m1}->{m2}')

# Save payload migration round-trip without filesystem dependence.
snap=deepcopy(r.state); loader=Game(); result=loader.load_payload(snap)
check('portable save round-trip',result.get('ok') and loader.state['location']==snap['location'] and loader.state['player_status']['cottage']['condition']==snap['player_status']['cottage']['condition'])

# Release hygiene/version/report source contracts.
version=(ROOT/'VERSION').read_text().strip(); check('release version','2.0.1'==version,version)
app=(ROOT/'backend/app.py').read_text(); aip=(ROOT/'backend/core/ai_player.py').read_text()
check('public API rejects stale illegal actions','req.action not in legal' in app)
check('AI report version is dynamic','f"Version: {version}"' in aip and 'Version: 2.0.0' not in aip)

passed=sum(ok for _,ok,_ in checks); print(f'v2.0.1 foundation certification: {passed}/{len(checks)} PASS')
raise SystemExit(0 if passed==len(checks) else 1)
