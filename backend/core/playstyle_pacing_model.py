"""RC4 multi-playstyle story pacing observer.

Observes player tempo without changing authored story gates. It classifies broad playstyle
and records pacing risk so the Town Consciousness can adapt pressure without inventing canon.
"""
from copy import deepcopy

class PlaystylePacingModel:
    schema_version=1
    def runtime_defaults(self):
        return {"schema_version":1,"profile":"unformed","tempo":"early","pacing_risk":"none",
                "metrics":{},"history":[],"last_day":0}
    def migrate(self,state):
        rt=state.setdefault("playstyle_pacing",self.runtime_defaults())
        for k,v in self.runtime_defaults().items(): rt.setdefault(k,deepcopy(v))
        rt["schema_version"]=self.schema_version; return rt
    def metrics(self,state):
        story=state.get("authored_story",{}); chapter=story.get("chapter","arrival")
        chapters=["arrival","first_threads","distributed_archive","witnesses","boundaries","chorus_shape","eleanor_method","convergence"]
        progress=chapters.index(chapter) if chapter in chapters else 0
        life=state.get("player_life",{}); acts=len(life.get("activity_history",[]))
        rels=state.get("relationships",{}); social=sum(int(r.get("talks",0)) for r in rels.values() if isinstance(r,dict))
        biz=len(state.get("player_businesses",{}).get("enterprises",{}))
        property_depth=len(state.get("property",{}).get("owned",{}))+len(state.get("property",{}).get("leases",{}))+len(state.get("property",{}).get("expansions",[]))
        evidence=len(state.get("investigation",{}).get("evidence",[]))+len(state.get("mystery_investigation",{}).get("evidence_log",[]))
        romance=max([int(r.get("affinity",0)) for r in rels.values() if isinstance(r,dict)] or [0])
        return {"day":int(state.get("day",1)),"story_progress":progress,"ordinary_actions":acts,"social_actions":social,
                "businesses":biz,"property_depth":property_depth,"evidence":evidence,"romance_affinity":romance,"avoidance":int(state.get("branch_state",{}).get("avoidance",0))+int(state.get("player_identity",{}).get("traits",{}).get("avoidance",0))}
    def classify(self,m):
        scores={
            "investigator":m["evidence"]*8+m["story_progress"]*12,
            "homesteader":m["ordinary_actions"]*2+m["property_depth"]*18,
            "entrepreneur":m["businesses"]*35+m["property_depth"]*8,
            "social":m["social_actions"]*5+m["romance_affinity"],
            "romance_focused":max(0,m["romance_affinity"]-50)*4+m["social_actions"],
            "avoidant":m["avoidance"]*12+max(0,m["ordinary_actions"]*2-m["story_progress"]*18-m["evidence"]*5),
            "wanderer":max(0,m["day"]*4-m["ordinary_actions"]-m["social_actions"]-m["evidence"]*2),
        }
        return max(scores,key=lambda k:(scores[k],k))
    def assess(self,state):
        rt=self.migrate(state); m=self.metrics(state); profile=self.classify(m)
        if m["story_progress"]>=6: tempo="late"
        elif m["story_progress"]>=3: tempo="middle"
        else: tempo="early"
        expected=min(7,max(0,(m["day"]-1)//3))
        if m["story_progress"]+2<expected: risk="stalled"
        elif m["story_progress"]>expected+3: risk="rushing"
        else: risk="balanced"
        changed=(profile!=rt.get("profile") or tempo!=rt.get("tempo") or risk!=rt.get("pacing_risk"))
        rt.update({"profile":profile,"tempo":tempo,"pacing_risk":risk,"metrics":m})
        if changed:
            rt["history"].append({"day":m["day"],"profile":profile,"tempo":tempo,"pacing_risk":risk})
            rt["history"]=rt["history"][-60:]
        return rt
    def daily_tick(self,state):
        rt=self.assess(state); day=int(state.get("day",1))
        if rt.get("last_day",0)>=day:return None
        rt["last_day"]=day
        return {"day":day,"profile":rt["profile"],"tempo":rt["tempo"],"pacing_risk":rt["pacing_risk"]}
    def public(self,state):
        rt=self.assess(state)
        return {k:deepcopy(rt[k]) for k in ("profile","tempo","pacing_risk","metrics","history")}

PLAYSTYLE_PACING_MODEL=PlaystylePacingModel()
