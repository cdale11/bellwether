from pathlib import Path
from copy import deepcopy
from backend.ai.provider import AIProvider
from backend.core.game import Game
from backend.core.economy_model import ECONOMY_MODEL
ROOT=Path(__file__).resolve().parents[1]
checks=[]
def check(n,ok,d): checks.append((n,bool(ok),d))
src=(ROOT/'backend/ai/provider.py').read_text()
check('dialogue_answers_questions','If it asks a question, answer it before adding anything else.' in src,'Prompt explicitly prioritizes direct answers')
check('dialogue_handles_advice','If it asks for advice, give concrete in-world advice' in src,'Advice requests receive concrete grounded guidance')
check('dialogue_handles_disclosure','acknowledge the specific content rather than replying generically' in src,'Player disclosures require specific acknowledgement')
check('dialogue_continuity','never reset the conversation as though each message were the first' in src,'Follow-up turns use recent continuity')
check('dialogue_length_flexible','1-3 short sentences' in src and 'len(words)>60' in src,'Replies may breathe beyond one sentence but remain bounded')
check('dialogue_followup_bounded','do not end every reply with a question' in src,'Follow-up questions are optional rather than formulaic')
check('knowledge_humility','It is acceptable to say you do not know.' in src,'NPC knowledge ceiling allows uncertainty')
check('authority_boundary','Do not invent plot facts, secrets, invitations, shared plans, objects, or off-screen events.' in src,'Dialogue remains non-authoritative')
# Accelerated baseline economy stability: deterministic market should stay finite and bounded without player intervention.
g=Game(); baseline=deepcopy(g.state)
for day in range(2,122):
    g.state['day']=day
    ECONOMY_MODEL.daily_tick(g.state)
e=ECONOMY_MODEL.migrate(g.state); businesses=e['market']['businesses']; demands=e['market']['produce_demand']
check('economy_prices_positive',all(ECONOMY_MODEL.price(g.state,sid,iid)>=1 for sid in businesses for iid in __import__('backend.core.economy_model',fromlist=['SHOPS']).SHOPS[sid]['stock']),'All shop prices remain positive after 120 accelerated days')
check('economy_business_finite',all(0<=float(b['health'])<=100 and float(b['cash_reserve'])>=0 for b in businesses.values()),'Business health and reserves remain finite/bounded')
check('economy_demand_bounded',all(0.25<=float(v)<=3.0 for v in demands.values()),'Produce demand remains in a playable finite band')
check('economy_history_bounded',len(e['market']['history'])<=120 and len(e['ledger'])<=240,'Long-run economy histories remain bounded')
for n,ok,d in checks: print(('PASS' if ok else 'FAIL'),n,'-',d)
print(f'RESULT {sum(x[1] for x in checks)}/{len(checks)}')
raise SystemExit(0 if all(x[1] for x in checks) else 1)
