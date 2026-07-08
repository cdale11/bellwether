"""Part 4 player activities and daily-life substrate.

Authoritative catalog data is separated from mutable save state.  The first
vertical slice is a real cottage garden loop; later economy/cooking parts can
consume its harvest without replacing this state model.
"""
from copy import deepcopy

CROPS = {
    "radish": {"name":"Radish", "seasons":{"early_spring","late_spring","early_summer","late_summer","early_autumn"}, "growth_minutes":1440, "water_need":35, "yield":3},
    "lettuce": {"name":"Lettuce", "seasons":{"early_spring","late_spring","early_summer","late_summer","early_autumn"}, "growth_minutes":2160, "water_need":45, "yield":2},
    "carrot": {"name":"Carrot", "seasons":{"early_spring","late_spring","early_summer","late_summer"}, "growth_minutes":4320, "water_need":30, "yield":3},
    "broad_bean": {"name":"Broad bean", "seasons":{"early_spring","late_spring","early_autumn","late_autumn"}, "growth_minutes":5760, "water_need":40, "yield":4},
}

class ActivityModel:
    def runtime_defaults(self):
        return {
            "schema_version": 1,
            "garden": {
                "soil_prepared": False,
                "soil_condition": 35,
                "moisture": 45,
                "weeds": 55,
                "plots": [None, None, None],
                "seed_stock": {"radish":0,"lettuce":0,"carrot":0,"broad_bean":0},
                "harvest_store": {},
                "last_update_absolute_minute": 550,
                "actions_completed": 0,
            },
            "skills": {"gardening":0,"home_care":0,"cooking":0},
            "routines": {},
        }

    def absolute_minute(self, state):
        return (int(state.get("day",1))-1)*1440 + int(state.get("minute",0))

    def stage(self, plot):
        if not plot: return "empty"
        ratio=plot.get("growth",0)/max(1,plot.get("growth_required",1))
        if ratio>=1: return "ready"
        if ratio>=.7: return "maturing"
        if ratio>=.3: return "growing"
        if ratio>0: return "seedling"
        return "sown"

    def advance(self, state, minutes):
        rt=state.setdefault("player_activities",self.runtime_defaults())
        g=rt["garden"]
        weather=state.get("weather",{}).get("state","")
        rain=weather in {"rain","light_rain","heavy_rain","storm","showers","drizzle"} or "rain" in weather
        snow=weather == "snow"
        if rain: g["moisture"]=min(100,g.get("moisture",45)+minutes*.12)
        elif snow: g["moisture"]=min(100,g.get("moisture",45)+minutes*.025)
        else: g["moisture"]=max(0,g.get("moisture",45)-minutes*.018)
        g["weeds"]=min(100,g.get("weeds",0)+minutes*.003)
        moisture=g["moisture"]
        weed_penalty=max(0,(g["weeds"]-65)/100)
        for p in g["plots"]:
            if not p or self.stage(p)=="ready": continue
            crop=CROPS[p["crop_id"]]
            water_factor=1.0 if moisture>=crop["water_need"] else max(.15,moisture/max(1,crop["water_need"]))
            season_ok=state.get("season",{}).get("id") in crop["seasons"]
            season_factor=1.0 if season_ok else .35
            gain=minutes*water_factor*season_factor*(1-0.5*weed_penalty)
            p["growth"]=min(p["growth_required"],p.get("growth",0)+gain)
            p["health"]=max(0,min(100,p.get("health",100) - (0.012*minutes if moisture<10 else 0) - weed_penalty*.004*minutes))
        g["last_update_absolute_minute"]=self.absolute_minute(state)

    def available_garden_actions(self, state):
        g=state.setdefault("player_activities",self.runtime_defaults())["garden"]
        out=[]
        if not g["soil_prepared"]: out.append(("garden:prepare","Prepare the Garden Beds"))
        else:
            for crop_id,crop in CROPS.items():
                if g["seed_stock"].get(crop_id,0)>0 and any(p is None for p in g["plots"]):
                    out.append((f"garden:sow:{crop_id}",f"Sow {crop['name']} Seeds"))
            if g["moisture"]<75 and any(g["plots"]): out.append(("garden:water","Water the Garden"))
            if g["weeds"]>15: out.append(("garden:tend","Weed and Tend the Beds"))
            if any(p and self.stage(p)=="ready" for p in g["plots"]): out.append(("garden:harvest","Harvest Ready Crops"))
        out.append(("garden:inspect","Inspect the Garden"))
        return out

ACTIVITY_MODEL=ActivityModel()
