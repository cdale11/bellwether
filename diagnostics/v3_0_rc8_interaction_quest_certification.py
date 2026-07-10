from copy import deepcopy
from backend.core.game import Game
from backend.core.procedural_arc_model import PROCEDURAL_ARC_MODEL, ARC_TEMPLATES

g=Game(); checks=[]
def check(n,c,d=''):
 checks.append((n,bool(c),d)); print(('PASS' if c else 'FAIL'),n,d)
# Every visible core NPC co-located with player must have at least one identity-tagged action when action system offers NPC interaction.
for nid,npc in g.state['npcs'].items():
 npc['visible']=True; npc['location']=g.state['location']
a=g.actions()
for nid,npc in g.state['npcs'].items():
 offered=[x for x in a if x.get('npc_id')==nid]
 check('npc_metadata_'+nid, bool(offered), str([x.get('id') for x in offered]))
# Side quest completion lifecycle
for q in g.state['quests']['side']: q['hidden']=False
r=g.complete('side','jonah'); q=next(x for x in g.state['quests']['side'] if x['id']=='jonah')
check('side_done',q.get('done') and q.get('status')=='completed')
check('side_reward_once',q.get('reward_applied'))
money=g.state['money']; g.complete('side','jonah'); check('side_reward_idempotent',g.state['money']==money)
# Procedural lifecycle: involvement is in progress, resolution becomes completed history with reward.
g2=Game(); root=PROCEDURAL_ARC_MODEL.migrate(g2.state); arc=PROCEDURAL_ARC_MODEL.start(g2.state,ARC_TEMPLATES[0]['id']); g2.state['location']=arc['location']; PROCEDURAL_ARC_MODEL.involve_player(g2.state,arc['id'],__import__('backend.core.memory_model',fromlist=['MEMORY_MODEL']).MEMORY_MODEL,__import__('backend.core.cognition_model',fromlist=['COGNITION_MODEL']).COGNITION_MODEL)
check('arc_in_progress',arc.get('status')=='in_progress')
# advance day and apply all due stages until resolved
for day in range(g2.state['day'],g2.state['day']+6):
 g2.state['day']=day
 for aa,t,st in list(PROCEDURAL_ARC_MODEL.due_stages(g2.state)):
  PROCEDURAL_ARC_MODEL.apply_stage(g2.state,aa,t,st,__import__('backend.core.memory_model',fromlist=['MEMORY_MODEL']).MEMORY_MODEL,__import__('backend.core.cognition_model',fromlist=['COGNITION_MODEL']).COGNITION_MODEL)
hist=PROCEDURAL_ARC_MODEL.migrate(g2.state)['history']; done=next((x for x in hist if x['id']==arc['id']),None)
check('arc_completed_history',done and done.get('status')=='resolved')
check('arc_reward_applied',done and done.get('reward_applied'))
view=g2.view(); pub=next((x for x in view['state']['quests']['side'] if x.get('id')=='arc:'+arc['id']),None)
check('arc_public_done',pub and pub.get('done') is True and pub.get('status')=='completed')
print(f"RESULT {sum(c for _,c,_ in checks)}/{len(checks)}")
raise SystemExit(0 if all(c for _,c,_ in checks) else 1)
