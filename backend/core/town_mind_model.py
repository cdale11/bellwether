from copy import deepcopy
from backend.core.interpretation_model import INTERPRETATION_MODEL
from backend.core.resistance_model import RESISTANCE_MODEL

INTENTIONS = [
    {"id":"ordinary_rhythm","label":"Protect ordinary village rhythm","domain":"pacing","target":"ordinary_life","pressure":1,"duration_pulses":12},
    {"id":"social_crossing","label":"Create grounded opportunities for residents to cross paths","domain":"social","target":"encounters","pressure":1,"duration_pulses":10},
    {"id":"economic_attention","label":"Let local work and business pressures become more noticeable","domain":"economy","target":"business_pressure","pressure":1,"duration_pulses":12},
    {"id":"environmental_texture","label":"Emphasize seasonal weather, ecology, and place","domain":"environment","target":"world_texture","pressure":1,"duration_pulses":10},
    {"id":"curiosity_nudge","label":"Offer subtle reasons to explore or investigate without forcing the story","domain":"mystery","target":"curiosity","pressure":1,"duration_pulses":12},
    {"id":"relationship_attention","label":"Give existing relationships room to develop through plausible contact","domain":"social","target":"relationships","pressure":1,"duration_pulses":12},
    {"id":"quiet_recovery","label":"Reduce pressure and allow routines, recovery, and domestic life to breathe","domain":"pacing","target":"recovery","pressure":0,"duration_pulses":10},
]

STRATEGIES={
 "property_pressure":{"label":"Pressure the life built around property and home","targets":["property","cottage"]},
 "enterprise_pressure":{"label":"Pressure the player's economic independence","targets":["business","economy"]},
 "mobility_pressure":{"label":"Make movement and escape less dependable","targets":["transport"]},
 "social_pressure":{"label":"Exploit attachment and social dependence","targets":["relationships"]},
 "routine_pressure":{"label":"Disturb the routines the player uses to avoid inquiry","targets":["routine"]},
 "mystery_pressure":{"label":"Make avoidance harder through bounded curiosity pressure","targets":["mystery"]},
}

