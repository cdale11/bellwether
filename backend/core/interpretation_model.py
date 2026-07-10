"""v3.5.0 fallible multi-observer interpretation.

Authoritative history remains factual. Each observer receives a different evidence
window and may form revisable hypotheses grounded only in visible event IDs.
"""
from copy import deepcopy

class InterpretationModel:
    SCHEMA_VERSION=3
    OBSERVERS=("town_mind","chorus","village","mara","jonah","mrs_ellis")
    NPC_OBSERVERS={"mara","jonah","mrs_ellis"}
    def runtime_defaults(self):
        return {"schema_version":self.SCHEMA_VERSION,"observers":{o:{"hypotheses":[],"last_review_day":0,"revision_count":0,"last_model":None,"revision_ledger":[]} for o in self.OBSERVERS},"review_history":[]}
    def migrate(self,state):
        root=state.setdefault("interpretation_system",deepcopy(self.runtime_defaults()))
        root.setdefault("observers",{})
        for o in self.OBSERVERS:
            slot=root["observers"].setdefault(o,{})
            for k,v in self.runtime_defaults()["observers"][o].items(): slot.setdefault(k,deepcopy(v))
        root.setdefault("review_history",[]); root["schema_version"]=self.SCHEMA_VERSION
        return root
    def _all_events(self,state):
        return state.get("memory_system",{}).get("events",[])
    def visible_events(self,state,observer,limit=28):
        events=self._all_events(state)
        if observer in self.NPC_OBSERVERS:
            refs=set(state.get("memory_system",{}).get("npc_memory",{}).get(observer,{}).get("event_refs",[]))
            rows=[e for e in events if e.get("id") in refs]
        elif observer=="village":
            # Social interpretation can use public/multi-witness events, not private conversations.
            rows=[e for e in events if e.get("type") in {"world","work","hobby","story","relationship","encounter"} and (len(e.get("witnesses",[]))>0 or "public" in e.get("tags",[]))]
        elif observer=="chorus":
            # Chorus sees pressure, anomaly and recurrence-adjacent evidence, plus salient reactions.
            rows=[e for e in events if set(e.get("tags",[])) & {"horror","anomaly","bell","recurrence","fear","resistance"} or e.get("type") in {"story","observation"}]
        else:
            rows=list(events)
        rows=rows[-limit:]
        return [{k:e.get(k) for k in ("id","day","type","summary","actors","location","tags","importance")} for e in rows]
    def evidence_packet(self,state,limit=24):
        return self.visible_events(state,"town_mind",limit)
    def observer_context(self,state,observer):
        root=self.migrate(state); slot=root["observers"].get(observer,{})
        role={
            "town_mind":"Infer strategic patterns in what the player values, avoids, trusts, and may be deliberately performing.",
            "chorus":"Infer imperfect fear, attachment, and epistemic vulnerabilities. You are not omniscient and can misread the player.",
            "village":"Infer the social story residents might collectively tell from public conduct and gossip-visible events.",
            "mara":"Interpret the player only from Mara's witnessed history and remembered interactions. Preserve uncertainty and personal bias.",
            "jonah":"Interpret the player only from Jonah's witnessed history and remembered interactions. Preserve uncertainty and personal bias.",
            "mrs_ellis":"Interpret the player only from Mrs Ellis's witnessed history and remembered interactions. Distinguish memory, suspicion, and fact.",
        }.get(observer,"")
        return {"observer":observer,"day":state.get("day",1),"evidence":self.visible_events(state,observer),"existing_hypotheses":deepcopy(slot.get("hypotheses",[])[-8:]),"observer_role":role,"instruction":"Interpret patterns, contradictions, conditional motives, coping strategies, trust habits, and possible deliberate deception. Be fallible. Do not restate numeric traits. Do not claim access to events outside this packet."}
    def apply_review(self,state,observer,result,model_name=None):
        if observer not in self.OBSERVERS or not isinstance(result,dict): return False
        root=self.migrate(state); slot=root["observers"][observer]
        valid_ids={e.get("id") for e in self.visible_events(state,observer,limit=500)}
        rows=result.get("hypotheses",[])
        if not isinstance(rows,list): return False
        accepted=[]
        for row in rows[:6]:
            if not isinstance(row,dict): continue
            claim=str(row.get("claim","")).strip()[:280]
            if len(claim)<12: continue
            support=[x for x in row.get("supporting_evidence",[]) if x in valid_ids][:8]
            contradict=[x for x in row.get("contradicting_evidence",[]) if x in valid_ids][:6]
            if not support: continue
            accepted.append({"claim":claim,"confidence":max(0.05,min(.95,float(row.get("confidence",.5)))),"supporting_evidence":support,"contradicting_evidence":contradict,"possible_test":str(row.get("possible_test",""))[:220],"status":str(row.get("status","active")) if str(row.get("status","active")) in {"active","weakened","retired"} else "active","formed_day":int(state.get("day",1)),"observer":observer})
        if not accepted:return False
        previous=deepcopy(slot.get("hypotheses",[])); day=int(state.get("day",1))
        slot["hypotheses"]=accepted; slot["last_review_day"]=day; slot["revision_count"]+=1; slot["last_model"]=model_name
        slot.setdefault("revision_ledger",[]).append({"day":day,"revision":slot["revision_count"],"previous":previous[:6],"current":deepcopy(accepted),"model":model_name})
        slot["revision_ledger"]=slot["revision_ledger"][-20:]
        root["review_history"].append({"day":day,"observer":observer,"claims":[x["claim"] for x in accepted]}); root["review_history"]=root["review_history"][-60:]
        return True
    def public_summary(self,state,observer="town_mind"):
        slot=self.migrate(state)["observers"].get(observer,{})
        return {"observer":observer,"last_review_day":slot.get("last_review_day",0),"revision_count":slot.get("revision_count",0),"hypotheses":deepcopy(slot.get("hypotheses",[])),"revision_ledger":deepcopy(slot.get("revision_ledger",[]))}
INTERPRETATION_MODEL=InterpretationModel()
