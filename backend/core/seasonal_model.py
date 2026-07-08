"""Part 8 seasonal village-life and ecology substrate.

Derives ordinary ecological and village responses from authoritative season, weather,
time and location state. Runtime observations are persistent; authored seasonal profiles
remain immutable.
"""
from copy import deepcopy

SEASONAL_PROFILES = {
 "early_spring":{"vegetation":"buds opening in hedges and damp verge grass","wildlife":"rooks nest-building and blackbirds probing soft ground","village_rhythm":"garden clearing, repairs and cautious planting","market_factor":{"lettuce_seed":1.2,"broad_bean_seed":1.2}},
 "late_spring":{"vegetation":"hawthorn blossom, nettles and fast-growing grass","wildlife":"swallows overhead and busy nesting birds","village_rhythm":"gardens, washing lines and longer outdoor errands","market_factor":{"lettuce_seed":1.2,"radish_seed":1.2}},
 "early_summer":{"vegetation":"full hedges, cow parsley and vigorous garden growth","wildlife":"swifts, bees and evening bats","village_rhythm":"long workdays and lingering evening conversations","market_factor":{"groceries":1.1}},
 "high_summer":{"vegetation":"drying verge tops and dense green gardens","wildlife":"bees in shade flowers and birds active at dawn","village_rhythm":"early starts, shaded pauses and late outdoor social life","market_factor":{"groceries":1.1}},
 "late_summer":{"vegetation":"seed heads, heavy hedges and first tired leaves","wildlife":"swallows gathering and wasps around fallen fruit","village_rhythm":"harvest, preserving and late-summer maintenance","market_factor":{"repair_supplies":1.1}},
 "early_autumn":{"vegetation":"berries, damp leaves and fading roadside growth","wildlife":"rooks gathering and migrant birds passing through","village_rhythm":"harvest work, chimney checks and earlier errands","market_factor":{"repair_supplies":1.2}},
 "late_autumn":{"vegetation":"bare stems, leaf litter and dark wet hedges","wildlife":"rooks in fields and garden birds returning to feeders","village_rhythm":"indoor repairs, fuel preparation and shortened workdays","market_factor":{"groceries":1.2,"repair_supplies":1.2}},
 "early_winter":{"vegetation":"dormant beds, bare hedges and frost-darkened grass","wildlife":"robins near doors and rooks crossing pale fields","village_rhythm":"short errands, heating routines and indoor work","market_factor":{"groceries":1.25}},
 "deep_winter":{"vegetation":"hard ground, dormant plots and frost-burned verges","wildlife":"small birds feeding urgently and sparse dawn activity","village_rhythm":"compressed daylight routines and mutual checking-in","market_factor":{"groceries":1.3,"repair_supplies":1.15}},
 "late_winter":{"vegetation":"snowdrops, wet bare hedges and the first swelling buds","wildlife":"territorial birdsong returning on brighter mornings","village_rhythm":"mending, planning and tentative garden preparation","market_factor":{"broad_bean_seed":1.2}},
}

class SeasonalModel:
    def runtime_defaults(self):
        return {"schema_version":1,"current_profile":None,"day_snapshots":{},"observations":[],"ecology":{"vegetation":"","wildlife":"","activity_level":"normal"}}
    def profile(self,state):
        sid=state.get("season",{}).get("id","late_spring")
        return deepcopy(SEASONAL_PROFILES.get(sid,SEASONAL_PROFILES["late_spring"]))
    def refresh(self,state):
        rt=state.setdefault("seasonal_life",self.runtime_defaults()); sid=state.get("season",{}).get("id","late_spring")
        p=self.profile(state); weather=state.get("weather",{}).get("state",""); minute=int(state.get("minute",0))
        level="normal"
        if "heavy_rain" in weather or "storm" in weather: level="sheltered"
        elif minute < 360 or minute > 1260: level="quiet"
        elif "clear" in weather or "sun" in weather: level="active"
        rt["current_profile"]=sid; rt["ecology"]={"vegetation":p["vegetation"],"wildlife":p["wildlife"],"activity_level":level}
        day=str(state.get("day",1))
        rt["day_snapshots"].setdefault(day,{"season":sid,"vegetation":p["vegetation"],"wildlife":p["wildlife"],"village_rhythm":p["village_rhythm"]})
        # Feed ordinary ambience through existing state, making environment visible.
        state.setdefault("ambient",{})["wildlife"]=p["wildlife"].capitalize()+("; most activity is under cover." if level=="sheltered" else ".")
        state["ambient"]["village"]=p["village_rhythm"].capitalize()+"."
        return rt["ecology"]
    def location_context(self,state,location_id):
        rt=state.setdefault("seasonal_life",self.runtime_defaults()); self.refresh(state)
        tags=[]
        try:
            from backend.core.world_model import WORLD_MODEL
            tags=WORLD_MODEL.location(location_id).get("ecology_tags",[])
        except Exception: pass
        return {"season":rt["current_profile"],"ecology":deepcopy(rt["ecology"]),"location_ecology_tags":list(tags)}

SEASONAL_MODEL=SeasonalModel()
