from copy import deepcopy
from backend.core.game import INITIAL_STATE, Game
from backend.core.interface_horror_model import INTERFACE_HORROR_MODEL

def check(name, cond):
    if not cond: raise AssertionError(name)
    print('PASS', name)

s=deepcopy(INITIAL_STATE); INTERFACE_HORROR_MODEL.migrate(s)
check('inactive by default', not INTERFACE_HORROR_MODEL.resolve(s)['active'])
s['location']='village_green'; s['systemic_horror']['active_overlays']['village_green']={'anomaly_id':'green_path_mismatch','kind':'spatial_misalignment','strength':1,'pulse':2}
r=INTERFACE_HORROR_MODEL.resolve(s)
check('map contradiction derives from legal overlay', r['effects']==['map_contradiction'])
check('resolver does not mutate map graph', s['map_exploration']==INITIAL_STATE['map_exploration'])
check('effect provenance retained', r['source']=='green_path_mismatch')
check('presentation log auditable', bool(s['interface_horror']['presentation_log']))
s['systemic_horror']['active_overlays'].clear()
check('effect expires with source overlay', not INTERFACE_HORROR_MODEL.resolve(s)['active'])
s['location']='village_shop'; s['systemic_horror']['active_overlays']['village_shop']={'anomaly_id':'shop_labels_repeat','kind':'textual_repetition','strength':2,'pulse':3}
r=INTERFACE_HORROR_MODEL.resolve(s)
check('strong effect bounded to two effects', len(r['effects'])<=2)
check('journal inconsistency is eligible presentation effect', 'journal_inconsistency' in r['effects'])
check('authority explicitly presentation-only', INTERFACE_HORROR_MODEL.developer_context(s)['authority']=='presentation_only')
g=Game(); v=g.view()
check('public view exposes bounded presentation state', 'presentation_horror' in v['state'])
check('developer/settings button preserved', 'dev-button' in open('frontend/templates/index.html').read())
js=open('frontend/static/js/game.js').read()
check('map contradiction renderer present', 'map-ghost-contradiction' in js)
check('journal display contradiction renderer present', 'displayOnlyJournalEcho' in js)
check('reduced motion handling present', 'prefers-reduced-motion' in open('frontend/static/css/game.css').read())
print('v0.8.4 interface horror diagnostic: 14/14 PASS')
