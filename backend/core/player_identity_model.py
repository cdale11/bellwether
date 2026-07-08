"""Part 13 player psychology and evolving identity substrate.

Authoritative game history is interpreted into bounded behavioural tendencies. The
model never rewrites player history: it derives an inspectable identity snapshot
and records only meaningful changes in that interpretation.
"""
from copy import deepcopy

class PlayerIdentityModel:
    TRAITS=("care","community","inquiry","routine","social","independence","resilience","avoidance")

    def runtime_defaults(self):
        return {"schema_version":1,"traits":{k:0 for k in self.TRAITS},
                "dominant_traits":[],"coping_style":"unformed","town_read":"newcomer",
                "evolution_history":[],"last_signature":None}

    def _counts(self,state):
        out={}
        for row in state.get("player_life",{}).get("activity_history",[]):
            a=row.get("activity","unknown"); out[a]=out.get(a,0)+1
        return out

    def derive(self,state):
        counts=self._counts(state); branch=state.get("branch_state",{}); rels=state.get("relationships",{})
        talks=sum(int(r.get("talks",0)) for r in rels.values() if isinstance(r,dict))
        trust=sum(max(0,int(r.get("trust",0))) for r in rels.values() if isinstance(r,dict))
        evidence=len(state.get("investigation",{}).get("evidence",[]))
        structured=len(state.get("mystery_investigation",{}).get("evidence_log",[]))
        acts=sum(counts.values()); dominant=max(counts,key=counts.get) if counts else None
        routine_share=(counts.get(dominant,0)/acts) if dominant and acts else 0
        psych=state.get("psychological_state",{}); horrors=len(state.get("systemic_horror",{}).get("experienced",[]))
        jobs=state.get("jobs",{}); shifts=sum(len(v.get("shift_history",[])) for v in jobs.get("employment",{}).values() if isinstance(v,dict))
        scores={
          "care":min(100,branch.get("care",0)*7+counts.get("tidy",0)*5+counts.get("tea",0)*2+counts.get("garden",0)*4),
          "community":min(100,branch.get("community",0)*6+talks*4+trust*2),
          "inquiry":min(100,branch.get("inquiry",0)*6+(evidence+structured)*5+counts.get("read_timetable",0)*3),
          "routine":min(100,int(routine_share*70)+min(30,acts*2)),
          "social":min(100,talks*8+trust*3),
          "independence":min(100,max(0,acts*3-talks*2)+shifts*3),
          "resilience":min(100,branch.get("recoveries",[]).__len__()*18+horrors*5+max(0,50-int(psych.get("unease",0)))//5),
          "avoidance":min(100,branch.get("avoidance",0)*8+max(0,int(psych.get("unease",0))-45)//2),
        }
        ranked=sorted(scores,key=lambda k:(-scores[k],k)); dominant_traits=[k for k in ranked[:3] if scores[k]>=15]
        if horrors and scores["inquiry"]>=scores["avoidance"]+10: coping="pattern_seeking"
        elif horrors and scores["avoidance"]>scores["inquiry"]: coping="withdrawal"
        elif scores["community"]>=45: coping="connection"
        elif scores["care"]>=45: coping="practical_routine"
        elif acts>=4: coping="self_reliance"
        else: coping="unformed"
        if talks>=6 and trust>=4: town_read="known_neighbor"
        elif acts>=10 or shifts>=2: town_read="settling_in"
        elif evidence+structured>=6: town_read="watchful_outsider"
        else: town_read="newcomer"
        return {"traits":scores,"dominant_traits":dominant_traits,"coping_style":coping,"town_read":town_read}

    def refresh(self,state,reason="state_change"):
        rt=state.setdefault("player_identity",self.runtime_defaults()); derived=self.derive(state)
        sig=(tuple(derived["dominant_traits"]),derived["coping_style"],derived["town_read"])
        old=rt.get("last_signature")
        rt.update(deepcopy(derived)); rt["last_signature"]=list(sig)
        old_norm=tuple(old) if isinstance(old,(list,tuple)) else None
        if old_norm is not None and old_norm!=sig:
            rt.setdefault("evolution_history",[]).append({"day":state.get("day"),"minute":state.get("minute"),"reason":reason,
                "dominant_traits":deepcopy(derived["dominant_traits"]),"coping_style":derived["coping_style"],"town_read":derived["town_read"]})
            rt["evolution_history"]=rt["evolution_history"][-30:]
        return rt

    def public_context(self,state):
        rt=self.refresh(state,"context_refresh")
        return {"dominant_traits":deepcopy(rt["dominant_traits"]),"coping_style":rt["coping_style"],"town_read":rt["town_read"],
                "trait_levels":{k:v for k,v in rt["traits"].items() if v>=15}}

PLAYER_IDENTITY_MODEL=PlayerIdentityModel()
