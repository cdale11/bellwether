"""v2.10.0 bounded integration between authored story, simulation and Town Consciousness.

Authored story and evidence remain authoritative. This model observes progress/avoidance and
selects non-canonical response postures; it never creates clues, facts, chapters or endings.
"""
from copy import deepcopy

POSTURES = {
    "normalize": "Make ordinary life unusually attractive and coherent",
    "distract": "Redirect attention toward the life the player has built",
    "isolate": "Increase social and interpretive uncertainty without rewriting relationships",
    "contradict": "Increase bounded presentation and routine pressure around known anomalies",
    "confront": "Apply direct strategic pressure when avoidance persists despite strong evidence",
}

class StoryConsciousnessIntegrationModel:
    schema_version=1
    def runtime_defaults(self):
        return {"schema_version":1,"posture":"observe","history":[],"last_day":0,"story_progress":0,
                "avoidance_pressure":0,"ordinary_attachment":0,"response_strength":0,"signals":[]}
    def migrate(self,state):
        rt=state.setdefault("story_consciousness_integration",self.runtime_defaults())
        for k,v in self.runtime_defaults().items(): rt.setdefault(k,deepcopy(v))
        rt["schema_version"]=self.schema_version
        return rt
    def metrics(self,state):
        story=state.get("authored_story",{}); inv=state.get("investigation",{}); graph=state.get("mystery_investigation",{})
        life=state.get("player_life",{}); town=state.get("town_mind",{}).get("strategy",{})
        chapters=["arrival","first_threads","distributed_archive","witnesses","boundaries","chorus_shape","eleanor_method","convergence"]
        chapter=story.get("chapter","arrival")
        progress=chapters.index(chapter) if chapter in chapters else 0
        evidence=len(inv.get("evidence",[]))+len(graph.get("evidence_log",[]))
        ordinary=len(life.get("activity_history",[]))+int(life.get("cottage_care",0))
        avoidance=int(state.get("branch_state",{}).get("avoidance",0))+int(state.get("player_identity",{}).get("traits",{}).get("avoidance",0))
        return {"chapter":chapter,"progress":progress,"evidence":evidence,"ordinary":ordinary,"avoidance":avoidance,
                "town_strategy":town.get("active_strategy"),"narrative_seen":len(state.get("authored_narrative",{}).get("seen",[]))}
    def choose_posture(self,m):
        if m["progress"]>=6: return "confront"
        if m["evidence"]>=8 and m["avoidance"]>=4: return "contradict"
        if m["ordinary"]>=18 and m["progress"]<=2: return "distract"
        if m["progress"]>=3 and m["town_strategy"]=="social_pressure": return "isolate"
        return "normalize"
    def daily_tick(self,state):
        rt=self.migrate(state); day=int(state.get("day",1))
        if day<2 or rt["last_day"]>=day:return None
        m=self.metrics(state); posture=self.choose_posture(m)
        strength=max(1,min(3,1+m["progress"]//3+(1 if m["avoidance"]>=6 else 0)))
        rt.update({"posture":posture,"last_day":day,"story_progress":m["progress"],"avoidance_pressure":m["avoidance"],"ordinary_attachment":m["ordinary"],"response_strength":strength})
        row={"day":day,"posture":posture,"strength":strength,"chapter":m["chapter"],"evidence":m["evidence"],"ordinary":m["ordinary"],"avoidance":m["avoidance"]}
        rt["history"].append(row); rt["history"]=rt["history"][-60:]
        # Non-canonical, bounded consequences only.
        if posture=="normalize": state.setdefault("psychological_state",{})["unease"]=max(0,int(state.get("psychological_state",{}).get("unease",0))-1)
        elif posture=="distract": state.setdefault("village_brain",{})["focus"]="ordinary_opportunity"
        elif posture=="isolate": state.setdefault("psychological_state",{})["unease"]=min(100,int(state.get("psychological_state",{}).get("unease",0))+1)
        elif posture=="contradict": state.setdefault("psychological_state",{})["familiarity_disruptions"]=int(state.get("psychological_state",{}).get("familiarity_disruptions",0))+1
        elif posture=="confront": state.setdefault("village_brain",{})["supernatural_pressure"]=min(100,int(state.get("village_brain",{}).get("supernatural_pressure",0))+1)
        return row
    def record_authored_signal(self,state,scene_id,chapter):
        rt=self.migrate(state); token=f"{chapter}:{scene_id}"
        if token not in rt["signals"]: rt["signals"].append(token); rt["signals"]=rt["signals"][-80:]
    def public(self,state):
        rt=self.migrate(state)
        return {"posture":rt["posture"],"response_strength":rt["response_strength"],"story_progress":rt["story_progress"],"avoidance_pressure":rt["avoidance_pressure"],"ordinary_attachment":rt["ordinary_attachment"],"recent_history":deepcopy(rt["history"][-8:]),"authority":"observes authored truth; cannot create or mutate canon"}

STORY_CONSCIOUSNESS_INTEGRATION_MODEL=StoryConsciousnessIntegrationModel()
