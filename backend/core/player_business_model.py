"""v2.2.0 player enterprise ownership and operation.

Builds on authoritative property, economy, garden, pantry and population state. It does
not replace village businesses: player enterprises are small rural ventures with manual
and manager-operated modes, staff costs, stock inputs, reputation and failure pressure.
"""
from copy import deepcopy

ENTERPRISES={
 "produce_stall":{"name":"Bellwether Produce Stall","location":"village_green","startup":28,"requires_property":None,"input":"garden_produce","units":3,"base_revenue":7,"minutes":90},
 "preserve_kitchen":{"name":"Ashcroft Preserves","location":"ashcroft_cottage","startup":45,"requires_expansion":"work_room","input":"preserve","units":1,"base_revenue":9,"minutes":120},
 "repair_workshop":{"name":"Yard Repair Workshop","location":"workshop_yard","startup":60,"requires_property":"workshop_lease","input":"repair_supplies","units":1,"base_revenue":11,"minutes":150},
}

class PlayerBusinessModel:
 schema_version=2
 def runtime_defaults(self):
  return {"schema_version":2,"enterprises":{},"history":[],"total_profit":0,"total_losses":0,"last_daily_tick":0}
 def migrate(self,state):
  rt=state.setdefault("player_businesses",self.runtime_defaults());d=self.runtime_defaults()
  for k,v in d.items():rt.setdefault(k,deepcopy(v))
  rt["schema_version"]=self.schema_version
  for bid,b in rt["enterprises"].items():
   b.setdefault("mode","owner_operated");b.setdefault("cash",20);b.setdefault("reputation",50);b.setdefault("health",70);b.setdefault("staff",0);b.setdefault("wage",4);b.setdefault("sales",0);b.setdefault("days_owned",0);b.setdefault("consecutive_losses",0);b.setdefault("closed",False);b.setdefault("stock",0);b.setdefault("stock_capacity",8);b.setdefault("prepared_batches",0);b.setdefault("deliveries",0);b.setdefault("missed_sales",0)
  return rt
 def _record(self,state,kind,bid,amount=0,detail=None):
  rt=self.migrate(state);rt["history"].append({"day":state.get("day",1),"minute":state.get("minute",0),"kind":kind,"business":bid,"amount":amount,"detail":detail});rt["history"]=rt["history"][-120:]
  state.setdefault("economy",{}).setdefault("ledger",[]).append({"day":state.get("day",1),"minute":state.get("minute",0),"kind":"player_business_"+kind,"amount":amount,"reason":bid,"business":"player:"+bid})
 def _eligible(self,state,bid):
  spec=ENTERPRISES[bid];prop=state.get("property",{})
  if spec.get("requires_property") and spec["requires_property"] not in prop.get("owned",{}) and spec["requires_property"] not in prop.get("leases",{}):return False,"You need control of the required workspace first."
  if spec.get("requires_expansion") and spec["requires_expansion"] not in prop.get("expansions",[]):return False,"The cottage needs the required work space first."
  return True,""
 def actions(self,state):
  rt=self.migrate(state);loc=state.get("location");out=[]
  for bid,spec in ENTERPRISES.items():
   if bid not in rt["enterprises"] and loc==spec["location"]:
    ok,_=self._eligible(state,bid)
    if ok:out.append((f"business:start:{bid}",f"Start {spec['name']} (฿{spec['startup']})"))
  for bid,b in rt["enterprises"].items():
   spec=ENTERPRISES[bid]
   if loc!=spec["location"] or b.get("closed"):continue
   if b["mode"]=="owner_operated":
    out.append((f"business:prepare:{bid}",f"Prepare stock for {spec['name']}"))
    if b.get("stock",0)>0: out.append((f"business:operate:{bid}",f"Open {spec['name']} for customers"))
   out.append((f"business:mode:{bid}","Switch to manager-operated mode" if b["mode"]=="owner_operated" else "Return to owner-operated mode"))
   if b["mode"]=="manager_operated":
    if b["staff"]<1:out.append((f"business:hire:{bid}",f"Hire a local manager (฿{b['wage']}/day)"))
    else:out.append((f"business:fire:{bid}","End the manager arrangement"))
   if b["cash"]<12 and state.get("money",0)>=10:out.append((f"business:invest:{bid}","Invest ฿10 in the business"))
  return out
 def _consume_input(self,state,bid):
  spec=ENTERPRISES[bid];kind=spec["input"];need=spec["units"]
  if kind=="garden_produce":
   store=state.get("player_activities",{}).get("garden",{}).get("harvest_store",{})
   available=[k for k,v in store.items() if v>0]
   if sum(store.values())<need:return False,"You need at least three units of harvested produce."
   left=need
   for crop in available:
    take=min(left,store[crop]);store[crop]-=take;left-=take
    if left<=0:break
   return True,""
  if kind=="preserve":
   pantry=state.get("life_simulation",{}).get("pantry",{}).get("preserves",{})
   item=next((k for k,v in pantry.items() if v>=need),None)
   if not item:return False,"You need a prepared preserve in the pantry."
   pantry[item]-=need;return True,""
  if kind=="repair_supplies":
   house=state.get("economy",{}).get("household",{})
   if house.get("repair_supplies",0)<need:return False,"You need repair supplies for workshop jobs."
   house["repair_supplies"]-=need;return True,""
  return False,"The enterprise has no usable input path."
 def perform(self,state,action):
  parts=action.split(":");rt=self.migrate(state)
  if len(parts)!=3 or parts[0]!="business":return False,"Nothing happens.",0
  verb,bid=parts[1],parts[2]
  if bid not in ENTERPRISES:return False,"That enterprise does not exist.",0
  spec=ENTERPRISES[bid]
  if state.get("location")!=spec["location"]:return False,"You need to handle that business in person.",0
  if verb=="start":
   if bid in rt["enterprises"]:return False,"You already own that enterprise.",0
   ok,msg=self._eligible(state,bid)
   if not ok:return False,msg,0
   if state.get("money",0)<spec["startup"]:return False,"You cannot afford the startup costs.",0
   state["money"]-=spec["startup"];rt["enterprises"][bid]={"mode":"owner_operated","cash":20,"reputation":50,"health":70,"staff":0,"wage":4,"sales":0,"days_owned":0,"consecutive_losses":0,"closed":False,"stock":0,"stock_capacity":8,"prepared_batches":0,"deliveries":0,"missed_sales":0}
   self._record(state,"startup",bid,-spec["startup"]);return True,f"You establish {spec['name']}. It is small, but it is yours to run.",180
  b=rt["enterprises"].get(bid)
  if not b:return False,"You do not own that enterprise.",0
  if verb=="prepare":
   if b["closed"]:return False,"The business is closed and needs recovery capital.",0
   if b.get("stock",0)>=b.get("stock_capacity",8):return False,"The business already has as much prepared stock as it can hold.",0
   ok,msg=self._consume_input(state,bid)
   if not ok:return False,msg,0
   cargo=state.get("transport_overview",{}).get("cargo_capacity") or 2
   batch=2 if cargo>=7 else 1
   batch=min(batch,b.get("stock_capacity",8)-b.get("stock",0));b["stock"]+=batch;b["prepared_batches"]+=1
   self._record(state,"stock_prepared",bid,0,{"units":batch});return True,f"You prepare {batch} sale unit{'s' if batch!=1 else ''} for {spec['name']}. Stock is now {b['stock']}/{b['stock_capacity']}.",max(45,spec["minutes"]//2)
  if verb=="operate":
   if b["closed"]:return False,"The business is closed and needs recovery capital.",0
   if b.get("stock",0)<=0:return False,"There is no prepared stock to sell. Prepare stock first.",0
   outlook=state.get("economy",{}).get("market",{}).get("village_outlook","stable");factor=.8 if outlook=="fragile" else .9 if outlook=="uneasy" else 1.0
   units=min(b["stock"],2 if b["reputation"]>=65 else 1);revenue=max(1,round(spec["base_revenue"]*factor*(.75+b["reputation"]/200)*units));b["stock"]-=units;b["cash"]+=revenue;b["sales"]+=units;b["reputation"]=min(100,b["reputation"]+1);b["health"]=min(100,b["health"]+1);rt["total_profit"]+=revenue;self._record(state,"sale",bid,revenue,{"units":units})
   return True,f"You open {spec['name']} for customers and sell {units} unit{'s' if units!=1 else ''}, taking ฿{revenue}. {b['stock']} prepared stock remains.",spec["minutes"]
  if verb=="mode":
   b["mode"]="manager_operated" if b["mode"]=="owner_operated" else "owner_operated";self._record(state,"mode",bid,0,b["mode"]);return True,f"{spec['name']} is now {b['mode'].replace('_',' ')}.",20
  if verb=="hire":
   if b["mode"]!="manager_operated":return False,"Switch the business to manager-operated mode first.",0
   if b["staff"]:return False,"A manager is already employed.",0
   b["staff"]=1;self._record(state,"hire",bid,0);return True,"You hire a local manager. Their wage will be paid from business cash each day.",30
  if verb=="fire":b["staff"]=0;self._record(state,"staff_end",bid,0);return True,"You end the manager arrangement.",20
  if verb=="invest":
   if state.get("money",0)<10:return False,"You cannot spare ฿10.",0
   state["money"]-=10;b["cash"]+=10;b["health"]=min(100,b["health"]+5);self._record(state,"investment",bid,-10);return True,"You put ฿10 of personal money into the business.",15
  return False,"Nothing happens.",0
 def daily_tick(self,state):
  rt=self.migrate(state);day=int(state.get("day",1))
  if rt["last_daily_tick"]>=day:return None
  rt["last_daily_tick"]=day;results=[]
  for bid,b in rt["enterprises"].items():
   b["days_owned"]+=1
   if b["closed"]:continue
   cost=2+(b["wage"] if b["staff"] else 0);income=0
   if b["mode"]=="manager_operated" and b["staff"]:
    if b.get("stock",0)>0:
     outlook=state.get("economy",{}).get("market",{}).get("village_outlook","stable");income=max(0,round(ENTERPRISES[bid]["base_revenue"]*(.45 if outlook=="fragile" else .65)));b["stock"]-=1;b["sales"]+=1
    else:
     b["missed_sales"]+=1
   net=income-cost;b["cash"]+=net
   if net<0:rt["total_losses"]+=-net;b["consecutive_losses"]+=1
   else:rt["total_profit"]+=net;b["consecutive_losses"]=0
   b["health"]=max(0,min(100,b["health"]+(1 if net>=0 else -2)))
   if b["cash"]<0 or b["health"]<=5:b["closed"]=True
   self._record(state,"daily_result",bid,net,{"income":income,"cost":cost,"closed":b["closed"]});results.append({"business":bid,"net":net,"closed":b["closed"]})
  return results
 def public(self,state):
  rt=self.migrate(state);return {"enterprises":deepcopy(rt["enterprises"]),"total_profit":rt["total_profit"],"total_losses":rt["total_losses"],"history":deepcopy(rt["history"][-12:])}

PLAYER_BUSINESS_MODEL=PlayerBusinessModel()
