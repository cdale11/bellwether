"""v3.6.0 epistemic NPC projects.

LLM owns fallible reasoning (belief/question/revision/disclosure preference).
The deterministic engine owns legal attempts, observations, timing and state mutation.
"""
from copy import deepcopy

class NPCProjectModel:
    SCHEMA_VERSION=1
    CORE=("mara","jonah","mrs_ellis")
    ATTEMPTS={
      "mara":[("inspect_own_garden","Inspect a familiar garden for comparison"),("compare_weather_notes","Compare recent weather with observed plant changes"),("ask_resident_gardener","Ask a resident about similar growth elsewhere"),("inspect_ashcroft_edge","Inspect the edge of Ashcroft Cottage grounds")],
      "jonah":[("review_bakery_ledger","Review recent bakery supply and sales patterns"),("check_delivery_route","Check whether delivery disruption explains shortages"),("ask_supplier","Ask a supplier about recent irregularities"),("compare_busy_days","Compare exhaustion with customer and delivery patterns")],
      "mrs_ellis":[("compare_parish_notes","Compare two remembered parish references"),("check_archive_index","Check whether an archive index supports the memory"),("ask_old_resident","Ask another long-term resident without leading them"),("revisit_location_memory","Revisit a place connected to an uncertain memory")],
    }
    OBS={
      "inspect_own_garden":"The comparison garden shows ordinary variation, but not the same pattern.","compare_weather_notes":"Weather alone does not cleanly explain the timing.","ask_resident_gardener":"Another gardener recalls something similar, but places it in a different year.","inspect_ashcroft_edge":"The strongest irregularity appears close to the cottage boundary, though cause remains unknown.",
      "review_bakery_ledger":"The ledger suggests strain comes from several small disruptions rather than one collapse.","check_delivery_route":"Road disruption plausibly explains some missed supply, but not all of the fatigue.","ask_supplier":"The supplier reports delays that partly support the working explanation.","compare_busy_days":"Exhaustion does not track customer volume as neatly as expected.",
      "compare_parish_notes":"Two references agree on a place but disagree on timing.","check_archive_index":"The index confirms a record existed, but not the remembered wording.","ask_old_resident":"The other resident remembers the matter differently without obvious deception.","revisit_location_memory":"The place is familiar, but the memory attached to it remains uncertain."
    }
    def runtime_defaults(self): return {"schema_version":1,"projects":{},"history":[],"last_advance_day":0}
    def migrate(self,s):
        rt=s.setdefault("npc_epistemic_projects",deepcopy(self.runtime_defaults()))
        for k,v in self.runtime_defaults().items(): rt.setdefault(k,deepcopy(v))
        rt["schema_version"]=1; return rt
    def legal_attempts(self,s,npc):
        p=self.migrate(s)["projects"].get(npc,{})
        used=set(p.get("attempt_history",[]))
        return [{"id":i,"label":label} for i,label in self.ATTEMPTS.get(npc,[]) if i not in used]
    def reasoning_context(self,s,npc):
        p=deepcopy(self.migrate(s)["projects"].get(npc,{}))
        interp=deepcopy(s.get("interpretation_system",{}).get("observers",{}).get(npc,{}).get("hypotheses",[]))
        return {"npc":npc,"day":s.get("day",1),"existing_project":p,"npc_interpretations":interp[-4:],"social_context":deepcopy(s.get("social_obligations",{}).get("goals",{}).get(npc)),"active_obligations":[deepcopy(x) for x in s.get("social_obligations",{}).get("obligations",[]) if x.get("status")=="active" and npc in (x.get("debtor"),x.get("creditor"))][-6:],"legal_attempts":self.legal_attempts(s,npc),"instruction":"Maintain one grounded inquiry. Revise belief from observations. Choose only a legal_attempt id. You may decide disclosure stance, but cannot invent discoveries or world facts."}
    def apply_reasoning(self,s,npc,result,model=None):
        if npc not in self.CORE or not isinstance(result,dict): return False
        rt=self.migrate(s); legal={x[0] for x in self.ATTEMPTS[npc]}; attempt=str(result.get("next_attempt",""))
        if attempt not in legal or attempt in rt["projects"].get(npc,{}).get("attempt_history",[]): return False
        belief=str(result.get("belief","")).strip()[:260]; question=str(result.get("question","")).strip()[:220]
        if len(belief)<10 or len(question)<8:return False
        old=deepcopy(rt["projects"].get(npc,{})); p=rt["projects"].setdefault(npc,{})
        p.update({"npc":npc,"belief":belief,"question":question,"next_attempt":attempt,"reason":str(result.get("reason",""))[:220],"disclosure":str(result.get("disclosure","uncertain")) if str(result.get("disclosure","uncertain")) in {"open","selective","conceal","uncertain"} else "uncertain","status":"active","last_reasoning_day":int(s.get("day",1)),"model":model})
        p.setdefault("observations",old.get("observations",[]));p.setdefault("attempt_history",old.get("attempt_history",[]));p.setdefault("revision_history",old.get("revision_history",[]))
        if old.get("belief") and old.get("belief")!=belief:p["revision_history"].append({"day":s.get("day",1),"from":old.get("belief"),"to":belief,"observation":old.get("observations",[])[-1] if old.get("observations") else None})
        p["revision_history"]=p["revision_history"][-16:]; return True
    def advance_day(self,s):
        rt=self.migrate(s); day=int(s.get("day",1)); out=[]
        if rt.get("last_advance_day")==day:return out
        rt["last_advance_day"]=day
        for npc,p in rt["projects"].items():
            aid=p.get("next_attempt")
            if p.get("status")!="active" or not aid or aid in p.get("attempt_history",[]):continue
            obs=self.OBS.get(aid); p.setdefault("attempt_history",[]).append(aid);p.setdefault("observations",[]).append({"day":day,"attempt":aid,"text":obs});p["observations"]=p["observations"][-12:];p["next_attempt"]=None
            row={"day":day,"npc":npc,"attempt":aid,"observation":obs};rt["history"].append(row);out.append(row)
        rt["history"]=rt["history"][-80:];return out
    def public(self,s):return deepcopy(self.migrate(s))
NPC_PROJECT_MODEL=NPCProjectModel()
