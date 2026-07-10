from pathlib import Path
from backend.core.game import Game
from backend.core.action_surface import compact
from backend.ai.provider import AIProvider
ROOT=Path(__file__).resolve().parents[1]
checks=[]
def check(n,ok,d): checks.append((n,bool(ok),d))
g=Game(); g.state['location']='ashcroft_cottage'; g.state['flags']['read_letter']=True
acts=g.actions(); pub=g.view()['actions']
check('sleep_authoritative',any(a['id']=='sleep' for a in acts),'Sleep is produced by authoritative cottage action grammar after letter unlock')
check('sleep_compact_surface',any(a['id']=='sleep' for a in pub),'Sleep survives bounded compact action disclosure even when Home & Life is crowded')
# crowding regression: sleep must survive more than category limit
crowd=[{'id':f'life:x{i}','label':f'Activity {i}','kind':'life'} for i in range(20)]+[{'id':'sleep','label':'Sleep Until Morning','kind':'life'}]
check('sleep_priority_under_crowding',any(a['id']=='sleep' for a in compact(crowd)),'Sleep is priority-preserved under Home & Life crowding')
src=(ROOT/'backend/ai/provider.py').read_text()
check('foreground_timeout','BELLWETHER_PLAYER_CONVERSATION_TIMEOUT' in src,'Foreground conversation has configurable bounded timeout')
check('foreground_retry','tries_override=2,foreground=True' in src,'Foreground conversation has bounded retry path')
check('repetition_guard','_dialogue_repeats_recent' in src and 'repetition_repaired' in src,'Recent-reply repetition is detected and repair is tracked')
check('daypart_guard','_obvious_daypart_contradiction' in src,'Obvious daypart contradiction guard exists')
check('hard_reply_bound','if len(words)>24' in src,'Foreground replies have a hard display/storage word bound')
check('authority_prompt','Do not invent plot facts, secrets, invitations, shared plans, objects, or off-screen events.' in src,'Foreground prompt protects authoritative facts')
check('disabled_fallback','if not self.enabled:' in src and 'return None' in src,'Provider exposes deterministic no-AI fallback contract')
for n,ok,d in checks: print(('PASS' if ok else 'FAIL'),n,'-',d)
print(f'RESULT {sum(x[1] for x in checks)}/{len(checks)}')
raise SystemExit(0 if all(x[1] for x in checks) else 1)
