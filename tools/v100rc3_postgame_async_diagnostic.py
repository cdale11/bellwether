from backend.core.game import Game
from backend.core.postgame_model import POSTGAME_MODEL, ENDING_EFFECTS
from backend.ai.async_runtime import AsyncAIRuntime
import time
checks=[]
def ck(name,cond): checks.append((name,bool(cond))); print(('PASS' if cond else 'FAIL'),name)
g=Game(); s=g.state
# Force only the prerequisite ending eligibility flag and a legal ending.
s['authored_story']={'ending_eligible':True}
# direct model activation tests all family mappings without bypassing runtime rules
for eid in ENDING_EFFECTS:
    x=Game(); x.state.setdefault('ending_families',{})['resolved']={'id':eid,'title':eid}; rt=POSTGAME_MODEL.migrate(x.state)
    ck('postgame activates '+eid, rt['active'] and rt['ending_id']==eid and bool(rt['village_changes']))
x=Game(); x.state.setdefault('ending_families',{})['resolved']={'id':'accommodation','title':'Accommodation'}; POSTGAME_MODEL.migrate(x.state)
a={i for i,_ in POSTGAME_MODEL.actions(x.state)}
ck('postgame actions available', {'postgame:community','postgame:side_mystery'} <= a)
old=x.state['postgame']['legacy_points']; x.perform('postgame:community'); ck('postgame action persists',x.state['postgame']['legacy_points']==old+1)
ck('ordinary actions remain after resolution', any(z['id']=='rest' for z in x.actions()) and any(z['id'].startswith('move:') for z in x.actions()))
rt=AsyncAIRuntime(); ck('queue accepts job',rt.submit('test','director_batch',1,('npc',),lambda:{'ok':True}))
for _ in range(100):
    st=rt.status()
    if st['completed_waiting']: break
    time.sleep(.01)
ck('job lifecycle visible', any(e['event']=='job_queued' for e in st['recent_events']) and any(e['event']=='job_finished' for e in st['recent_events']))
job=rt.harvest()[0]; rt.record_application(job,'applied'); ck('application log visible',any(e['event']=='job_result_applied' for e in rt.status()['recent_events']))
ck('queue counters explicit',all(k in rt.status() for k in ('queued','running','completed_waiting','jobs','recent_events')))
print(f'{sum(v for _,v in checks)}/{len(checks)} PASS')
raise SystemExit(0 if all(v for _,v in checks) else 1)
