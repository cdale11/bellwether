"""v2.0.2 autonomous gameplay certification.

Runs spoiler-safe ordinary-life QA through Game.actions() and Game.perform(), the
same authoritative action surface and state transition entry point used by play.
It uses isolated fresh Game instances and never reads story prose or advances
blocked story/horror/ending/recurrence actions.
"""
from copy import deepcopy
from pathlib import Path
import json
from backend.core.game import Game
from backend.core.player_status_model import PLAYER_STATUS_MODEL
from backend.core.quest_model import QUEST_MODEL

ROOT=Path(__file__).resolve().parents[1]
results=[]
def record(goal, ok, evidence):
    results.append({'goal':goal,'passed':bool(ok),'evidence':evidence})
    print(('PASS' if ok else 'FAIL'), goal, '|', evidence)

def legal(game, action_id):
    return action_id in {a.get('id') for a in game.actions()}

def act(game, action_id):
    if not legal(game, action_id):
        return False, 'not exposed on authoritative action surface'
    before=deepcopy(game.state)
    game.perform(action_id)
    return before != game.state, 'performed through Game.perform'

# Food portability: same carried/household food action at home and away.
for loc in ('ashcroft_cottage','village_green','riverside_path'):
    g=Game(); g.state['location']=loc
    PLAYER_STATUS_MODEL.migrate(g.state)['hunger']=70
    g.state.setdefault('economy',{}).setdefault('household',{})['bread_loaf']=1
    visible=legal(g,'status:eat:bread'); before=PLAYER_STATUS_MODEL.migrate(g.state)['hunger']
    changed,msg=act(g,'status:eat:bread') if visible else (False,'not visible')
    after=PLAYER_STATUS_MODEL.migrate(g.state)['hunger']
    record(f'portable food at {loc}',visible and changed and after<before and g.state['economy']['household']['bread_loaf']==0,f'visible={visible}, hunger {before}->{after}, {msg}')

# Fishing loop: discover legal action, perform, verify inventory mutation and save payload round trip.
f=Game(); f.state['location']='riverside_path'; f.state['day']=1
f.state['player_activities']['hobbies']['sessions']['fishing']=0; f.state['player_activities']['skills']['fishing']=20
before=len(f.state.get('inventory',[])); changed,msg=act(f,'hobby:fish'); after=len(f.state.get('inventory',[]))
record('fishing catch reaches inventory',changed and after==before+1,f'inventory {before}->{after}, {msg}')
loader=Game(); loaded=loader.load_payload(deepcopy(f.state)); record('fishing inventory survives save round trip',bool(loaded.get('ok')) and loader.state.get('inventory')==f.state.get('inventory'),str(f.state.get('inventory',[])[-2:]))

# Cottage repair: autonomously execute only currently legal next step.
r=Game(); r.state['location']='ashcroft_cottage'; c=PLAYER_STATUS_MODEL.migrate(r.state)['cottage']; c['condition']=60
r.state.setdefault('economy',{}).setdefault('household',{})['repair_supplies']=1
sequence=[]
for expected in ('status:repair:inspect','status:repair:prepare','status:repair:work'):
    if legal(r,expected):
        changed,_=act(r,expected); sequence.append((expected,changed,c.get('active_repair'),c.get('condition')))
    else: sequence.append((expected,False,'not_legal',c.get('condition')))
record('repair prerequisite chain',all(x[1] for x in sequence) and c['condition']>60 and c.get('active_repair') is None,json.dumps(sequence))
remote=Game(); remote.state=deepcopy(r.state); remote.state['location']='village_green'; remote.state['player_status']['cottage']['active_repair']='prepared'
record('remote repair absent from legal surface',not legal(remote,'status:repair:work'),'repair work hidden away from cottage')

# Quest reward transaction is tested without exposing quest text.
q=Game(); qid=q.state['quests']['main'][0]['id']; m0=q.state.get('money',0)
first=QUEST_MODEL.complete(q.state,'main',qid); m1=q.state.get('money',0); second=QUEST_MODEL.complete(q.state,'main',qid); m2=q.state.get('money',0)
record('quest reward exactly once',bool(first and first.get('reward_applied') and second and not second.get('newly_completed') and m1==m2),f'money {m0}->{m1}->{m2}')

# Action-surface guard: no fabricated action is legal.
g=Game(); record('fabricated action excluded','qa:fabricated:action' not in {a.get('id') for a in g.actions()},f'{len(g.actions())} legal actions inspected')

# Release identity.
version=(ROOT/'VERSION').read_text().strip(); record('release identity',version=='2.0.2',version)

report={'version':version,'mode':'spoiler-safe autonomous ordinary-life certification','passed':sum(x['passed'] for x in results),'total':len(results),'results':results}
out=ROOT/'v202_ai_gameplay_certification_report.json'; out.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(f"v2.0.2 AI gameplay certification: {report['passed']}/{report['total']} PASS")
raise SystemExit(0 if report['passed']==report['total'] else 1)
