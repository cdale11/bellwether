from backend.core.investigation_model import INVESTIGATION_MODEL as M
from backend.core.game import Game

def check(ok,msg):
    if not ok: raise AssertionError(msg)
    print('PASS',msg)
check(len(M.mysteries)>=7,'seven or more mystery threads')
check(len(M.hypotheses)>=7,'seven or more hypotheses')
check(any(len(v)>1 for v in M.evidence_links.values()),'evidence can connect mystery threads')
r=M.runtime_defaults(); check(all(p['status']=='unopened' for p in r['mystery_progress'].values()),'threads begin unopened')
r['observations']['farm_boundary_discrepancy']={'id':'farm_boundary_discrepancy'}
for mid in M.links_for_evidence('farm_boundary_discrepancy'): r['mystery_progress'][mid]['evidence'].append('farm_boundary_discrepancy')
M.refresh(r); check(r['mystery_progress']['land_boundaries']['status']=='active','evidence activates linked mystery')
check(r['mystery_progress']['records_disagree']['status']=='active','shared evidence activates second mystery')
check(bool(r['connections']),'active related mysteries create connection')
g=Game(); g.migrate_state(); check('mystery_overview' in g.view()['state'],'public state includes mystery overview')
check(g.record_evidence('farm_boundary_discrepancy','Boundary','A wall and fence disagree.',location='calder_farm'),'new evidence records')
check(not g.record_evidence('farm_boundary_discrepancy','Boundary','duplicate',location='calder_farm'),'duplicate evidence rejected')
res=g.assess_hypothesis('boundaries_have_shifted'); check(res and res['status']=='tentative','partial support remains tentative')
check(M.validate(),'catalogue validates')
print('v0.8.0 diagnostic: 12/12 PASS')
