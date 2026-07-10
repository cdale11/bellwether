"""v1.5.0 quest lifecycle, rewards, persistence and duplicate-award protection."""
from copy import deepcopy

DEFAULT_REWARDS={
 "arrival":{"money":0,"life_xp":4,"items":["Eleanor's garden notebook"]},
 "eleanor_letter":{"money":0,"life_xp":5,"items":["Eleanor's annotated village map"]},
 "first_morning":{"money":3,"life_xp":6},
 "jonah":{"money":2,"life_xp":4,"items":["Bakery token"]},
 "mara":{"money":0,"life_xp":6,"items":["Heritage seed packet"]},
}
class QuestModel:
 def migrate(self,state):
  rt=state.setdefault("quest_runtime",{"schema_version":1,"transactions":{},"history":[],"completion_checks":0})
  rt.setdefault("transactions",{});rt.setdefault("history",[]);rt.setdefault("completion_checks",0)
  for group in ("main","side"):
   for q in state.setdefault("quests",{}).setdefault(group,[]):
    q.setdefault("status","completed" if q.get("done") else "active")
    q.setdefault("reward",deepcopy(DEFAULT_REWARDS.get(q.get("id"),{})))
    q.setdefault("reward_applied",False)
  return rt
 def reward_for_arc(self,arc):
  domain=arc.get("domain")
  base={"money":4,"life_xp":6}
  if domain=="mystery":base["items"]=["Local history rubbing"]
  elif domain=="economy":base["money"]=7
  elif domain=="social":base["community"]=1
  return base
 def apply_reward(self,state,quest_key,reward):
  rt=self.migrate(state); tx=f"quest_reward:{quest_key}"
  if tx in rt["transactions"]:return False,rt["transactions"][tx]
  reward=deepcopy(reward or {}); state["money"]=int(state.get("money",0))+int(reward.get("money",0) or 0)
  inv=state.setdefault("inventory",[])
  for item in reward.get("items",[]) or []:
   if item not in inv:inv.append(item)
  xp=int(reward.get("life_xp",0) or 0)
  if xp:
   prog=state.setdefault("life_simulation",{}).setdefault("progression",{});prog["life_xp"]=int(prog.get("life_xp",0))+xp;prog["level"]=prog["life_xp"]//20
  community=int(reward.get("community",0) or 0)
  if community:state.setdefault("life_simulation",{}).setdefault("community",{})["participation"]=int(state["life_simulation"]["community"].get("participation",0))+community
  row={"transaction_id":tx,"day":state.get("day"),"minute":state.get("minute"),"reward":reward};rt["transactions"][tx]=row;rt["history"].append({"quest":quest_key,**row});rt["history"]=rt["history"][-100:]
  return True,row
 def complete(self,state,group,quest_id):
  rt=self.migrate(state);rt["completion_checks"]+=1
  q=next((x for x in state.get("quests",{}).get(group,[]) if x.get("id")==quest_id),None)
  if not q:return None
  if q.get("done") and q.get("reward_applied"):return {"newly_completed":False,"quest":q}
  newly=not q.get("done");q["done"]=True;q["status"]="completed";q.setdefault("completed_day",state.get("day"));q.setdefault("completed_minute",state.get("minute"))
  applied,row=self.apply_reward(state,f"{group}:{quest_id}",q.get("reward",{}));q["reward_applied"]=bool(q.get("reward_applied") or applied or f"quest_reward:{group}:{quest_id}" in rt["transactions"]);q["reward_transaction_id"]=f"quest_reward:{group}:{quest_id}"
  return {"newly_completed":newly,"reward_applied":applied,"quest":q,"transaction":row}
 def complete_arc(self,state,arc):
  key=f"arc:{arc.get('id')}";applied,row=self.apply_reward(state,key,arc.get("reward") or self.reward_for_arc(arc));arc["reward_applied"]=True;arc["reward_transaction_id"]=f"quest_reward:{key}";return applied,row
 def developer_context(self,state):
  rt=self.migrate(state); rows=[]
  for group in ("main","side"):
   for q in state.get("quests",{}).get(group,[]):rows.append({"id":q.get("id"),"group":group,"status":q.get("status"),"done":q.get("done"),"reward":q.get("reward"),"reward_applied":q.get("reward_applied"),"transaction":q.get("reward_transaction_id")})
  return {"quests":rows,"transactions":deepcopy(rt["transactions"]),"history":deepcopy(rt["history"][-30:]),"completion_checks":rt["completion_checks"]}
QUEST_MODEL=QuestModel()
