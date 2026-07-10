"""Part 3 social-web substrate for autonomous NPC-to-NPC relationships.

Authored social history and compatibility are immutable catalogue data. Runtime
relationship state, encounters, and bounded information hooks are save state.
"""
from copy import deepcopy
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SOCIAL_DATA_PATH=ROOT/"content"/"social"/"core_social_web.json"

class SocialModel:
    DIMS={"affinity","trust","familiarity","tension"}
    def __init__(self,path=SOCIAL_DATA_PATH):
        self.path=Path(path); self.data=json.loads(self.path.read_text(encoding="utf-8"))
        self.schema_version=int(self.data.get("schema_version",1)); self.edges=self.data["edges"]; self.validate()
    @staticmethod
    def edge_id(a,b): return "|".join(sorted((a,b)))
    def validate(self):
        errors=[]
        for eid,e in self.edges.items():
            parts=eid.split("|")
            if len(parts)!=2 or parts[0]>=parts[1]: errors.append(f"{eid}: edge id must be sorted pair")
            if set(e.get("baseline",{}))!=self.DIMS: errors.append(f"{eid}: invalid baseline dimensions")
            for k,v in e.get("baseline",{}).items():
                if not isinstance(v,(int,float)) or not -100<=v<=100: errors.append(f"{eid}: invalid {k}={v}")
            for key in ("history","compatibility","friction","meeting_contexts","conversation_topics"):
                if key not in e: errors.append(f"{eid}: missing {key}")
        if errors: raise ValueError("Invalid social web: "+"; ".join(errors))
        return True
    def authored_edge(self,a,b): return deepcopy(self.edges[self.edge_id(a,b)])
    def runtime_defaults(self):
        return {eid:{"schema_version":self.schema_version,"state":deepcopy(e["baseline"]),"encounter_count":0,"last_encounter_minute":None,"encounter_history":[],"shared_topics":[],"recent_effects":[]} for eid,e in self.edges.items()}
    def context(self,a,b,runtime):
        eid=self.edge_id(a,b); authored=self.edges[eid]; rt=runtime[eid]
        return {"pair":eid,"history":authored["history"],"compatibility":deepcopy(authored["compatibility"]),"friction":deepcopy(authored["friction"]),"state":deepcopy(rt["state"]),"shared_topics":deepcopy(rt["shared_topics"][-8:])}
    def bounded_encounter_effect(self,a,b,location,activities):
        e=self.edges[self.edge_id(a,b)]; compatible=location in e["meeting_contexts"]
        purposeful=any(any(word in (act or "").lower() for word in ("work","baking","garden","errand","serving","checking")) for act in activities)
        return {"affinity":1 if compatible else 0,"trust":1 if compatible and purposeful else 0,"familiarity":1,"tension":0}

SOCIAL_MODEL=SocialModel()
