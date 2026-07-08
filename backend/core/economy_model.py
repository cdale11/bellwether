"""Part 5 economy, shops and services substrate.

Authoritative prices/catalogue are separate from mutable stock, ledger and household state.
Part 6 jobs can provide regular income without replacing this model.
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
  return {"schema_version":1,"ledger":[],"household":{"groceries":2,"tea":3,"cleaning_supplies":1,"repair_supplies":0},"shop_stock":{sid:{iid:99 for iid in shop["stock"]} for sid,shop in SHOPS.items()},"daily_costs":{"last_charged_day":0,"heating_due":0,"maintenance_due":0},"total_earned":0,"total_spent":0}
 def shop_for_location(self, loc):
  for sid,shop in SHOPS.items():
   if shop["location"]==loc:return sid
  return None
 def record(self,state,kind,amount,reason):
  e=state.setdefault("economy",self.runtime_defaults()); e["ledger"].append({"day":state.get("day",1),"minute":state.get("minute",0),"kind":kind,"amount":amount,"reason":reason}); e["ledger"]=e["ledger"][-80:]
  if amount<0:e["total_spent"]+=-amount
  else:e["total_earned"]+=amount
 def buy(self,state,shop_id,item_id):
  if shop_id not in SHOPS or item_id not in SHOPS[shop_id]["stock"]: return False,"That is not sold here."
  item=ITEMS[item_id]; e=state.setdefault("economy",self.runtime_defaults())
  if e["shop_stock"].setdefault(shop_id,{}).get(item_id,0)<=0:return False,"It is out of stock."
  if state.get("money",0)<item["price"]:return False,"You cannot afford that."
  state["money"]-=item["price"]; e["shop_stock"][shop_id][item_id]-=1
  if item["kind"]=="seed":
   g=state["player_activities"]["garden"]; g["seed_stock"][item["crop_id"]]=g["seed_stock"].get(item["crop_id"],0)+item["seed_units"]
  elif item["kind"] in {"household","repair","food"}: e["household"][item_id]=e["household"].get(item_id,0)+item.get("units",1)
  elif item["kind"]=="meal": state["player_life"]["meals"]+=1
  self.record(state,"purchase",-item["price"],item_id); return True,f"You buy {item['name'].lower()} for £{item['price']}."
 def sell_produce(self,state,crop_id,quantity=None):
  store=state["player_activities"]["garden"]["harvest_store"]; have=int(store.get(crop_id,0)); qty=have if quantity is None else min(have,max(0,int(quantity)))
  if qty<=0 or crop_id not in PRODUCE_VALUES:return False,"You have none of that produce to sell."
  earned=qty*PRODUCE_VALUES[crop_id]; store[crop_id]=have-qty; state["money"]+=earned; self.record(state,"sale",earned,f"{crop_id}:{qty}"); return True,f"The shop takes {qty} {crop_id.replace('_',' ')} for £{earned}."
 def actions(self,state):
  sid=self.shop_for_location(state.get("location")); out=[]
  if sid:
   for iid in SHOPS[sid]["stock"]:
    item=ITEMS[iid]; out.append((f"economy:buy:{sid}:{iid}",f"Buy {item['name']} (£{item['price']})"))
   if SHOPS[sid]["buys_produce"]:
    for crop,qty in state.get("player_activities",{}).get("garden",{}).get("harvest_store",{}).items():
     if qty>0: out.append((f"economy:sell:{crop}",f"Sell all {crop.replace('_',' ').title()} ({qty})"))
  return out
ECONOMY_MODEL=EconomyModel()
