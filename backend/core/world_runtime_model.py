"""Persistent ordinary environmental runtime for Bellwether v1.0.1.

The model turns authoritative weather/season history into slow environmental
state. It is deterministic, migration-safe, and intentionally cheaper than an
LLM call. Directors may later propose bounded strategic tendencies, but this
model remains the authority that applies and exposes consequences.
"""
from copy import deepcopy

class WorldRuntimeModel:
    def runtime_defaults(self):
        return {
            "schema_version": 1,
            "last_absolute_minute": 550,
            "last_day_recorded": 0,
            "weather_history": [],
            "tendencies": {
                "wet_period": 0.0,
                "drying_pressure": 0.0,
                "pollinator_activity": 0.55,
                "bird_activity": 0.65,
                "soil_saturation": 0.45,
                "river_pressure": 0.25,
            },
            "location_conditions": {},
            "observations": [],
            "economy_signals": {"delivery_disruption": 0, "produce_pressure": 0.0},
            "ticks": 0,
        }

    def migrate(self, state):
        rt=state.setdefault("world_runtime", self.runtime_defaults())
        defaults=self.runtime_defaults()
        for key,value in defaults.items(): rt.setdefault(key,deepcopy(value))
        for key,value in defaults["tendencies"].items(): rt.setdefault("tendencies",{}).setdefault(key,value)
        for key,value in defaults["economy_signals"].items(): rt.setdefault("economy_signals",{}).setdefault(key,value)
        rt["schema_version"]=1
        return rt

    @staticmethod
    def _clamp(value, low=0.0, high=1.0):
        return max(low,min(high,float(value)))

    def advance(self, state, minutes):
        rt=self.migrate(state); t=rt["tendencies"]
        weather=state.get("weather",{}).get("state","soft_overcast")
        season=state.get("season",{}).get("id","late_spring")
        rain=weather in {"light_rain","heavy_rain","storm","snow"}
        severe=weather in {"heavy_rain","storm","snow"}
        clear=weather=="clear"
        scale=max(0.0,float(minutes))/1440.0
        t["wet_period"]=self._clamp(t["wet_period"] + scale*(0.85 if rain else -0.22))
        t["drying_pressure"]=self._clamp(t["drying_pressure"] + scale*(0.65 if clear else -0.28))
        t["soil_saturation"]=self._clamp(t["soil_saturation"] + scale*(0.72 if rain else -0.16))
        t["river_pressure"]=self._clamp(t["river_pressure"] + scale*(0.5 if severe else 0.15 if rain else -0.1))
        cold="winter" in season
        pollinator_target=0.18 if cold else (0.35 if rain else 0.78 if clear else 0.58)
        bird_target=0.35 if severe else (0.48 if cold else 0.72)
        blend=min(1.0,scale*1.8)
        t["pollinator_activity"]=round(t["pollinator_activity"]+(pollinator_target-t["pollinator_activity"])*blend,3)
        t["bird_activity"]=round(t["bird_activity"]+(bird_target-t["bird_activity"])*blend,3)
        rt["ticks"]+=1
        rt["last_absolute_minute"]=(int(state.get("day",1))-1)*1440+int(state.get("minute",0))
        self._refresh_locations(state,rt)
        rt["economy_signals"]={
            "delivery_disruption": 2 if weather=="storm" else 1 if severe else 0,
            "produce_pressure": round(max(0,t["drying_pressure"]-.65)+max(0,t["wet_period"]-.78),2),
        }
        return rt

    def _refresh_locations(self,state,rt):
        t=rt["tendencies"]; cond=rt.setdefault("location_conditions",{})
        cond["ashcroft_cottage"]={"soil":"waterlogged" if t["soil_saturation"]>.82 else "dry" if t["soil_saturation"]<.22 else "workable"}
        cond["riverside_path"]={"river":"high" if t["river_pressure"]>.72 else "rising" if t["river_pressure"]>.48 else "normal"}
        cond["north_woods"]={"ground":"sodden" if t["wet_period"]>.75 else "damp" if t["wet_period"]>.35 else "firm"}
        loc_state=state.setdefault("location_state",{})
        if "riverside_path" in loc_state: loc_state["riverside_path"]["river_level"]=cond["riverside_path"]["river"]

    def record_day(self,state,day=None):
        rt=self.migrate(state); d=int(day if day is not None else state.get("day",1))
        if rt.get("last_day_recorded",0)>=d:return None
        row={"day":d,"weather":state.get("weather",{}).get("state"),"temperature_c":state.get("weather",{}).get("temperature_c"),"season":state.get("season",{}).get("id")}
        rt["weather_history"].append(row); rt["weather_history"]=rt["weather_history"][-30:]
        rt["last_day_recorded"]=d
        return row

    def observation(self,state,location_id):
        rt=self.migrate(state); t=rt["tendencies"]; cond=rt.get("location_conditions",{}).get(location_id,{})
        text=None
        if location_id=="ashcroft_cottage":
            soil=cond.get("soil","workable")
            text={"waterlogged":"The cottage soil holds water in every low patch; recent rain is still shaping what can grow here.","dry":"The topsoil is drying and pale around the edges of the beds.","workable":"The garden soil is damp enough to work without clinging heavily to the spade."}[soil]
        elif location_id=="riverside_path":
            river=cond.get("river","normal")
            text={"high":"The river is high against the bank, carrying the memory of several wet days.","rising":"The river is running fuller than usual and still appears to be rising.","normal":"The river keeps within its ordinary banks, moving steadily past reeds and roots."}[river]
        elif location_id=="north_woods":
            ground=cond.get("ground","damp"); text=f"Under the trees the ground is {ground}; the recent weather has left a persistent mark on the path."
        elif t["pollinator_activity"]<.3:
            text="There are noticeably fewer insects moving among the flowers than the season would normally suggest."
        elif t["bird_activity"]<.4:
            text="Bird activity is subdued; most calls come from cover rather than open ground."
        if text:
            row={"day":state.get("day",1),"minute":state.get("minute",0),"location":location_id,"text":text}
            obs=rt.setdefault("observations",[])
            if not obs or obs[-1].get("text")!=text: obs.append(row)
            rt["observations"]=obs[-40:]
        return text

WORLD_RUNTIME_MODEL=WorldRuntimeModel()
