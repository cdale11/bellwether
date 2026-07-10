"""v1.0 RC3 persistent post-resolution village life."""
from copy import deepcopy

ENDING_EFFECTS={
 "incorporation":{"village_state":"The village feels unusually receptive to your routines.","economy_bias":"local","horror_tone":"intimate"},
 "false_escape":{"village_state":"Ordinary details sometimes arrive with the shape of somewhere else.","economy_bias":"uncertain","horror_tone":"displaced"},
 "rupture":{"village_state":"Repairs, absences and changed routes mark the cost of the rupture.","economy_bias":"rebuilding","horror_tone":"scarred"},
 "accommodation":{"village_state":"Life continues inside limits that are now understood, if never harmless.","economy_bias":"steady","horror_tone":"watchful"},
 "containment":{"village_state":"Maintenance has become a shared civic habit, quiet and deliberate.","economy_bias":"community","horror_tone":"bounded"},
 "liberation_coexistence":{"village_state":"Bellwether feels connected without feeling closed; staying is now recognisably a choice.","economy_bias":"open","horror_tone":"negotiated"},
}
class PostgameModel:
 def defaults(self): return {"schema_version":1,"active":False,"ending_id":None,"started_day":None,"days_lived":0,"legacy_points":0,"side_mystery_progress":0,"village_changes":[],"activity_counts":{}}
 def migrate(self,s):
  rt=s.setdefault("postgame",self.defaults())
  for k,v in self.defaults().items(): rt.setdefault(k,deepcopy(v))
  resolved=s.get("ending_families",{}).get("resolved")
  if resolved and not rt.get("active"): self.activate(s,resolved.get("id"))
  return rt
 def activate(self,s,ending_id):
  rt=s.setdefault("postgame",self.defaults()); rt.update({"active":True,"ending_id":ending_id,"started_day":s.get("day",1)})
  effect=ENDING_EFFECTS.get(ending_id,ENDING_EFFECTS["accommodation"]); rt["village_changes"]=[effect["village_state"]]
  s.setdefault("ambient",{})["postgame"]=effect["village_state"]; return rt
 def daily_tick(self,s):
  rt=self.migrate(s)
  if rt["active"]: rt["days_lived"]+=1
  return rt
 def record(self,s,kind):
  rt=self.migrate(s)
  if not rt["active"]: return False
  rt["activity_counts"][kind]=rt["activity_counts"].get(kind,0)+1; rt["legacy_points"]+=1
  if kind=="side_mystery": rt["side_mystery_progress"]=min(5,rt["side_mystery_progress"]+1)
  return True
 def actions(self,s):
  rt=self.migrate(s)
  if not rt["active"]: return []
  out=[("postgame:community","Help with the Village's Changed Routine"),("postgame:side_mystery","Follow a Remaining Loose End")]
  if s.get("location")=="ashcroft_cottage": out.append(("postgame:home","Work on the Life You Have Built Here"))
  return out
 def public(self,s):
  rt=self.migrate(s); effect=ENDING_EFFECTS.get(rt.get("ending_id"),{})
  return {**deepcopy(rt),"ending_effect":deepcopy(effect)}
POSTGAME_MODEL=PostgameModel()
