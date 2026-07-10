from copy import deepcopy
import json
from backend.core.game import Game
from backend.core.property_model import PROPERTY_MODEL

def check(name, ok, detail=''):
    print(('PASS' if ok else 'FAIL'), name, detail)
    return bool(ok)

r=[]; g=Game(); s=g.state; g.migrate_state(); s['money']=250
r.append(check('property state migrated','property' in s and 'ashcroft_cottage' in s['property']['owned']))
s['location']='field_lane'; ids={a['id'] for a in g.actions()}; r.append(check('meadow lease public action','property:acquire:meadow_lease' in ids))
before=len(s['player_activities']['garden']['plots']); money=s['money']; g.perform('property:acquire:meadow_lease')
r.append(check('lease authoritative','meadow_lease' in s['property']['leases']))
r.append(check('land expands existing garden',len(s['player_activities']['garden']['plots'])==before+2))
r.append(check('acquisition costs money',s['money']==money-12))
s['day']=2; money=s['money']; tick=PROPERTY_MODEL.daily_tick(s); r.append(check('lease rent charged',tick['due']==1 and s['money']==money-1))
s['location']='ashcroft_cottage'; s['player_status']['cottage']['condition']=90; s['economy']['household']['repair_supplies']=10
ids={a['id'] for a in g.actions()}; r.append(check('cottage expansion public action','property:expand:pantry_room' in ids))
g.perform('property:expand:pantry_room'); r.append(check('expansion persists','pantry_room' in s['property']['expansions']))
ids={a['id'] for a in g.actions()}; r.append(check('ordered expansion progression','property:expand:work_room' in ids and 'property:expand:upper_room' not in ids))
roundtrip=json.loads(json.dumps(s)); r.append(check('save roundtrip',roundtrip['property']==s['property']))
view=g.view(); r.append(check('public property overview',view['state']['property_overview']['garden_plot_capacity']==5))
print(f'{sum(r)}/{len(r)} PASS'); raise SystemExit(0 if all(r) else 1)
