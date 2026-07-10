"""Cross-run recurrence architecture (v0.9.0).

Recurrence is lossy and asymmetric. Completed runs are compressed into bounded
fragments, instincts, anchors, story residues and NPC echoes. Nothing here copies
the mutable village wholesale into a new run.
"""
from copy import deepcopy

class RecurrenceModel:
    SCHEMA_VERSION=2
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
    ANCHOR_TEXT={
        "home":"The cottage feels less like an inheritance than somewhere your hands already know.",
        "community":"Faces in the village carry a warmth that arrives before explanation.",
        "inquiry":"A question has survived even though its wording has not.",
        "institution":"The village's records and routines feel familiar before their details do.",
    }
    STORY_FLAG_ALLOWLIST=("reached_cottage","read_letter","met_jonah","met_mara")

    def runtime_defaults(self):
        return {"schema_version":self.SCHEMA_VERSION,"run_index":1,"completed_runs":[],
                "fragments":[],"latent_fragments":[],"returned_fragments":[],"instincts":[],
                "anchors":{},"story_residues":[],"npc_echoes":{},"transition_history":[],
                "daily_return_log":[],"last_return_day":0,"awakening_history":[]}

    def migrate(self,rt):
        d=self.runtime_defaults()
        for k,v in d.items(): rt.setdefault(k,deepcopy(v))
        # Schema-1 fragments were all immediately visible. Preserve them as returned.
        if int(rt.get("schema_version",1))<2 and rt.get("fragments"):
            for row in rt["fragments"]:
                if not any(x.get("id")==row.get("id") for x in rt["returned_fragments"]):
                    rt["returned_fragments"].append(deepcopy(row))
        rt["schema_version"]=self.SCHEMA_VERSION
        return rt

    def _add_unique(self,rows,row,key="id",limit=16):
        existing=next((x for x in rows if x.get(key)==row.get(key)),None)
        if existing:
            # Repeated cross-run residue strengthens provenance without duplicating rows.
            existing["recurrences"]=min(5,int(existing.get("recurrences",1))+1)
            existing["origin_run"]=min(int(existing.get("origin_run",row.get("origin_run",1))),int(row.get("origin_run",1)))
        else: rows.append(row)
        del rows[:-limit]

    def _derive_anchors(self,state,run_index):
        out=[]; rels=state.get("relationships",{})
        strong=sum(1 for r in rels.values() if isinstance(r,dict) and int(r.get("trust",0))+int(r.get("affinity",0))>=7)
        life=state.get("player_life",{}); content=state.get("content_progression",{})
        if int(life.get("cottage_care",0))>=20 or content.get("home_restoration",{}).get("completed"):
            out.append(("home",min(3,1+int(life.get("cottage_care",0))//35)))
        if strong>=1: out.append(("community",min(3,1+strong//2)))
        inv=state.get("mystery_investigation",{})
        supported=sum(1 for v in inv.get("hypotheses",{}).values() if isinstance(v,dict) and v.get("status")=="supported")
        if supported: out.append(("inquiry",min(3,1+supported//2)))
        jobs=state.get("jobs",{}); social=state.get("social_consequences",{})
        if jobs.get("current_job") or social.get("open_commitments"): out.append(("institution",1))
        return [{"id":aid,"strength":strength,"origin_run":run_index,"text":self.ANCHOR_TEXT[aid]} for aid,strength in out]

    def carry_forward(self,old_state):
        old=deepcopy(old_state.get("recurrence",self.runtime_defaults())); self.migrate(old)
        danger=old_state.get("danger",{}); horror=old_state.get("systemic_horror",{})
        ident=old_state.get("player_identity",{}); inv=old_state.get("mystery_investigation",{}); rels=old_state.get("relationships",{})
        run=int(old.get("run_index",1))
        anomaly_domains=set(horror.get("domain_counts",{}).keys())
        anomaly_domains.update(x.get("domain") for x in horror.get("corruption_log",[]) if isinstance(x,dict) and x.get("domain"))
        for x in horror.get("experienced",[]):
            if isinstance(x,dict) and x.get("domain"): anomaly_domains.add(x["domain"])
        summary={"run":run,"ended_by":danger.get("terminal_reason") or ("completed" if old_state.get("branch_state",{}).get("run_complete") else "restart"),
                 "day":old_state.get("day",1),"death_hazard":(danger.get("death") or {}).get("hazard_id"),
                 "dominant_traits":deepcopy(ident.get("dominant_traits",[]))[:3],"anomaly_domains":sorted(anomaly_domains),
                 "supported_hypotheses":sorted([k for k,v in inv.get("hypotheses",{}).items() if isinstance(v,dict) and v.get("status")=="supported"])}
        old["completed_runs"].append(summary); old["completed_runs"]=old["completed_runs"][-8:]

        candidates=[]
        if summary["death_hazard"]: candidates.append("death")
        for domain in summary["anomaly_domains"]: candidates.append(domain if domain in self.FRAGMENT_TEXT else "memory")
        if summary["supported_hypotheses"]: candidates.append("investigation")
        if "routine" in summary["dominant_traits"] or "care" in summary["dominant_traits"]: candidates.append("routine")
        for order,fid in enumerate(list(dict.fromkeys(candidates))[:3]):
            row={"id":fid,"text":self.FRAGMENT_TEXT[fid],"origin_run":run,"return_after_day":1+order*2,"kind":"fragment"}
            self._add_unique(old["fragments"],deepcopy(row))
            if not any(x.get("id")==fid for x in old["returned_fragments"]): self._add_unique(old["latent_fragments"],deepcopy(row))

        for hid in danger.get("warnings_seen",[]): self._add_unique(old["instincts"],{"id":"hazard:"+hid,"hazard_id":hid,"strength":1,"origin_run":run,"kind":"instinct"})
        if summary["death_hazard"]: self._add_unique(old["instincts"],{"id":"hazard:"+summary["death_hazard"],"hazard_id":summary["death_hazard"],"strength":2,"origin_run":run,"kind":"instinct"})

        for anchor in self._derive_anchors(old_state,run):
            current=old["anchors"].get(anchor["id"])
            if current: current["strength"]=min(3,max(int(current.get("strength",1)),anchor["strength"])+1); current["last_reinforced_run"]=run
            else: old["anchors"][anchor["id"]]=anchor

        flags=old_state.get("flags",{})
        residue={"origin_run":run,"flags":[f for f in self.STORY_FLAG_ALLOWLIST if flags.get(f)],"supported_hypotheses":summary["supported_hypotheses"][:4]}
        if residue["flags"] or residue["supported_hypotheses"]: old["story_residues"].append(residue); old["story_residues"]=old["story_residues"][-8:]

        ranked=sorted(((nid,int(r.get("trust",0))+int(r.get("affinity",0))+int(r.get("familiarity",0))//2) for nid,r in rels.items() if isinstance(r,dict)),key=lambda x:(-x[1],x[0]))
        # Asymmetry is intentional: only independently strong ties carry an echo, with different kinds.
        kinds=("familiarity_without_source","protective_hesitation","misplaced_recognition")
        for idx,(nid,score) in enumerate(ranked[:3]):
            if score<5: continue
            prior=old["npc_echoes"].get(nid,{})
            old["npc_echoes"][nid]={"strength":min(3,max(int(prior.get("strength",0)),1+score//10)),"origin_run":run,
                                     "kind":kinds[idx%len(kinds)],"activation_day":1+idx*2,"activated":False}

        old["run_index"]=run+1
        carried=[x["id"] for x in old["latent_fragments"][:4]]
        old["transition_history"].append({"from_run":run,"to_run":old["run_index"],"latent_fragments":carried,"anchors":sorted(old["anchors"])})
        old["transition_history"]=old["transition_history"][-8:]
        old["last_return_day"]=0; old["daily_return_log"]=[]
        return old

    def awakening_location(self,recurrence):
        anchors=recurrence.get("anchors",{})
        if int(anchors.get("home",{}).get("strength",0))>=2: return "ashcroft_cottage"
        if int(anchors.get("community",{}).get("strength",0))>=2: return "village_green"
        return "bus_stop"

    def apply_to_new_run(self,state,recurrence):
        state["recurrence"]=deepcopy(recurrence); rec=state["recurrence"]; self.migrate(rec)
        danger=state.get("danger",{}); known={x.get("hazard_id") for x in rec.get("instincts",[]) if x.get("hazard_id")}
        danger.setdefault("warnings_seen",[])
        for hid in sorted(known):
            if hid not in danger["warnings_seen"]: danger["warnings_seen"].append(hid)
        loc=self.awakening_location(rec); state["location"]=loc
        rec["awakening_history"].append({"run":rec["run_index"],"location":loc,"anchor_basis":sorted(rec.get("anchors",{}))}); rec["awakening_history"]=rec["awakening_history"][-8:]
        # Story continuity is residue, not a wholesale quest-state copy. Canon systems can consult this explicitly.
        state.setdefault("story_integration",{}).setdefault("recurrence_residues",deepcopy(rec.get("story_residues",[])[-3:]))
        return state

    def advance_day(self,state):
        rec=state.get("recurrence",{}); self.migrate(rec); day=int(state.get("day",1))
        if day<=int(rec.get("last_return_day",0)): return []
        returned=[]
        eligible=[x for x in rec.get("latent_fragments",[]) if int(x.get("return_after_day",1))<=day]
        if eligible:
            row=deepcopy(sorted(eligible,key=lambda x:(int(x.get("return_after_day",1)),x.get("id","")))[0])
            rec["latent_fragments"]=[x for x in rec["latent_fragments"] if x.get("id")!=row.get("id")]
            self._add_unique(rec["returned_fragments"],row)
            returned.append({"speaker":"Memory","text":row.get("text","")})
        for nid,echo in sorted(rec.get("npc_echoes",{}).items()):
            if not echo.get("activated") and day>=int(echo.get("activation_day",1)):
                echo["activated"]=True
                returned.append({"speaker":"Bellwether","text":f"A trace of recognition has begun to surface around {nid.replace('_',' ').title()}, though neither of you can name its source."})
                break
        if returned: rec["daily_return_log"].append({"day":day,"events":deepcopy(returned)}); rec["daily_return_log"]=rec["daily_return_log"][-20:]
        rec["last_return_day"]=day
        return returned

    def opening_echoes(self,recurrence):
        self.migrate(recurrence)
        out=[]
        anchors=recurrence.get("anchors",{})
        strongest=sorted(anchors.values(),key=lambda x:(-int(x.get("strength",0)),x.get("id","")))[:1]
        out.extend(x.get("text") for x in strongest if x.get("text"))
        # Only already-returned fragments can surface immediately; latent fragments return over days.
        out.extend(x.get("text") for x in recurrence.get("returned_fragments",[])[-1:] if x.get("text"))
        return out[:2]

    def developer_context(self,state):
        rec=state.get("recurrence",{}); self.migrate(rec)
        return {"schema_version":rec["schema_version"],"run_index":rec["run_index"],"anchors":deepcopy(rec["anchors"]),
                "latent_fragments":deepcopy(rec["latent_fragments"]),"returned_fragments":deepcopy(rec["returned_fragments"]),
                "npc_echoes":deepcopy(rec["npc_echoes"]),"story_residues":deepcopy(rec["story_residues"][-3:]),
                "awakening_history":deepcopy(rec["awakening_history"][-5:])}

RECURRENCE_MODEL=RecurrenceModel()
