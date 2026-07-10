from copy import deepcopy
from backend.core.game import Game, INITIAL_STATE

checks=[]
def check(name, ok, detail):
    checks.append((name,bool(ok),detail))

g=Game()
g.state=deepcopy(INITIAL_STATE)
g.migrate_state()
# Letter unlock path: Mara should be visible and actionable through both action surface and presence panel metadata.
g.state['location']='ashcroft_cottage'
g.perform('read_letter')
actions=g.actions()
talk=next((a for a in actions if a.get('id')=='talk:mara'),None)
check('mara_visible_after_letter',g.state['npcs']['mara'].get('visible') is True,'Letter unlock makes Mara visible')
check('mara_colocated_after_letter',g.state['npcs']['mara'].get('location')=='ashcroft_cottage','Mara starts at the cottage for her authored introduction')
check('mara_intro_action_available',talk is not None,'Authored Talk to Mara action is available')
check('talk_action_has_panel_identity',bool(talk and talk.get('npc_id')=='mara' and talk.get('npc_name')=='Mara'),'Presence panel can associate authored talk action with Mara')
# Execute authored introduction and verify dialogue choices.
g.perform('talk:mara')
check('mara_dialogue_opens',g.state.get('dialogue',{}).get('npc')=='mara','Talk action opens Mara authored dialogue')
check('mara_intro_choices',len(g.state.get('dialogue',{}).get('choices',[]))>=2,'Mara authored introduction exposes choices')
g.perform('choice:mara_garden')
check('mara_intro_completes',g.state['flags'].get('met_mara') is True,'Choice completes Mara introduction')
# Repeat interaction should become free-talk and retain panel identity.
g.state['location']=g.state['npcs']['mara']['location']
actions=g.actions()
free=next((a for a in actions if a.get('id')=='free_talk:mara'),None)
check('mara_repeat_free_talk',free is not None,'Repeat Mara interaction exposes free-talk path')
check('free_talk_panel_identity',bool(free and free.get('npc_id')=='mara' and free.get('npc_name')=='Mara'),'Presence panel can associate free-talk action with Mara')
# All authored story talk actions should carry the same metadata contract.
for npc_id,npc in g.state.get('npcs',{}).items():
    if npc.get('visible',True) and npc.get('location')==g.state['location']:
        for a in g.actions():
            if a.get('id')==f'talk:{npc_id}':
                check(f'talk_metadata_{npc_id}',a.get('npc_id')==npc_id and a.get('npc_name')==npc.get('name'),f'{npc_id} talk metadata matches presence identity')
failed=[x for x in checks if not x[1]]
print(f'RC7 MARA INTERACTION: {len(checks)-len(failed)}/{len(checks)} PASS')
for n,ok,d in checks: print(('PASS' if ok else 'FAIL'),n,'-',d)
raise SystemExit(1 if failed else 0)
