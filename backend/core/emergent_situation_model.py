"""v3.7 emergent situation composition.

The LLM interprets heterogeneous authoritative facts and proposes causal links plus
legal primitive IDs. The engine validates primitives and owns every mutation.
"""
from copy import deepcopy

class EmergentSituationModel:
    SCHEMA_VERSION=1
    MAX_ACTIVE=4
    PRIMITIVES={
      "bakery_reduce_hours":{"label":"Bakery temporarily reduces hours","kind":"business_modifier","target":"bakery","days":2},
      "jonah_seek_help":{"label":"Jonah seeks practical help with bakery strain","kind":"npc_project_nudge","target":"jonah"},
      "mara_misread_distance":{"label":"Mara becomes uncertain about Jonah's distance","kind":"social_tension","a":"mara","b":"jonah","delta":-1},
      "player_mediation_opening":{"label":"Create a bounded opportunity for the player to mediate","kind":"opportunity","target":"social_mediation"},
      "road_delay_pressure":{"label":"Road damage causes a short delivery delay","kind":"economy_pressure","target":"delivery","days":2},
      "village_gossip_opening":{"label":"A public ambiguity becomes gossip material","kind":"opportunity","target":"gossip"},
      "cottage_help_opening":{"label":"A practical cottage-help opportunity becomes plausible","kind":"opportunity","target":"cottage_help"},
      "archive_comparison_opening":{"label":"A records-comparison opportunity becomes plausible","kind":"opportunity","target":"records"},
    }
    def defaults(self):return {"schema_version":1,"active":[],"history":[],"last_review_day":0,"rejected":0,"applied":0}
    def migrate(self,s):
        rt=s.setdefault("emergent_situations",deepcopy(self.defaults()))
        for k,v in self.defaults().items():rt.setdefault(k,deepcopy(v))
        return rt
    def context(self,s):
        econ=s.get("economy",{}); weather=s.get("weather",{}); rel=s.get("relationships",{}); projects=s.get("npc_epistemic_projects",{}).get("projects",{})
        return {"day":s.get("day",1),"weather":deepcopy(weather),"business_pressure":deepcopy(econ.get("business_pressure",{})),"shortages":deepcopy(econ.get("shortages",{})),"core_npcs":{k:{"activity":v.get("activity"),"location":v.get("location")} for k,v in s.get("npcs",{}).items() if k in ("mara","jonah","mrs_ellis")},"relationships":{k:{"affinity":v.get("affinity",0),"trust":v.get("trust",0),"familiarity":v.get("familiarity",0)} for k,v in rel.items() if k in ("mara","jonah","mrs_ellis") and isinstance(v,dict)},"npc_projects":{k:{"belief":v.get("belief"),"question":v.get("question"),"disclosure":v.get("disclosure")} for k,v in projects.items()},"town_theories":deepcopy(s.get("interpretation_system",{}).get("observers",{}).get("town_mind",{}).get("hypotheses",[])[-3:]),"chorus_theories":deepcopy(s.get("interpretation_system",{}).get("observers",{}).get("chorus",{}).get("hypotheses",[])[-3:]),"recent_world_events":deepcopy(s.get("world_events",[])[-8:]),"legal_primitives":[{"id":k,"label":v["label"]} for k,v in self.PRIMITIVES.items()]}
    def apply_proposal(self,s,result,model=None):
        rt=self.migrate(s)
        if not isinstance(result,dict):rt["rejected"]+=1;return False
        ids=result.get("primitive_ids",[])
        if not isinstance(ids,list) or not ids or any(i not in self.PRIMITIVES for i in ids):rt["rejected"]+=1;return False
        ids=list(dict.fromkeys(ids))[:3]
        explanation=str(result.get("interpretation","")).strip()[:500]
        if len(explanation)<20:rt["rejected"]+=1;return False
        row={"id":f"sit_{s.get('day',1)}_{len(rt['history'])+1}","day":s.get("day",1),"interpretation":explanation,"causal_links":result.get("causal_links",[])[:6] if isinstance(result.get("causal_links",[]),list) else [],"primitive_ids":ids,"status":"active","model":model,"executed":[]}
        rt["active"].append(row);rt["active"]=rt["active"][-self.MAX_ACTIVE:];rt["history"].append(deepcopy(row));rt["history"]=rt["history"][-40:];rt["last_review_day"]=s.get("day",1);rt["applied"]+=1;return True
    def execute(self,s):
        from backend.core.causal_history_model import CAUSAL_HISTORY_MODEL
        rt=self.migrate(s);out=[]
        for sit in rt["active"]:
            if sit.get("status")!="active":continue
            for pid in sit.get("primitive_ids",[]):
                if pid in sit.get("executed",[]):continue
                p=self.PRIMITIVES[pid];kind=p["kind"]
                if kind=="social_tension":
                    web=s.setdefault("social_web",{}).setdefault("edges",{}); key="|".join(sorted((p["a"],p["b"])))
                    edge=web.setdefault(key,{"affinity":0,"trust":0,"tension":0});edge["tension"]=max(0,int(edge.get("tension",0))+abs(int(p.get("delta",-1))))
                    CAUSAL_HISTORY_MODEL.add_social_fact(s,"tension",p["a"],p["b"],f"{p['a']} is uncertain about {p['b']} after recent pressures.",[sit["id"],pid],"emergent_situation")
                elif kind=="opportunity":
                    s.setdefault("emergent_opportunities",[]).append({"day":s.get("day",1),"type":p["target"],"source":sit["id"]});s["emergent_opportunities"]=s["emergent_opportunities"][-12:]
                    CAUSAL_HISTORY_MODEL.add_social_fact(s,"opportunity","village",p["target"],f"A {p['target']} opportunity has become plausible.",[sit["id"],pid],"emergent_situation")
                elif kind=="business_modifier":s.setdefault("emergent_modifiers",{})[pid]={"until_day":s.get("day",1)+p.get("days",1),"target":p["target"]}
                elif kind=="economy_pressure":s.setdefault("emergent_modifiers",{})[pid]={"until_day":s.get("day",1)+p.get("days",1),"target":p["target"]}
                elif kind=="npc_project_nudge":s.setdefault("emergent_npc_nudges",[]).append({"day":s.get("day",1),"npc":p["target"],"source":sit["id"]});s["emergent_npc_nudges"]=s["emergent_npc_nudges"][-12:]
                sit.setdefault("executed",[]).append(pid);out.append({"situation":sit["id"],"primitive":pid,"label":p["label"]})
            sit["status"]="resolved"
        rt["active"]=[x for x in rt["active"] if x.get("status")=="active"]
        return out
    def public(self,s):return deepcopy(self.migrate(s))
EMERGENT_SITUATION_MODEL=EmergentSituationModel()
