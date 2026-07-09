"""Bellwether economy substrate.

v0.4.1 adds a persistent village market layer on top of the existing authoritative
catalogue and transaction ledger. Business pressure, demand and stock recovery are
bounded deterministic state; future Directors may propose pressure changes through
validators without directly editing money or inventory.
"""
from copy import deepcopy

ITEMS = {
 "radish_seed": {"name":"Radish seed packet","price":2,"kind":"seed","crop_id":"radish","seed_units":3},
 "lettuce_seed": {"name":"Lettuce seed packet","price":2,"kind":"seed","crop_id":"lettuce","seed_units":3},
 "carrot_seed": {"name":"Carrot seed packet","price":3,"kind":"seed","crop_id":"carrot","seed_units":3},
 "broad_bean_seed": {"name":"Broad bean seed packet","price":3,"kind":"seed","crop_id":"broad_bean","seed_units":3},
 "groceries": {"name":"Basic groceries","price":4,"kind":"household","units":3},
 "tea": {"name":"Tea","price":2,"kind":"household","units":4},
 "cleaning_supplies": {"name":"Cleaning supplies","price":3,"kind":"household","units":2},
 "repair_supplies": {"name":"Basic repair supplies","price":5,"kind":"repair","units":1},
 "bakery_breakfast": {"name":"Warm bakery breakfast","price":2,"kind":"meal","units":1},
 "bread_loaf": {"name":"Fresh loaf","price":2,"kind":"food","units":2},
}
PRODUCE_VALUES={"radish":1,"lettuce":2,"carrot":1,"broad_bean":1}
SHOPS={
 "village_shop":{"name":"Village Shop","location":"village_shop","stock":["radish_seed","lettuce_seed","carrot_seed","broad_bean_seed","groceries","tea","cleaning_supplies","repair_supplies"],"buys_produce":True},
 "bakery":{"name":"Bellwether Bakery","location":"bakery","stock":["bakery_breakfast","bread_loaf"],"buys_produce":False},
}

