from backend.core.game import Game
from backend.core.presentation_ledger_model import PRESENTATION_LEDGER_MODEL
from backend.ai.provider import AIProvider

g=Game()
for i in range(250): PRESENTATION_LEDGER_MODEL.append(g.state,'Narrator',f'line {i}')
pub=PRESENTATION_LEDGER_MODEL.public(g.state,80)
page=PRESENTATION_LEDGER_MODEL.page(g.state,0,100)
checks=[('public_bounded',len(pub['entries'])==80),('page_bounded',len(page['entries'])==100 and page['has_more']),('newest_first',page['entries'][0]['text']=='line 249')]
p=AIProvider(); checks += [('ctx_default',p.num_ctx==2048),('keepalive_short',p.keep_alive=='30s')]
for n,ok in checks: print(('PASS' if ok else 'FAIL'),n)
raise SystemExit(0 if all(ok for _,ok in checks) else 1)
