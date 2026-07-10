from backend.core.game import Game
from backend.ai.async_runtime import ASYNC_AI_RUNTIME

passed=0; total=0
def check(name, cond):
    global passed,total
    total+=1
    if cond: passed+=1; print('PASS',name)
    else: print('FAIL',name)

g=Game()
p=g.simulation_pacing_status()
check('pacing status has band',p.get('band') in {'low','moderate','high','critical'})
check('pacing hold is bounded',0 <= p.get('hold_seconds',99) <= 10)
g.record_world_event('A meaningful test change.','economy')
check('opportunity journal records meaningful event',len(g.state.get('ai_runtime',{}).get('coverage',{}).get('opportunity_journal',[]))>=1)
before=len(g.state['ai_runtime']['coverage']['opportunity_journal'])
g.record_world_event('Another small errand is completed as Bellwether moves through its day.','tick')
check('tick boilerplate excluded from opportunity journal',len(g.state['ai_runtime']['coverage']['opportunity_journal'])==before)
v=g.view()
check('public view exposes pacing state','simulation_pacing' in v)
check('pacing message is player-readable',bool(v['simulation_pacing'].get('message')))
print(f'{passed}/{total} PASS')
raise SystemExit(0 if passed==total else 1)
