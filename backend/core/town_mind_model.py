from copy import deepcopy

INTENTIONS = [
    {"id":"ordinary_rhythm","label":"Protect ordinary village rhythm","domain":"pacing","target":"ordinary_life","pressure":1,"duration_pulses":12},
    {"id":"social_crossing","label":"Create grounded opportunities for residents to cross paths","domain":"social","target":"encounters","pressure":1,"duration_pulses":10},
    {"id":"economic_attention","label":"Let local work and business pressures become more noticeable","domain":"economy","target":"business_pressure","pressure":1,"duration_pulses":12},
    {"id":"environmental_texture","label":"Emphasize seasonal weather, ecology, and place","domain":"environment","target":"world_texture","pressure":1,"duration_pulses":10},
    {"id":"curiosity_nudge","label":"Offer subtle reasons to explore or investigate without forcing the story","domain":"mystery","target":"curiosity","pressure":1,"duration_pulses":12},
    {"id":"relationship_attention","label":"Give existing relationships room to develop through plausible contact","domain":"social","target":"relationships","pressure":1,"duration_pulses":12},
    {"id":"quiet_recovery","label":"Reduce pressure and allow routines, recovery, and domestic life to breathe","domain":"pacing","target":"recovery","pressure":0,"duration_pulses":10},
]

class TownMindModel:
    schema_version = 1

    def runtime_defaults(self):
        return {
            "schema_version": self.schema_version,
            "status": "dormant",
            "active_intentions": [],
            "intention_history": [],
            "last_review_pulse": -999,
            "review_count": 0,
            "accepted_count": 0,
            "rejected_count": 0,
            "last_model": None,
            "last_reason": None,
        }

    def candidates(self, state):
        active={x.get("id") for x in state.get("town_mind",{}).get("active_intentions",[])}
        pool=[deepcopy(x) for x in INTENTIONS if x["id"] not in active]
        return pool or [deepcopy(INTENTIONS[0])]

    def compact_context(self, state):
        economy=state.get("economy",{})
        relationships=state.get("relationships",{})
        rel_values=[]
        for rel in relationships.values():
            if isinstance(rel,dict): rel_values.append(rel.get("affinity",0))
        return {
            "day":state.get("day"), "minute":state.get("minute"),
            "village_mood":state.get("village_brain",{}).get("mood"),
            "village_focus":state.get("village_brain",{}).get("focus"),
            "psychological_stage":state.get("psychological_state",{}).get("stage","ordinary"),
            "story_flags":{k:v for k,v in state.get("flags",{}).items() if v} if isinstance(state.get("flags"),dict) else {},
            "player_style":state.get("llm_context",{}).get("player_style",{}),
            "active_dynamic_events":[x.get("id") for x in state.get("dynamic_events",{}).get("active",[]) if isinstance(x,dict)][:4],
            "business_pressure":economy.get("business_pressure",{}),
            "relationship_affinity_range":[min(rel_values),max(rel_values)] if rel_values else [0,0],
            "recent_world_events":state.get("world_events",[])[-4:],
            "active_intentions":state.get("town_mind",{}).get("active_intentions",[]),
        }

    def expire(self, state):
        pulse=state.get("village_brain",{}).get("pulse_count",0)
        tm=state.setdefault("town_mind",self.runtime_defaults())
        tm["active_intentions"]=[x for x in tm.get("active_intentions",[]) if x.get("expires_pulse",pulse+1)>pulse]

    def validate_and_apply(self, state, candidate, model_name=None, reason="scheduled"):
        if not isinstance(candidate,dict): return False
        legal={x["id"]:x for x in INTENTIONS}
        cid=candidate.get("id")
        if cid not in legal:
            state["town_mind"]["rejected_count"]+=1; return False
        pulse=state.get("village_brain",{}).get("pulse_count",0)
        item=deepcopy(legal[cid]); item["created_pulse"]=pulse; item["expires_pulse"]=pulse+item.pop("duration_pulses",10)
        tm=state["town_mind"]
        tm["active_intentions"]=[x for x in tm.get("active_intentions",[]) if x.get("domain")!=item.get("domain")]
        tm["active_intentions"].append(item)
        tm["active_intentions"]=tm["active_intentions"][-3:]
        tm["intention_history"].append({**item,"reason":reason}); tm["intention_history"]=tm["intention_history"][-24:]
        tm["status"]="active"; tm["accepted_count"]+=1; tm["last_model"]=model_name; tm["last_reason"]=reason
        return True

    def director_context(self,state):
        self.expire(state)
        return [{k:x.get(k) for k in ("id","domain","target","pressure")} for x in state.get("town_mind",{}).get("active_intentions",[])]

TOWN_MIND_MODEL=TownMindModel()
