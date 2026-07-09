"""Bellwether v1.1.0 economy and village-change simulation.

Money, stock, wages and accounting remain deterministic. AI may interpret conditions,
but cannot mint money or directly edit ledgers. Business health, supply, staffing,
demand and recovery evolve from authoritative state and visible player actions.
"""
from copy import deepcopy

ITEMS={
 "radish_seed":{"name":"Radish seed packet","price":2,"kind":"seed","crop_id":"radish","seed_units":3,"supply":"farm"},
 "lettuce_seed":{"name":"Lettuce seed packet","price":2,"kind":"seed","crop_id":"lettuce","seed_units":3,"supply":"farm"},
 "carrot_seed":{"name":"Carrot seed packet","price":3,"kind":"seed","crop_id":"carrot","seed_units":3,"supply":"farm"},
 "broad_bean_seed":{"name":"Broad bean seed packet","price":3,"kind":"seed","crop_id":"broad_bean","seed_units":3,"supply":"farm"},
 "groceries":{"name":"Basic groceries","price":4,"kind":"household","units":3,"supply":"wholesale"},
 "tea":{"name":"Tea","price":2,"kind":"household","units":4,"supply":"wholesale"},
 "cleaning_supplies":{"name":"Cleaning supplies","price":3,"kind":"household","units":2,"supply":"wholesale"},
 "repair_supplies":{"name":"Basic repair supplies","price":5,"kind":"repair","units":1,"supply":"hardware"},
 "bakery_breakfast":{"name":"Warm bakery breakfast","price":2,"kind":"meal","units":1,"supply":"flour"},
 "bread_loaf":{"name":"Fresh loaf","price":2,"kind":"food","units":2,"supply":"flour"},
}
PRODUCE_VALUES={"radish":1,"lettuce":2,"carrot":1,"broad_bean":1}
SHOPS={
 "village_shop":{"name":"Village Shop","location":"village_shop","stock":["radish_seed","lettuce_seed","carrot_seed","broad_bean_seed","groceries","tea","cleaning_supplies","repair_supplies"],"buys_produce":True},
 "bakery":{"name":"Bellwether Bakery","location":"bakery","stock":["bakery_breakfast","bread_loaf"],"buys_produce":False},
}

