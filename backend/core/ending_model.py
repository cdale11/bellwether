"""v1.0 RC2 canonical ending families.

Eligibility is deterministic and derived from authoritative play state. The LLM has no
role in creating, unlocking, or resolving endings.
"""
from copy import deepcopy

FAMILIES = {
    "incorporation": {"title":"Incorporation", "text":"You stop trying to stand outside Bellwether's pattern. The village makes room for you by changing the shape of that room, and eventually the distinction between being held and belonging becomes difficult to name."},
    "false_escape": {"title":"False Escape", "text":"You leave with daylight ahead and Bellwether behind. Later, among unfamiliar roads and ordinary rooms, a small repeated detail tells you that distance was never the same thing as release."},
    "rupture": {"title":"Rupture", "text":"You force a break in the pattern with enough knowledge and preparation to make the wound real. Bellwether survives, but not unchanged; neither do the people whose lives were tied to what you broke."},
    "accommodation": {"title":"Accommodation", "text":"You learn the limits of the place and build a life inside them without surrendering the knowledge of what they are. Bellwether remains dangerous, familiar, and partly negotiable."},
    "containment": {"title":"Containment", "text":"You cannot free Bellwether, but you help narrow what it can reach. The work becomes communal, practical, and unfinished: a boundary maintained because people remember why it matters."},
    "liberation_coexistence": {"title":"True Liberation-Coexistence", "text":"You do not destroy the living pattern or submit to it. Through memory, anchors, shared knowledge and careful limits, you create a relationship in which leaving becomes possible and staying becomes a choice."},
}

class EndingModel:
    def runtime_defaults(self):
        return {"schema_version":1,"eligible":[],"resolved":None,"eligibility_history":[]}

    def migrate(self, state):
        rt=state.setdefault("ending_families", self.runtime_defaults())
        for k,v in self.runtime_defaults().items(): rt.setdefault(k,deepcopy(v))
        return rt

    def metrics(self, s):
        rels=[r for r in s.get("relationships",{}).values() if isinstance(r,dict)]
        strong=sum(1 for r in rels if r.get("trust",0)>=4 and r.get("familiarity",0)>=4)
        inv=s.get("investigation",{})
        mystery=s.get("mystery_investigation",{})
        rec=s.get("recurrence",{})
        anchors=rec.get("anchors",{})
        if isinstance(anchors,list): anchor_strength=len(anchors)
        else: anchor_strength=sum(int(v.get("strength",0) if isinstance(v,dict) else v or 0) for v in anchors.values())
        return {
            "evidence":len(inv.get("evidence",[])),
            "deep_mysteries":sum(1 for v in mystery.get("mysteries",{}).values() if isinstance(v,dict) and v.get("state") in {"deepening","resolved"}),
            "strong_relationships":strong,
            "anchor_strength":anchor_strength,
            "run_index":int(rec.get("run_index",1)),
            "familiar_places":sum(1 for v in s.get("player_life",{}).get("location_familiarity",{}).values() if v>=8),
            "health":int(s.get("health",100)),
            "care":int(s.get("branch_state",{}).get("care",0)),
            "community":int(s.get("branch_state",{}).get("community",0)),
            "inquiry":int(s.get("branch_state",{}).get("inquiry",0)),
            "avoidance":int(s.get("branch_state",{}).get("avoidance",0)),
        }

    def eligible(self,s):
        if not s.get("authored_story",{}).get("ending_eligible",False): return []
        m=self.metrics(s); out=[]
        # Broad endings remain reachable; demanding endings require demonstrated preparation.
        if m["avoidance"]>=4 or (m["strong_relationships"]==0 and m["inquiry"]>=4): out.append("false_escape")
        if m["community"]>=5 and m["strong_relationships"]>=2: out.append("containment")
        if m["care"]>=4 and m["familiar_places"]>=3: out.append("accommodation")
        if m["inquiry"]>=6 and m["evidence"]>=6 and m["health"]>=45: out.append("rupture")
        if m["anchor_strength"]>=2 and m["community"]>=4: out.append("incorporation")
        if m["evidence"]>=8 and m["strong_relationships"]>=2 and m["anchor_strength"]>=3 and m["run_index"]>=2 and m["familiar_places"]>=4: out.append("liberation_coexistence")
        # Ending eligibility must never dead-end a completed story.
        if not out: out.append("accommodation")
        return out

    def refresh(self,s):
        rt=self.migrate(s); now=self.eligible(s)
        if now != rt.get("eligible",[]):
            rt["eligible"]=now
            rt["eligibility_history"].append({"day":s.get("day"),"eligible":list(now)})
            rt["eligibility_history"]=rt["eligibility_history"][-12:]
        return now

    def public(self,s):
        rt=self.migrate(s); eligible=self.refresh(s)
        return {"eligible":[{"id":i,"title":FAMILIES[i]["title"]} for i in eligible],"resolved":deepcopy(rt.get("resolved"))}

ENDING_MODEL=EndingModel()
