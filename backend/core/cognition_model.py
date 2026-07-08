"""v0.7.1 bounded NPC cognition and long-term memory interpretation.

Cognition is subjective state. It never creates objective facts. Beliefs reference
catalogue facts or witnessed structured events; impressions, suspicions and concerns
remain explicitly subjective and confidence-bounded.
"""
from copy import deepcopy

class CognitionModel:
    SCHEMA_VERSION = 1
    BELIEF_KINDS = {"fact", "belief", "rumour", "impression", "suspicion"}

    def runtime_defaults(self, npc_ids):
        return {"schema_version": self.SCHEMA_VERSION, "npcs": {nid: self._slot() for nid in npc_ids}}

    def _slot(self):
        return {
            "beliefs": [], "impressions": [], "concerns": [], "unresolved_questions": [],
            "short_term_goals": [], "ambitions": [], "last_refresh_day": 0,
            "revision_log": [], "forgotten_count": 0, "bootstrap_complete": False,
        }

    def migrate(self, state, npc_ids):
        root = state.setdefault("npc_cognition", self.runtime_defaults(npc_ids))
        root.setdefault("schema_version", self.SCHEMA_VERSION)
        root.setdefault("npcs", {})
        for nid in npc_ids:
            slot = root["npcs"].setdefault(nid, self._slot())
            for k, v in self._slot().items(): slot.setdefault(k, deepcopy(v))
        return root

    def add_belief(self, state, npc_id, kind, text, confidence=.5, source_type="event", source_id=None, subject=None):
        if kind not in self.BELIEF_KINDS: return False
        root = self.migrate(state, list(state.get("npcs", {})))
        slot = root["npcs"].get(npc_id)
        if slot is None: return False
        text = str(text).strip()[:240]
        if not text: return False
        row = {"kind": kind, "text": text, "confidence": round(max(0.0,min(1.0,float(confidence))),3),
               "source_type": source_type, "source_id": source_id, "subject": subject,
               "day": int(state.get("day",1)), "last_reinforced_day": int(state.get("day",1))}
        # Reinforce exact same subjective proposition rather than duplicating it.
        for old in slot["beliefs"]:
            if old.get("kind")==kind and old.get("text","").casefold()==text.casefold():
                old["confidence"] = round(min(1.0, max(float(old.get("confidence",0)), row["confidence"]) + .08),3)
                old["last_reinforced_day"] = row["day"]
                return True
        slot["beliefs"].append(row); slot["beliefs"] = slot["beliefs"][-40:]
        return True

    def revise_belief(self, state, npc_id, text, new_confidence, reason, source_id=None):
        root=self.migrate(state,list(state.get("npcs",{}))); slot=root["npcs"].get(npc_id)
        if not slot: return False
        for row in slot["beliefs"]:
            if row.get("text","").casefold()==str(text).casefold():
                old=float(row.get("confidence",0)); row["confidence"]=round(max(0,min(1,float(new_confidence))),3)
                slot["revision_log"].append({"day":state.get("day",1),"text":row["text"],"from":old,"to":row["confidence"],"reason":str(reason)[:160],"source_id":source_id})
                slot["revision_log"]=slot["revision_log"][-30:]
                return True
        return False

    def add_concern(self,state,npc_id,text,urgency=.5,source_id=None):
        root=self.migrate(state,list(state.get("npcs",{}))); slot=root["npcs"].get(npc_id)
        if not slot:return False
        row={"text":str(text)[:200],"urgency":round(max(0,min(1,float(urgency))),3),"source_id":source_id,"day":state.get("day",1)}
        if row["text"] and all(x.get("text")!=row["text"] for x in slot["concerns"]): slot["concerns"].append(row)
        slot["concerns"]=slot["concerns"][-12:]; return True

    def set_goal(self,state,npc_id,text,horizon="short",priority=.5,source="engine"):
        root=self.migrate(state,list(state.get("npcs",{}))); slot=root["npcs"].get(npc_id)
        if not slot:return False
        key="ambitions" if horizon=="long" else "short_term_goals"
        row={"text":str(text)[:180],"priority":round(max(0,min(1,float(priority))),3),"source":source,"day":state.get("day",1)}
        if row["text"] and all(x.get("text")!=row["text"] for x in slot[key]): slot[key].append(row)
        slot[key]=slot[key][-8:]; return True

    def ingest_event(self,state,npc_id,event_id):
        mem=state.get("memory_system",{}); event=next((e for e in mem.get("events",[]) if e.get("id")==event_id),None)
        if not event or npc_id not in set(event.get("actors",[])+event.get("witnesses",[])): return False
        # Store only an explicitly subjective interpretation backed by a witnessed event.
        return self.add_belief(state,npc_id,"belief",event.get("summary",""),min(.9,.35+.12*int(event.get("importance",1))),"witnessed_event",event_id)

    def bootstrap_authoritative_context(self, state, npc_catalogue, knowledge_model):
        """Seed cognition from authored lives and existing bounded knowledge without inventing facts."""
        root=self.migrate(state,list(state.get("npcs",{})))
        knowledge=state.get("npc_knowledge",{}).get("npcs",{})
        for nid, slot in root["npcs"].items():
            if slot.get("bootstrap_complete"): continue
            authored=npc_catalogue.npcs.get(nid,{})
            if not slot["ambitions"]:
                for thread in authored.get("personal_threads",[])[:2]:
                    tid=thread.get("id","").replace("_"," ").strip()
                    if tid: self.set_goal(state,nid,f"See where {tid} leads.","long",.55,"authored_personal_thread")
            if not slot["short_term_goals"]:
                obligations=authored.get("obligations",[])
                for ob in obligations[:2]:
                    purpose=str(ob.get("purpose","routine")).replace("_"," ")
                    self.set_goal(state,nid,f"Attend to {purpose}.","short",min(.9,float(ob.get("priority",50))/100),"authored_obligation")
            # Mirror catalogue-backed knowledge as subjective cognition with explicit variant type.
            for fid,b in knowledge.get(nid,{}).get("beliefs",{}).items():
                if fid not in knowledge_model.facts: continue
                variant=b.get("variant","truth"); kind="fact" if variant=="truth" and b.get("source")=="authored" else "rumour"
                self.add_belief(state,nid,kind,knowledge_model.text(fid,variant),b.get("confidence",.5),"knowledge_catalogue",fid)
            slot["bootstrap_complete"]=True
        return root

    def fade(self,state):
        """Daily bounded forgetting: low-confidence subjective beliefs fade; facts are retained."""
        root=self.migrate(state,list(state.get("npcs",{}))); day=int(state.get("day",1))
        for slot in root["npcs"].values():
            if int(slot.get("last_refresh_day",0))>=day: continue
            kept=[]
            for row in slot["beliefs"]:
                if row.get("kind")=="fact": kept.append(row); continue
                age=max(0,day-int(row.get("last_reinforced_day",row.get("day",day))))
                conf=max(0.0,float(row.get("confidence",0))-.025*age)
                row["confidence"]=round(conf,3)
                if conf>=.15: kept.append(row)
                else: slot["forgotten_count"]+=1
            slot["beliefs"]=kept[-40:]; slot["last_refresh_day"]=day

    def context(self,state,npc_id,limit=6):
        root=self.migrate(state,list(state.get("npcs",{}))); slot=root["npcs"].get(npc_id,self._slot())
        beliefs=sorted(slot["beliefs"],key=lambda x:(x.get("confidence",0),x.get("last_reinforced_day",0)),reverse=True)[:limit]
        return {"beliefs":deepcopy(beliefs),"impressions":deepcopy(slot["impressions"][-4:]),"concerns":deepcopy(slot["concerns"][-4:]),
                "unresolved_questions":deepcopy(slot["unresolved_questions"][-4:]),"short_term_goals":deepcopy(slot["short_term_goals"][-3:]),"ambitions":deepcopy(slot["ambitions"][-3:])}

COGNITION_MODEL=CognitionModel()
