"""Player transport ownership and rural mobility for Bellwether v2.3.0.

Travel topology remains authoritative in WORLD/TRAVEL_MODEL. This model owns player
vehicles, active travel mode, fuel, condition, cargo capacity and breakdown state.
"""
from copy import deepcopy

VEHICLES={
 'bicycle':{'name':'second-hand bicycle','price':45,'speed':0.72,'fuel_capacity':0,'fuel_per_journey':0,'cargo':4,'wear':0.7},
 'motorbike':{'name':'used motorbike','price':180,'speed':0.48,'fuel_capacity':12,'fuel_per_journey':1,'cargo':7,'wear':1.0},
 'car':{'name':'small used car','price':420,'speed':0.38,'fuel_capacity':24,'fuel_per_journey':2,'cargo':12,'wear':1.1},
 'van':{'name':'working van','price':650,'speed':0.42,'fuel_capacity':32,'fuel_per_journey':3,'cargo':24,'wear':1.3},
}
class TransportModel:
 schema_version=1
 def runtime_defaults(self): return {'schema_version':1,'owned':{},'active':'walk','journeys':0,'fuel_spent':0,'maintenance_spent':0,'breakdowns':0,'history':[]}
 def migrate(self,state):
  rt=state.setdefault('transport',self.runtime_defaults())
  for k,v in self.runtime_defaults().items(): rt.setdefault(k,deepcopy(v))
  if rt.get('active')!='walk' and rt.get('active') not in rt['owned']: rt['active']='walk'
  return rt
 def actions(self,state):
  rt=self.migrate(state); out=[]; loc=state.get('location')
  if loc=='village_shop':
   for vid,v in VEHICLES.items():
    if vid not in rt['owned']: out.append((f'transport:buy:{vid}',f"Buy {v['name']} (฿{v['price']})"))
   fuel_users=[x for x in rt['owned'] if VEHICLES[x]['fuel_capacity']]
   if fuel_users: out.append(('transport:fuel:active','Buy fuel for active vehicle (฿3/unit)'))
  if loc in {'ashcroft_cottage','workshop_yard','village_road','village_green'}:
   out.append(('transport:select:walk','Travel on foot'))
   for vid in rt['owned']: out.append((f'transport:select:{vid}',f"Use {VEHICLES[vid]['name']} for travel"))
  if loc=='workshop_yard':
   for vid,d in rt['owned'].items():
    if d.get('condition',100)<95: out.append((f'transport:service:{vid}',f"Service {VEHICLES[vid]['name']} (฿{max(5,int((100-d.get('condition',100))*.6))})"))
  return out
 def perform(self,state,action):
  p=action.split(':'); rt=self.migrate(state)
  if len(p)!=3 or p[0]!='transport': return False,'Nothing happens.',0
  kind,asset=p[1],p[2]
  if kind=='buy' and asset in VEHICLES:
   v=VEHICLES[asset]
   if asset in rt['owned']: return False,'You already own that vehicle.',0
   if state.get('money',0)<v['price']: return False,'You cannot afford that vehicle yet.',0
   state['money']-=v['price']; rt['owned'][asset]={'condition':100.0,'fuel':v['fuel_capacity'],'broken':False,'acquired_day':state.get('day',1)}; rt['active']=asset
   self._record(state,'purchase',asset,-v['price']); return True,f"You buy the {v['name']}. It is now your active travel mode.",45
  if kind=='select':
   if asset!='walk' and asset not in rt['owned']: return False,'You do not own that vehicle.',0
   if asset!='walk' and rt['owned'][asset].get('broken'): return False,'That vehicle needs repair before it can be used.',0
   rt['active']=asset; return True,('You will travel on foot.' if asset=='walk' else f"You will use the {VEHICLES[asset]['name']} for journeys."),5
  if kind=='fuel' and asset=='active':
   vid=rt.get('active'); d=rt['owned'].get(vid); v=VEHICLES.get(vid)
   if not d or not v or not v['fuel_capacity']: return False,'Your active travel mode does not need fuel.',0
   room=v['fuel_capacity']-int(d.get('fuel',0)); qty=min(room,state.get('money',0)//3)
   if qty<=0:return False,'You cannot add fuel right now.',0
   cost=qty*3; state['money']-=cost; d['fuel']+=qty; rt['fuel_spent']+=cost; self._record(state,'fuel',vid,-cost); return True,f"You add {qty} fuel units to the {v['name']}.",15
  if kind=='service' and asset in rt['owned']:
   d=rt['owned'][asset]; cost=max(5,int((100-d.get('condition',100))*.6))
   if state.get('money',0)<cost:return False,'You cannot afford the service.',0
   state['money']-=cost; d['condition']=100.0; d['broken']=False; rt['maintenance_spent']+=cost; self._record(state,'service',asset,-cost); return True,f"The {VEHICLES[asset]['name']} is serviced and ready for the road.",60
  return False,'Nothing happens.',0
 def journey_modifier(self,state):
  rt=self.migrate(state); vid=rt.get('active','walk')
  if vid=='walk': return {'mode':'walk','multiplier':1.0,'cargo':2}
  d=rt['owned'].get(vid); v=VEHICLES.get(vid)
  if not d or d.get('broken'): return {'mode':'walk','multiplier':1.0,'cargo':2}
  need=v['fuel_per_journey']
  if need and d.get('fuel',0)<need: return {'mode':'walk','multiplier':1.0,'cargo':2,'fallback_reason':'out_of_fuel'}
  return {'mode':vid,'multiplier':v['speed'],'cargo':v['cargo']}
 def complete_journey(self,state,minutes):
  rt=self.migrate(state); mod=self.journey_modifier(state); vid=mod['mode']; rt['journeys']+=1
  if vid=='walk': return mod
  d=rt['owned'][vid]; v=VEHICLES[vid]; d['fuel']=max(0,d.get('fuel',0)-v['fuel_per_journey']); d['condition']=max(0,round(d.get('condition',100)-v['wear'],1))
  if d['condition']<=15: d['broken']=True; rt['breakdowns']+=1
  self._record(state,'journey',vid,0); return mod
 def _record(self,state,kind,asset,amount):
  rt=self.migrate(state); rt['history'].append({'day':state.get('day',1),'minute':state.get('minute',0),'kind':kind,'asset':asset,'amount':amount}); rt['history']=rt['history'][-100:]
  state.setdefault('economy',{}).setdefault('ledger',[]).append({'day':state.get('day',1),'minute':state.get('minute',0),'kind':'transport_'+kind,'amount':amount,'reason':asset,'business':None})
 def public(self,state):
  rt=self.migrate(state); mod=self.journey_modifier(state)
  return {'active':rt['active'],'effective_mode':mod['mode'],'owned':deepcopy(rt['owned']),'cargo_capacity':mod['cargo'],'journeys':rt['journeys'],'breakdowns':rt['breakdowns']}
TRANSPORT_MODEL=TransportModel()
