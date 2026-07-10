"""Bounded AI ecology pulse: climate-aware crop, vegetation and wildlife response."""
from copy import deepcopy

ECOLOGY_RESPONSES = [
 {"id":"dormant_shelter","label":"Dormancy and shelter dominate","crop_factor":0.12,"vegetation_delta":-0.02,"animal_mode":"sheltered"},
 {"id":"slow_stressed","label":"Growth is slow and wildlife movement is limited","crop_factor":0.35,"vegetation_delta":0.0,"animal_mode":"limited"},
 {"id":"steady_growth","label":"Conditions support steady growth and ordinary movement","crop_factor":0.75,"vegetation_delta":0.02,"animal_mode":"ordinary"},
 {"id":"vigorous_growth","label":"Warm moist conditions support vigorous growth and active wildlife","crop_factor":1.15,"vegetation_delta":0.05,"animal_mode":"active"},
 {"id":"dry_stress","label":"Drying conditions stress plants and concentrate animal movement near water","crop_factor":0.45,"vegetation_delta":-0.03,"animal_mode":"water_seeking"},
 {"id":"waterlogged","label":"Saturated ground slows crops while wildlife seeks firmer cover","crop_factor":0.30,"vegetation_delta":0.01,"animal_mode":"high_ground"},
]

ANIMAL_LOCATIONS={
 "sheltered":["north_woods","churchyard"],"limited":["north_woods","field_lane"],
 "ordinary":["field_lane","riverside_path","village_green"],"active":["village_green","field_lane","riverside_path"],
 "water_seeking":["riverside_path","ashcroft_cottage"],"high_ground":["north_woods","old_quarry"],
}

class EcologyAIModel:
 def defaults(self):
  return {"schema_version":1,"last_review_day":0,"source":"deterministic_baseline","crop_factor":0.65,"vegetation_index":0.5,"animal_mode":"ordinary","animal_locations":deepcopy(ANIMAL_LOCATIONS["ordinary"]),"wildlife_presence":{"robins":"ashcroft_cottage","rooks":"field_lane","pollinators":"village_green","small_mammals":"north_woods"},"history":[]}
 def migrate(self,state):
  rt=state.setdefault("ecology_ai",self.defaults())
  for k,v in self.defaults().items(): rt.setdefault(k,deepcopy(v))
  return rt
 def context(self,state):
  wr=state.get("world_runtime",{}).get("tendencies",{})
  garden=state.get("player_activities",{}).get("garden",{})
  return {"day":state.get("day"),"season":state.get("season",{}),"weather":state.get("weather",{}),
   "soil_saturation":round(float(wr.get("soil_saturation",.5)),3),"drying_pressure":round(float(wr.get("drying_pressure",0)),3),
   "wet_period":round(float(wr.get("wet_period",0)),3),"garden_moisture":garden.get("moisture",50),"garden_weeds":garden.get("weeds",0),
   "previous_response":self.migrate(state).get("animal_mode")}
 def candidates(self,state):
  # All remain legal; the LLM selects the best bounded ecological response from measured context.
  return deepcopy(ECOLOGY_RESPONSES)
 def apply(self,state,choice,source_model):
  if not choice:return False
  legal={x["id"]:x for x in ECOLOGY_RESPONSES}
  if choice.get("id") not in legal:return False
  c=legal[choice["id"]]; rt=self.migrate(state)
  rt["last_review_day"]=int(state.get("day",1)); rt["source"]=source_model; rt["crop_factor"]=c["crop_factor"]
  rt["vegetation_index"]=round(max(0,min(1,float(rt.get("vegetation_index",.5))+c["vegetation_delta"])),3)
  rt["animal_mode"]=c["animal_mode"]; rt["animal_locations"]=deepcopy(ANIMAL_LOCATIONS[c["animal_mode"]])
  locations=rt["animal_locations"]
  wildlife=rt.setdefault("wildlife_presence",{})
  species=("robins","rooks","pollinators","small_mammals")
  for i,name in enumerate(species): wildlife[name]=locations[(int(state.get("day",1))+i)%len(locations)]
  rt["history"].append({"day":state.get("day"),"response":c["id"],"crop_factor":c["crop_factor"],"animal_mode":c["animal_mode"],"source":source_model})
  rt["history"]=rt["history"][-30:]
  return True

ECOLOGY_AI_MODEL=EcologyAIModel()
