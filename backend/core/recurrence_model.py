"""Part 15 cross-run memory and recurrence architecture.

Recurrence is deliberately lossy. Authoritative facts from a finished run are
archived, then converted into bounded fragments, instincts and asymmetric NPC
echoes. A new run never receives the previous mutable world state wholesale.
"""
from copy import deepcopy

class RecurrenceModel:
    SCHEMA_VERSION=1
    FRAGMENT_TEXT={
        "death":"A moment of danger returns without a complete before or after.",
        "bells":"You wake with the conviction that you have heard Bellwether's bells before.",
        "railway":"The railway halt feels familiar in a way that has nothing to do with maps.",
        "ecology":"Certain changes in birdsong and vegetation feel worth remembering.",
        "memory":"You distrust the certainty of a memory simply because it is vivid.",
        "geography":"A turn in the road can feel wrong before you know why.",
        "routine":"You have the sense that ordinary routines are worth learning carefully.",
        "investigation":"A half-formed pattern survives: separate oddities may share a cause.",
    }
    def runtime_defaults(self):
        return {"schema_version":self.SCHEMA_VERSION,"run_index":1,"completed_runs":[],
                "fragments":[],"instincts":[],"npc_echoes":{},"transition_history":[]}
    def migrate(self,rt):
        d=self.runtime_defaults()
        for k,v in d.items(): rt.setdefault(k,deepcopy(v))
        rt["schema_version"]=self.SCHEMA_VERSION
        return rt
    def _add_unique(self,rows,row,key="id",limit=12):
        if not any(x.get(key)==row.get(key) for x in rows): rows.append(row)
        del rows[:-limit]
    def carry_forward(self,old_state):
        old=deepcopy(old_state.get("recurrence",self.runtime_defaults())); self.migrate(old)
        danger=old_state.get("danger",{}); horror=old_state.get("systemic_horror",{})
        ident=old_state.get("player_identity",{}); inv=old_state.get("mystery_investigation",{})
        rels=old_state.get("relationships",{})
        # Part 17 hardening: Part 12 stores experienced anomaly IDs as strings.
        # Older diagnostic fixtures and possible migrated saves may contain mapping rows.
        # Derive domains from the authoritative runtime domain counters/corruption log and
        # tolerate both representations rather than crashing at the death -> new-run boundary.
        anomaly_domains=set(horror.get("domain_counts",{}).keys())
        anomaly_domains.update(x.get("domain") for x in horror.get("corruption_log",[]) if isinstance(x,dict) and x.get("domain"))
        for x in horror.get("experienced",[]):
            if isinstance(x,dict) and x.get("domain"): anomaly_domains.add(x["domain"])
        summary={"run":old.get("run_index",1),"ended_by":danger.get("terminal_reason") or ("completed" if old_state.get("branch_state",{}).get("run_complete") else "restart"),
                 "day":old_state.get("day",1),"death_hazard":(danger.get("death") or {}).get("hazard_id"),
                 "dominant_traits":deepcopy(ident.get("dominant_traits",[]))[:3],
                 "anomaly_domains":sorted(anomaly_domains),
                 "supported_hypotheses":sorted([k for k,v in inv.get("hypotheses",{}).items() if isinstance(v,dict) and v.get("status")=="supported"])}
        old["completed_runs"].append(summary); old["completed_runs"]=old["completed_runs"][-8:]
        candidates=[]
        if summary["death_hazard"]: candidates.append("death")
        for domain in summary["anomaly_domains"]: candidates.append(domain if domain in self.FRAGMENT_TEXT else "memory")
        if summary["supported_hypotheses"]: candidates.append("investigation")
        if "routine" in summary["dominant_traits"] or "care" in summary["dominant_traits"]: candidates.append("routine")
        for fid in candidates[:3]: self._add_unique(old["fragments"],{"id":fid,"text":self.FRAGMENT_TEXT[fid],"origin_run":summary["run"]})
        for hid in danger.get("warnings_seen",[]): self._add_unique(old["instincts"],{"id":"hazard:"+hid,"hazard_id":hid,"strength":1,"origin_run":summary["run"]})
        if summary["death_hazard"]: self._add_unique(old["instincts"],{"id":"hazard:"+summary["death_hazard"],"hazard_id":summary["death_hazard"],"strength":2,"origin_run":summary["run"]})
        ranked=sorted(((nid,int(r.get("trust",0))+int(r.get("warmth",0))) for nid,r in rels.items() if isinstance(r,dict)),key=lambda x:(-x[1],x[0]))
        if ranked and ranked[0][1]>=3:
            nid,score=ranked[0]; old["npc_echoes"][nid]={"strength":min(3,1+score//8),"origin_run":summary["run"],"kind":"familiarity_without_source"}
        old["run_index"]=int(old.get("run_index",1))+1
        old["transition_history"].append({"from_run":summary["run"],"to_run":old["run_index"],"fragments_carried":[x["id"] for x in old["fragments"][-3:]]})
        old["transition_history"]=old["transition_history"][-8:]
        return old
    def apply_to_new_run(self,state,recurrence):
        state["recurrence"]=deepcopy(recurrence); danger=state.get("danger",{})
        known={x.get("hazard_id") for x in recurrence.get("instincts",[]) if x.get("hazard_id")}
        danger.setdefault("warnings_seen",[])
        for hid in sorted(known):
            if hid not in danger["warnings_seen"]: danger["warnings_seen"].append(hid)
        return state
    def opening_echoes(self,recurrence):
        return [x.get("text") for x in recurrence.get("fragments",[])[-2:] if x.get("text")]

RECURRENCE_MODEL=RecurrenceModel()