class EconomyModel:
 def runtime_defaults(self):
  return {
   "schema_version":2,
   "ledger":[],
   "household":{"groceries":2,"tea":3,"cleaning_supplies":1,"repair_supplies":0},
   "shop_stock":{sid:{iid:99 for iid in shop["stock"]} for sid,shop in SHOPS.items()},
   "daily_costs":{"last_charged_day":0,"heating_due":0,"maintenance_due":0},
   "total_earned":0,"total_spent":0,
   "market":{"last_tick_day":0,"produce_demand":{crop:1.0 for crop in PRODUCE_VALUES},
             "businesses":{sid:{"pressure":0,"trend":"steady","sales":0,"purchases":0,"last_change_day":0} for sid in SHOPS},
             "history":[]},
  }
 def migrate(self,state):
  e=state.setdefault("economy",self.runtime_defaults()); defaults=self.runtime_defaults()
  for k,v in defaults.items(): e.setdefault(k,deepcopy(v))
  e["schema_version"]=2
  market=e.setdefault("market",deepcopy(defaults["market"]))
  market.setdefault("last_tick_day",0); market.setdefault("produce_demand",{crop:1.0 for crop in PRODUCE_VALUES}); market.setdefault("history",[])
  for crop in PRODUCE_VALUES: market["produce_demand"].setdefault(crop,1.0)
  businesses=market.setdefault("businesses",{})
  for sid in SHOPS:
   b=businesses.setdefault(sid,{"pressure":0,"trend":"steady","sales":0,"purchases":0,"last_change_day":0})
   for k,v in {"pressure":0,"trend":"steady","sales":0,"purchases":0,"last_change_day":0}.items(): b.setdefault(k,v)
  for sid,shop in SHOPS.items():
   stock=e.setdefault("shop_stock",{}).setdefault(sid,{})
   for iid in shop["stock"]: stock.setdefault(iid,99)
  return e
 def shop_for_location(self, loc):
  for sid,shop in SHOPS.items():
   if shop["location"]==loc:return sid
  return None
 def record(self,state,kind,amount,reason):
  e=self.migrate(state); e["ledger"].append({"day":state.get("day",1),"minute":state.get("minute",0),"kind":kind,"amount":amount,"reason":reason}); e["ledger"]=e["ledger"][-120:]
  if amount<0:e["total_spent"]+=-amount
  else:e["total_earned"]+=amount
 def price(self,state,shop_id,item_id):
  """Stable catalogue price with only bounded business-pressure adjustment."""
  base=ITEMS[item_id]["price"]; pressure=self.migrate(state)["market"]["businesses"][shop_id]["pressure"]
  # Pressure affects ordinary retail mildly; never more than +50%, and minimum Br 1.
  return max(1, round(base*(1.0 + max(0,pressure)*0.05)))
 def produce_price(self,state,crop_id):
  demand=self.migrate(state)["market"]["produce_demand"].get(crop_id,1.0)
  return max(1,round(PRODUCE_VALUES[crop_id]*demand))
 def buy(self,state,shop_id,item_id):
  if shop_id not in SHOPS or item_id not in SHOPS[shop_id]["stock"]: return False,"That is not sold here."
  item=ITEMS[item_id]; e=self.migrate(state); price=self.price(state,shop_id,item_id)
  if e["shop_stock"].setdefault(shop_id,{}).get(item_id,0)<=0:return False,"It is out of stock."
  if state.get("money",0)<price:return False,"You cannot afford that."
  state["money"]-=price; e["shop_stock"][shop_id][item_id]-=1; e["market"]["businesses"][shop_id]["sales"]+=1
  if item["kind"]=="seed":
   g=state["player_activities"]["garden"]; g["seed_stock"][item["crop_id"]]=g["seed_stock"].get(item["crop_id"],0)+item["seed_units"]
  elif item["kind"] in {"household","repair","food"}: e["household"][item_id]=e["household"].get(item_id,0)+item.get("units",1)
  elif item["kind"]=="meal": state["player_life"]["meals"]+=1
  self.record(state,"purchase",-price,item_id); return True,f"You buy {item['name'].lower()} for Br {price}."
 def sell_produce(self,state,crop_id,quantity=None):
  store=state["player_activities"]["garden"]["harvest_store"]; have=int(store.get(crop_id,0)); qty=have if quantity is None else min(have,max(0,int(quantity)))
  if qty<=0 or crop_id not in PRODUCE_VALUES:return False,"You have none of that produce to sell."
  unit=self.produce_price(state,crop_id); earned=qty*unit; store[crop_id]=have-qty; state["money"]+=earned
  e=self.migrate(state); e["market"]["businesses"]["village_shop"]["purchases"]+=qty
  # Selling into local demand gently cools that demand, preventing infinite price escalation.
  e["market"]["produce_demand"][crop_id]=max(0.75,round(e["market"]["produce_demand"][crop_id]-min(0.2,qty*0.02),2))
  self.record(state,"sale",earned,f"{crop_id}:{qty}@{unit}"); return True,f"The shop takes {qty} {crop_id.replace('_',' ')} for Br {earned}."
 def daily_tick(self,state):
  """Advance bounded local market conditions once per in-game day."""
  e=self.migrate(state); market=e["market"]; day=int(state.get("day",1))
  if market.get("last_tick_day",0)>=day:return None
  market["last_tick_day"]=day
  weather=state.get("weather",{}).get("state",""); season=state.get("season",{}).get("id","")
  # Demand rotates deterministically by calendar so the market changes without RNG or AI hallucination.
  crops=list(PRODUCE_VALUES); fav=crops[(day-1)%len(crops)]
  for crop in crops:
   d=market["produce_demand"].get(crop,1.0)
   target=1.5 if crop==fav else 1.0
   market["produce_demand"][crop]=round(max(0.75,min(1.75,d+(target-d)*0.35)),2)
  for sid,shop in SHOPS.items():
   b=market["businesses"][sid]; stock=e["shop_stock"][sid]
   low=sum(1 for iid in shop["stock"] if stock.get(iid,0)<=2)
   runtime_signal=state.get("world_runtime",{}).get("economy_signals",{})
   weather_strain=max(1 if weather in {"heavy_rain","storm","snow"} else 0, int(runtime_signal.get("delivery_disruption",0)))
   b["pressure"]=max(0,min(8,low+weather_strain))
   b["trend"]="strained" if b["pressure"]>=4 else ("watchful" if b["pressure"]>=2 else "steady")
   b["last_change_day"]=day
   # Deliveries recover stock gradually. Severe weather halves the normal delivery size.
   delivery=1 if weather_strain>=1 else 3
   for iid in shop["stock"]: stock[iid]=min(99,stock.get(iid,0)+delivery)
  snap={"day":day,"favoured_produce":fav,"business_trends":{sid:b["trend"] for sid,b in market["businesses"].items()}}
  market["history"].append(snap); market["history"]=market["history"][-30:]
  return snap
 def actions(self,state):
  sid=self.shop_for_location(state.get("location")); out=[]
  if sid:
   for iid in SHOPS[sid]["stock"]:
    item=ITEMS[iid]; price=self.price(state,sid,iid); out.append((f"economy:buy:{sid}:{iid}",f"Buy {item['name']} (Br {price})"))
   if SHOPS[sid]["buys_produce"]:
    for crop,qty in state.get("player_activities",{}).get("garden",{}).get("harvest_store",{}).items():
     if qty>0: out.append((f"economy:sell:{crop}",f"Sell all {crop.replace('_',' ').title()} ({qty}, Br {self.produce_price(state,crop)}/unit)"))
  return out
ECONOMY_MODEL=EconomyModel()