class EconomyModel:
 def _business(self):
  return {"health":72,"cash_reserve":60,"pressure":0,"trend":"steady","staffing":1.0,"supply":1.0,"demand":1.0,"reputation":0.65,"sales":0,"purchases":0,"daily_sales":0,"daily_purchases":0,"missed_sales":0,"last_change_day":0,"consecutive_strain":0,"player_support":0}
 def runtime_defaults(self):
  return {"schema_version":2,"ledger":[],"household":{"groceries":2,"tea":3,"cleaning_supplies":1,"repair_supplies":0},
   "shop_stock":{sid:{iid:99 for iid in shop["stock"]} for sid,shop in SHOPS.items()},
   "daily_costs":{"last_charged_day":0,"heating_due":0,"maintenance_due":0},"total_earned":0,"total_spent":0,
   "market":{"last_tick_day":0,"produce_demand":{c:1.0 for c in PRODUCE_VALUES},"businesses":{sid:self._business() for sid in SHOPS},"supply_routes":{"wholesale":1.0,"farm":1.0,"hardware":1.0,"flour":1.0},"village_outlook":"stable","history":[]},}
 def migrate(self,state):
  e=state.setdefault("economy",self.runtime_defaults()); d=self.runtime_defaults()
  for k,v in d.items(): e.setdefault(k,deepcopy(v))
  e["schema_version"]=2;m=e.setdefault("market",deepcopy(d["market"]))
  for k,v in d["market"].items():m.setdefault(k,deepcopy(v))
  for crop in PRODUCE_VALUES:m["produce_demand"].setdefault(crop,1.0)
  for sid in SHOPS:
   b=m["businesses"].setdefault(sid,self._business())
   for k,v in self._business().items():b.setdefault(k,v)
   stock=e.setdefault("shop_stock",{}).setdefault(sid,{})
   for iid in SHOPS[sid]["stock"]:stock.setdefault(iid,12)
  return e
 def shop_for_location(self,loc):
  return next((sid for sid,s in SHOPS.items() if s["location"]==loc),None)
 def record(self,state,kind,amount,reason,business=None):
  e=self.migrate(state);e["ledger"].append({"day":state.get("day",1),"minute":state.get("minute",0),"kind":kind,"amount":amount,"reason":reason,"business":business});e["ledger"]=e["ledger"][-240:]
  if amount<0:e["total_spent"]+=-amount
  else:e["total_earned"]+=amount
 def price(self,state,shop_id,item_id):
  base=ITEMS[item_id]["price"];b=self.migrate(state)["market"]["businesses"][shop_id]
  scarcity=max(0,1-float(b.get("supply",1)));pressure=float(b.get("pressure",0));demand=float(b.get("demand",1))
  factor=1+min(.45,scarcity*.25+pressure*.025+max(0,demand-1)*.2)
  return max(1,round(base*factor))
 def produce_price(self,state,crop_id):
  d=self.migrate(state)["market"]["produce_demand"].get(crop_id,1.0);return max(1,round(PRODUCE_VALUES[crop_id]*d))
 def business_open(self,state,sid):return self.migrate(state)["market"]["businesses"][sid]["health"]>8
 def buy(self,state,shop_id,item_id):
  if shop_id not in SHOPS or item_id not in SHOPS[shop_id]["stock"]:return False,"That is not sold here."
  e=self.migrate(state);b=e["market"]["businesses"][shop_id];price=self.price(state,shop_id,item_id);item=ITEMS[item_id]
  if not self.business_open(state,shop_id):return False,"The business is temporarily unable to trade."
  if e["shop_stock"][shop_id].get(item_id,0)<=0:b["missed_sales"]+=1;return False,"It is out of stock."
  if state.get("money",0)<price:return False,"You cannot afford that."
  state["money"]-=price;e["shop_stock"][shop_id][item_id]-=1;b["sales"]+=1;b["daily_sales"]+=1;b["cash_reserve"]=min(200,b["cash_reserve"]+price);b["health"]=min(100,b["health"]+.15)
  if item["kind"]=="seed":
   g=state["player_activities"]["garden"];g["seed_stock"][item["crop_id"]]=g["seed_stock"].get(item["crop_id"],0)+item["seed_units"]
  elif item["kind"] in {"household","repair","food"}:e["household"][item_id]=e["household"].get(item_id,0)+item.get("units",1)
  elif item["kind"]=="meal":state["player_life"]["meals"]+=1
  self.record(state,"purchase",-price,item_id,shop_id);return True,f"You buy {item['name'].lower()} for Br {price}."
 def sell_produce(self,state,crop_id,quantity=None):
  store=state["player_activities"]["garden"]["harvest_store"];have=int(store.get(crop_id,0));qty=have if quantity is None else min(have,max(0,int(quantity)))
  if qty<=0 or crop_id not in PRODUCE_VALUES:return False,"You have none of that produce to sell."
  unit=self.produce_price(state,crop_id);earned=qty*unit;store[crop_id]=have-qty;state["money"]+=earned;e=self.migrate(state);b=e["market"]["businesses"]["village_shop"];b["purchases"]+=qty;b["daily_purchases"]+=qty;b["cash_reserve"]=max(0,b["cash_reserve"]-earned);b["player_support"]+=min(3,qty*.1)
  e["market"]["produce_demand"][crop_id]=max(.75,round(e["market"]["produce_demand"][crop_id]-min(.2,qty*.02),2));self.record(state,"sale",earned,f"{crop_id}:{qty}@{unit}","village_shop");return True,f"The shop takes {qty} {crop_id.replace('_',' ')} for Br {earned}."
 def support_business(self,state,sid,amount=5):
  if sid not in SHOPS:return False,"There is no such business to support."
  amount=max(1,min(20,int(amount)));e=self.migrate(state)
  if state.get("money",0)<amount:return False,"You cannot spare that much."
  state["money"]-=amount;b=e["market"]["businesses"][sid];b["cash_reserve"]=min(200,b["cash_reserve"]+amount);b["health"]=min(100,b["health"]+amount*.35);b["player_support"]+=amount;self.record(state,"support",-amount,sid,sid);return True,f"You quietly put Br {amount} toward helping {SHOPS[sid]['name']} through the strain."
 def job_modifier(self,state,jid):
  sid="bakery" if jid=="bakery_helper" else "village_shop" if jid=="shop_assistant" else None
  if not sid:return {"available":True,"wage_factor":1.0,"reason":"community work"}
  b=self.migrate(state)["market"]["businesses"][sid];return {"available":b["health"]>15 and b["cash_reserve"]>3,"wage_factor":.85 if b["health"]<35 else 1.0,"reason":b["trend"]}
 def daily_tick(self,state):
  e=self.migrate(state);m=e["market"];day=int(state.get("day",1))
  if m.get("last_tick_day",0)>=day:return None
  m["last_tick_day"]=day;weather=state.get("weather",{}).get("state","");signals=state.get("world_runtime",{}).get("economy_signals",{});disruption=max(int(signals.get("delivery_disruption",0)),1 if weather in {"heavy_rain","storm","snow"} else 0)
  for route in m["supply_routes"]:
   target=max(.25,1-.28*disruption);m["supply_routes"][route]=round(max(.2,min(1.1,m["supply_routes"][route]+(target-m["supply_routes"][route])*.55)),2)
  crops=list(PRODUCE_VALUES);fav=crops[(day-1)%len(crops)]
  for crop in crops:
   d=m["produce_demand"].get(crop,1);target=1.5 if crop==fav else 1;m["produce_demand"][crop]=round(max(.75,min(1.75,d+(target-d)*.35)),2)
  changes=[]
  for sid,shop in SHOPS.items():
   b=m["businesses"][sid];stock=e["shop_stock"][sid];routes=[ITEMS[i]["supply"] for i in shop["stock"]];supply=sum(m["supply_routes"].get(r,1) for r in routes)/max(1,len(routes));b["supply"]=round(supply,2)
   demand=1+min(.35,b["daily_sales"]*.03);b["demand"]=round(demand,2);low=sum(1 for iid in shop["stock"] if stock.get(iid,0)<=2)
   operating=4+len(shop["stock"])*.15;b["cash_reserve"]=max(0,b["cash_reserve"]-operating);delivery=max(0,round(4*supply*b["staffing"]))
   for iid in shop["stock"]:stock[iid]=min(30,stock.get(iid,0)+delivery)
   strain=low*1.8+disruption*2+max(0,25-b["cash_reserve"])*.08+max(0,1-b["staffing"])*5
   recovery=min(2.5,b["daily_sales"]*.25+b["player_support"]*.03);b["health"]=round(max(0,min(100,b["health"]-strain*.45+recovery)),1);b["pressure"]=round(max(0,min(10,strain)),1)
   old=b.get("trend","steady");b["trend"]="critical" if b["health"]<20 else "strained" if b["health"]<45 else "watchful" if b["health"]<65 else "steady";b["consecutive_strain"]=b.get("consecutive_strain",0)+1 if b["trend"] in {"strained","critical"} else 0;b["last_change_day"]=day
   if old!=b["trend"]:changes.append({"business":sid,"from":old,"to":b["trend"]})
   b["daily_sales"]=0;b["daily_purchases"]=0
  avg=sum(b["health"] for b in m["businesses"].values())/len(m["businesses"]);m["village_outlook"]="fragile" if avg<35 else "uneasy" if avg<60 else "stable"
  snap={"day":day,"favoured_produce":fav,"business_trends":{sid:b["trend"] for sid,b in m["businesses"].items()},"business_health":{sid:b["health"] for sid,b in m["businesses"].items()},"supply_routes":deepcopy(m["supply_routes"]),"village_outlook":m["village_outlook"],"changes":changes};m["history"].append(snap);m["history"]=m["history"][-60:];return snap
 def actions(self,state):
  sid=self.shop_for_location(state.get("location"));out=[]
  if sid:
   for iid in SHOPS[sid]["stock"]:
    item=ITEMS[iid];out.append((f"economy:buy:{sid}:{iid}",f"Buy {item['name']} (Br {self.price(state,sid,iid)})"))
   if SHOPS[sid]["buys_produce"]:
    for crop,qty in state.get("player_activities",{}).get("garden",{}).get("harvest_store",{}).items():
     if qty>0:out.append((f"economy:sell:{crop}",f"Sell all {crop.replace('_',' ').title()} ({qty}, Br {self.produce_price(state,crop)}/unit)"))
   b=self.migrate(state)["market"]["businesses"][sid]
   if b["trend"] in {"strained","critical"}:out.append((f"economy:support:{sid}:5",f"Help {SHOPS[sid]['name']} through the strain (Br 5)"))
  return out
ECONOMY_MODEL=EconomyModel()