class TownMindModel:
    schema_version = 3
    def runtime_defaults(self):
        return {"schema_version":2,"status":"dormant","active_intentions":[],"intention_history":[],"last_review_pulse":-999,"review_count":0,"accepted_count":0,"rejected_count":0,"last_model":None,"last_reason":None,
                "strategy":{"observations":{},"dominant_playstyle":"unformed","active_strategy":None,"strategy_history":[],"pressure_log":[],"last_strategy_day":0,"last_pressure_day":0,"resistance_score":0,"hypothesis":None,"hypothesis_confidence":0,"tactic_failures":{},"last_outcome":None,"retreat_until_day":0,"chain_stage":0,"chain_origin":None}}
    def migrate(self,state):
        tm=state.setdefault("town_mind",self.runtime_defaults())
        for k,v in self.runtime_defaults().items(): tm.setdefault(k,deepcopy(v))
        st=tm.setdefault("strategy",deepcopy(self.runtime_defaults()["strategy"]))
        for k,v in self.runtime_defaults()["strategy"].items(): st.setdefault(k,deepcopy(v))
        tm["schema_version"]=self.schema_version; return tm
    def candidates(self,state):
        tm=self.migrate(state); active={x.get("id") for x in tm.get("active_intentions",[])}
        pool=[deepcopy(x) for x in INTENTIONS if x["id"] not in active]
        return pool or [deepcopy(INTENTIONS[0])]
    def observe_player(self,state):
        tm=self.migrate(state); st=tm["strategy"]; ident=state.get("player_identity",{}); traits=ident.get("traits",{})
        prop=state.get("property",{}); biz=state.get("player_businesses",{}); trans=state.get("transport",{})
        rels=state.get("relationships",{}); affinity=0
        for r in rels.values(): affinity += int(r.get("affinity",0)) if isinstance(r,dict) else int(r or 0)
        investigation=len(state.get("investigation",{}).get("evidence",[]))+len(state.get("mystery_investigation",{}).get("evidence_log",[]))
        obs={"property":len(prop.get("owned",{}))+len(prop.get("leases",{}))+len(prop.get("expansions",[])),"business":len(biz.get("enterprises",{})),"transport":len(trans.get("owned",{})),"relationships":affinity,"inquiry":investigation,"routine":int(traits.get("routine",0)),"avoidance":int(traits.get("avoidance",0)),"independence":int(traits.get("independence",0))}
        scores={"property_pressure":obs["property"]*30+obs["routine"],"enterprise_pressure":obs["business"]*55+obs["independence"],"mobility_pressure":obs["transport"]*45+obs["independence"]//2,"social_pressure":obs["relationships"]*2+int(traits.get("social",0)),"routine_pressure":obs["routine"]+obs["avoidance"],"mystery_pressure":max(0,45-obs["inquiry"]*8)+obs["avoidance"]}
        # Blend observed attachment with RC4 playstyle pacing, while keeping strategy deterministic.
        pacing=state.get("playstyle_pacing",{})
        profile=pacing.get("profile")
        if profile=="homesteader": scores["property_pressure"]+=25
        elif profile=="entrepreneur": scores["enterprise_pressure"]+=30
        elif profile=="social": scores["social_pressure"]+=25
        elif profile=="investigator": scores["mystery_pressure"]-=20; scores["social_pressure"]+=8
        elif profile=="romance_focused": scores["social_pressure"]+=35
        elif profile=="avoidant": scores["routine_pressure"]+=20; scores["mystery_pressure"]+=15
        elif profile=="wanderer": scores["mobility_pressure"]+=18
        # A tactic that has repeatedly failed is discounted so the consciousness changes approach.
        failures=st.get("tactic_failures",{})
        for key,count in failures.items():
            if key in scores: scores[key]-=min(60,int(count)*20)
        chosen=max(scores,key=lambda k:(scores[k],k)); st["observations"]=obs; st["dominant_playstyle"]=(profile or chosen.replace("_pressure","")); st["resistance_score"]=max(0,obs["inquiry"]*10-obs["avoidance"])
        st["hypothesis"]={"player_values":st["dominant_playstyle"],"best_leverage":chosen,"pacing_risk":pacing.get("pacing_risk","unknown")}
        st["hypothesis_confidence"]=min(100,25+max(scores.values())//4)
        interpreted=INTERPRETATION_MODEL.public_summary(state,"town_mind").get("hypotheses",[])
        if interpreted:
            lead=max(interpreted,key=lambda h:h.get("confidence",0))
            st["interpreted_theory"]={"claim":lead.get("claim"),"confidence":lead.get("confidence"),"possible_test":lead.get("possible_test"),"supporting_evidence":lead.get("supporting_evidence",[])}
        return chosen
    def strategic_daily_tick(self,state):
        tm=self.migrate(state); st=tm["strategy"]; day=int(state.get("day",1)); chosen=self.observe_player(state)
        # The consciousness starts responding on day 2, but only once per day. It may deliberately retreat.
        if day<2 or int(st.get("last_pressure_day",0))>=day:return None
        if day<=int(st.get("retreat_until_day",0)):
            st["last_pressure_day"]=day; st["last_outcome"]="deliberate_retreat"
            row={"day":day,"strategy":st.get("active_strategy"),"effect":"deliberate_retreat","magnitude":0}
            st["pressure_log"].append(row); st["pressure_log"]=st["pressure_log"][-60:]; return row
        if st.get("active_strategy")!=chosen:
            st["active_strategy"]=chosen; st["last_strategy_day"]=day; st["chain_stage"]=0; st["chain_origin"]=chosen
            st["strategy_history"].append({"day":day,"strategy":chosen,"observations":deepcopy(st["observations"]),"hypothesis":deepcopy(st.get("hypothesis"))}); st["strategy_history"]=st["strategy_history"][-30:]
        modifier=RESISTANCE_MODEL.pressure_modifier(state,chosen)
        absorbed=modifier<=0.4
        result=self._apply_pressure(state,chosen,modifier); st["last_pressure_day"]=day
        if absorbed:
            failures=st.setdefault("tactic_failures",{}); failures[chosen]=int(failures.get(chosen,0))+1; st["last_outcome"]="resisted"
            if failures[chosen]>=2: st["retreat_until_day"]=day+1
        else:
            st["last_outcome"]="pressure_landed"; st["chain_stage"]=min(3,int(st.get("chain_stage",0))+1)
        if result:
            row={"day":day,"strategy":chosen,**result}; st["pressure_log"].append(row); st["pressure_log"]=st["pressure_log"][-60:]
            state.setdefault("village_brain",{})["supernatural_pressure"]=min(100,int(state.get("village_brain",{}).get("supernatural_pressure",0))+1)
            return row
        return None
    def _apply_pressure(self,state,strategy,modifier=1.0):
        if strategy=="property_pressure":
            prop=state.get("property",{}); leases=prop.get("leases",{})
            if leases: prop["rent_arrears"]=int(prop.get("rent_arrears",0))+max(0,round(1*modifier)); return {"effect":"administrative_property_pressure","magnitude":1}
            cottage=state.get("player_status",{}).get("cottage",{}); cottage["condition"]=max(0,float(cottage.get("condition",100))-(.5*modifier)); return {"effect":"accelerated_cottage_wear","magnitude":round(.5*modifier,2)}
        if strategy=="enterprise_pressure":
            ents=state.get("player_businesses",{}).get("enterprises",{})
            if ents:
                bid=max(ents,key=lambda k:ents[k].get("cash",0)); b=ents[bid]; b["health"]=max(0,int(b.get("health",70))-max(0,round(1*modifier))); return {"effect":"business_friction","target":bid,"magnitude":1}
            return {"effect":"market_attention","magnitude":0}
        if strategy=="mobility_pressure":
            rt=state.get("transport",{}); active=rt.get("active"); d=rt.get("owned",{}).get(active)
            if d: d["condition"]=max(0,float(d.get("condition",100))-(1*modifier)); return {"effect":"vehicle_wear","target":active,"magnitude":1}
            return {"effect":"route_attention","magnitude":0}
        if strategy=="social_pressure":
            # Do not rewrite authored relationship values. Increase social pressure through psychology only.
            psych=state.setdefault("psychological_state",{}); psych["unease"]=min(100,int(psych.get("unease",0))+max(0,round(1*modifier))); return {"effect":"social_unease","magnitude":1}
        if strategy=="routine_pressure":
            psych=state.setdefault("psychological_state",{}); psych["familiarity_disruptions"]=int(psych.get("familiarity_disruptions",0))+max(0,round(1*modifier)); return {"effect":"routine_disruption","magnitude":1}
        if strategy=="mystery_pressure":
            state.setdefault("branch_state",{})["avoidance"]=int(state.get("branch_state",{}).get("avoidance",0))+max(0,round(1*modifier)); return {"effect":"avoidance_pressure","magnitude":1}
        return None
    def compact_context(self,state):
        tm=self.migrate(state); economy=state.get("economy",{}); relationships=state.get("relationships",{}); rel_values=[]
        for rel in relationships.values():
            if isinstance(rel,dict): rel_values.append(rel.get("affinity",0))
        return {"day":state.get("day"),"minute":state.get("minute"),"village_mood":state.get("village_brain",{}).get("mood"),"village_focus":state.get("village_brain",{}).get("focus"),"psychological_stage":state.get("psychological_state",{}).get("stage","ordinary"),"story_flags":{k:v for k,v in state.get("flags",{}).items() if v} if isinstance(state.get("flags"),dict) else {},"player_style":state.get("llm_context",{}).get("player_style",{}),"player_identity":state.get("player_identity",{}),"strategic_observation":deepcopy(tm["strategy"]),"active_dynamic_events":[x.get("id") for x in state.get("dynamic_events",{}).get("active",[]) if isinstance(x,dict)][:4],"business_pressure":economy.get("business_pressure",{}),"relationship_affinity_range":[min(rel_values),max(rel_values)] if rel_values else [0,0],"recent_world_events":state.get("world_events",[])[-4:],"active_intentions":tm.get("active_intentions",[]),"interpreted_player_theory":INTERPRETATION_MODEL.public_summary(state,"town_mind")}
    def expire(self,state):
        pulse=state.get("village_brain",{}).get("pulse_count",0); tm=self.migrate(state); tm["active_intentions"]=[x for x in tm.get("active_intentions",[]) if x.get("expires_pulse",pulse+1)>pulse]
    def validate_and_apply(self,state,candidate,model_name=None,reason="scheduled"):
        if not isinstance(candidate,dict):return False
        legal={x["id"]:x for x in INTENTIONS}; cid=candidate.get("id"); tm=self.migrate(state)
        if cid not in legal: tm["rejected_count"]+=1; return False
        pulse=state.get("village_brain",{}).get("pulse_count",0); item=deepcopy(legal[cid]); item["created_pulse"]=pulse; item["expires_pulse"]=pulse+item.pop("duration_pulses",10)
        tm["active_intentions"]=[x for x in tm.get("active_intentions",[]) if x.get("domain")!=item.get("domain")]; tm["active_intentions"].append(item); tm["active_intentions"]=tm["active_intentions"][-3:]
        tm["intention_history"].append({**item,"reason":reason}); tm["intention_history"]=tm["intention_history"][-24:]; tm["status"]="active"; tm["accepted_count"]+=1; tm["last_model"]=model_name; tm["last_reason"]=reason; return True
    def director_context(self,state):
        self.expire(state); return [{k:x.get(k) for k in ("id","domain","target","pressure")} for x in self.migrate(state).get("active_intentions",[])]
    def developer_context(self,state):
        tm=self.migrate(state); self.observe_player(state); return deepcopy(tm["strategy"])
TOWN_MIND_MODEL=TownMindModel()
