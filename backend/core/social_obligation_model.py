"""v3.10 persistent social obligations and self-generated NPC goals.

Interpretive AI may propose purpose and intent. The engine validates actors, target,
source facts and capability vocabulary; lifecycle and consequences remain deterministic.
"""
from copy import deepcopy

class SocialObligationModel:
    CORE=("mara","jonah","mrs_ellis")
    GOAL_CAPABILITIES={
      "seek_information","compare_evidence","ask_for_help","offer_help",
      "repair_relationship","fulfil_obligation","protect_someone","share_concern",
      "withhold_information","stabilize_work","investigate_pattern"
    }
    def defaults(self):
        return {"schema_version":1,"obligations":[],"goals":{},"history":[],"next_id":1}
    def migrate(self,s):
        rt=s.setdefault("social_obligations",deepcopy(self.defaults()))
        for k,v in self.defaults().items():rt.setdefault(k,deepcopy(v))
        return rt
    def create_obligation(self,s,debtor,creditor,kind,content,causes,source,days=5):
        if debtor not in self.CORE or creditor not in set(self.CORE)|{"player","village"}:return None
        rt=self.migrate(s); oid=f"obl_{rt['next_id']}";rt['next_id']+=1
        row={"id":oid,"created_day":int(s.get("day",1)),"due_day":int(s.get("day",1))+max(1,int(days)),
             "debtor":debtor,"creditor":creditor,"kind":str(kind)[:48],"content":str(content)[:280],
             "causes":[str(x) for x in causes if x][:8],"source":source,"status":"active","attempts":0}
        rt["obligations"].append(row);rt["obligations"]=rt["obligations"][-120:]
        from backend.core.causal_history_model import CAUSAL_HISTORY_MODEL
        CAUSAL_HISTORY_MODEL.link(s,"obligation",oid,row["causes"],row["content"],source)
        return row
    def context_for(self,s,npc):
        rt=self.migrate(s); facts=s.get("causal_history",{}).get("social_facts",[])
        relevant=[x for x in facts if x.get("status")=="active" and npc in (x.get("subject"),x.get("target"))][-12:]
        obligations=[x for x in rt["obligations"] if x.get("status")=="active" and npc in (x.get("debtor"),x.get("creditor"))][-8:]
        project=s.get("npc_epistemic_projects",{}).get("projects",{}).get(npc,{})
        return {"npc":npc,"day":s.get("day",1),"social_facts":deepcopy(relevant),"obligations":deepcopy(obligations),
                "epistemic_project":deepcopy(project),"current_goal":deepcopy(rt["goals"].get(npc)),
                "legal_capabilities":sorted(self.GOAL_CAPABILITIES),
                "instruction":"Infer one grounded goal from supplied facts. Purpose may be novel; capability must be legal. Cite source ids exactly."}
    def apply_goal(self,s,npc,result,model=None):
        if npc not in self.CORE or not isinstance(result,dict):return False
        cap=str(result.get("capability","")); purpose=str(result.get("purpose","")).strip(); sources=result.get("source_ids",[])
        if cap not in self.GOAL_CAPABILITIES or len(purpose)<12 or not isinstance(sources,list) or not sources:return False
        ctx=self.context_for(s,npc); valid={x.get("id") for x in ctx["social_facts"]+ctx["obligations"] if x.get("id")}
        if not set(map(str,sources)).issubset(valid):return False
        rt=self.migrate(s); old=deepcopy(rt["goals"].get(npc)); gid=f"goal_{npc}_{s.get('day',1)}_{len(rt['history'])+1}"
        row={"id":gid,"npc":npc,"formed_day":int(s.get("day",1)),"purpose":purpose[:320],"capability":cap,
             "reason":str(result.get("reason",""))[:300],"source_ids":[str(x) for x in sources][:8],"status":"active","model":model}
        if old and old.get("status")=="active":old["status"]="superseded";rt["history"].append(old)
        rt["goals"][npc]=row;rt["history"].append(deepcopy(row));rt["history"]=rt["history"][-80:]
        from backend.core.causal_history_model import CAUSAL_HISTORY_MODEL
        CAUSAL_HISTORY_MODEL.link(s,"npc_goal",gid,row["source_ids"],purpose,"npc_goal_reasoning")
        return True
    def record_intention_outcome(self,s,npc,action_id,kind,destination):
        """Turn an executed legal NPC action into bounded evidence about goal progress.

        This does not let the LLM declare success. The engine compares the executed
        action kind with the active goal capability and records progress/contradiction.
        """
        rt=self.migrate(s); goal=rt.get("goals",{}).get(npc)
        if not goal or goal.get("status")!="active": return None
        aligned={
          "seek_information":{"social","planning","errand"}, "compare_evidence":{"planning","work"},
          "ask_for_help":{"social"}, "offer_help":{"social","work","chore"},
          "repair_relationship":{"social"}, "fulfil_obligation":{"delivery","errand","work","social"},
          "protect_someone":{"social","routine"}, "share_concern":{"social"},
          "withhold_information":{"routine","work","planning"}, "stabilize_work":{"work","delivery","chore"},
          "investigate_pattern":{"planning","work","errand"}
        }
        match=kind in aligned.get(goal.get("capability"),set())
        row={"day":int(s.get("day",1)),"npc":npc,"goal_id":goal.get("id"),"action_id":action_id,
             "kind":kind,"destination":destination,"outcome":"advanced" if match else "diverged"}
        goal.setdefault("outcomes",[]).append(row); goal["outcomes"]=goal["outcomes"][-16:]
        goal["progress_evidence"]=sum(1 for x in goal["outcomes"] if x.get("outcome")=="advanced")
        goal["divergence_evidence"]=sum(1 for x in goal["outcomes"] if x.get("outcome")=="diverged")
        rt["history"].append(deepcopy(row));rt["history"]=rt["history"][-80:]
        return row

    def revise_goal_lifecycle(self,s,npc):
        rt=self.migrate(s); goal=rt.get("goals",{}).get(npc)
        if not goal or goal.get("status")!="active": return None
        advanced=int(goal.get("progress_evidence",0)); diverged=int(goal.get("divergence_evidence",0))
        if advanced>=3:
            goal["status"]="progressed"; goal["resolved_day"]=int(s.get("day",1)); reason="repeated grounded actions advanced the goal"
        elif diverged>=4 and advanced==0:
            goal["status"]="reconsider"; goal["resolved_day"]=int(s.get("day",1)); reason="repeated behaviour diverged from the stated goal"
        else: return None
        event={"day":int(s.get("day",1)),"npc":npc,"goal_id":goal.get("id"),"status":goal["status"],"reason":reason}
        rt["history"].append(deepcopy(event));rt["history"]=rt["history"][-80:]
        return event
    def daily_tick(self,s):
        rt=self.migrate(s);day=int(s.get("day",1));out=[]
        for npc in self.CORE:
            event=self.revise_goal_lifecycle(s,npc)
            if event: out.append({"type":"goal_lifecycle",**event})
        for o in rt["obligations"]:
            if o.get("status")!="active":continue
            if day>int(o.get("due_day",day)):
                o["status"]="overdue";out.append({"type":"overdue","id":o["id"],"debtor":o["debtor"],"creditor":o["creditor"]})
                from backend.core.causal_history_model import CAUSAL_HISTORY_MODEL
                CAUSAL_HISTORY_MODEL.add_social_fact(s,"resentment",o["creditor"],o["debtor"],f"An unmet obligation has changed how {o['creditor']} regards {o['debtor']}.",[o["id"]],"obligation_lifecycle")
        return out
    def public(self,s):
        rt=self.migrate(s);return {"active_obligations":deepcopy([x for x in rt["obligations"] if x.get("status")=="active"][-20:]),"goals":deepcopy(rt["goals"]),"recent_history":deepcopy(rt["history"][-20:])}
SOCIAL_OBLIGATION_MODEL=SocialObligationModel()
