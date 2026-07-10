"""v0.5.2 persistent player social consequences.

Only explicit, validated social acts become structured state. Dialogue prose is never
objective truth. This model stores commitments, favours, invitations, grievances,
apologies, and relationship-specific shared history with bounded effects.
"""
from copy import deepcopy
import re

class SocialConsequenceModel:
    SCHEMA_VERSION=1
    ACT_TYPES={"promise","favour","invitation","apology","insult","disclosure","request","agreement","refusal"}
    OPEN_TYPES={"promise","favour","invitation","request"}
    def runtime_defaults(self,npc_ids):
        return {"schema_version":self.SCHEMA_VERSION,"next_act_id":1,"acts":[],
                "by_npc":{nid:[] for nid in npc_ids},"grievances":{nid:[] for nid in npc_ids},
                "favours":{nid:{"owed_to_player":0,"owed_by_player":0} for nid in npc_ids},
                "shared_history":{nid:[] for nid in npc_ids},"gossip_log":[]}
    def migrate(self,state,npc_ids):
        d=self.runtime_defaults(npc_ids); sc=state.setdefault("social_consequences",deepcopy(d))
        for k,v in d.items(): sc.setdefault(k,deepcopy(v))
        for nid in npc_ids:
            sc["by_npc"].setdefault(nid,[]); sc["grievances"].setdefault(nid,[])
            sc["favours"].setdefault(nid,{"owed_to_player":0,"owed_by_player":0})
            sc["shared_history"].setdefault(nid,[])
        return sc
    def record_act(self,state,npc_id,act_type,summary,explicit=True,status="open",metadata=None):
        if act_type not in self.ACT_TYPES or npc_id not in state.get("npcs",{}): return None
        sc=self.migrate(state,list(state.get("npcs",{})))
        aid=f"soc_{sc['next_act_id']:06d}"; sc['next_act_id']+=1
        row={"id":aid,"type":act_type,"npc_id":npc_id,"summary":str(summary)[:240],
             "day":int(state.get("day",1)),"minute":int(state.get("minute",0)),
             "explicit":bool(explicit),"status":status,"metadata":deepcopy(metadata or {})}
        sc["acts"].append(row); sc["acts"]=sc["acts"][-300:]
        sc["by_npc"][npc_id].append(aid); sc["by_npc"][npc_id]=sc["by_npc"][npc_id][-80:]
        hist=sc["shared_history"][npc_id]; hist.append({"act_id":aid,"type":act_type,"summary":row["summary"],"day":row["day"],"status":status})
        sc["shared_history"][npc_id]=hist[-40:]
        if act_type=="insult":
            sc["grievances"][npc_id].append({"act_id":aid,"summary":row["summary"],"day":row["day"],"resolved":False})
            sc["grievances"][npc_id]=sc["grievances"][npc_id][-20:]
        return aid
    def resolve_grievance(self,state,npc_id,reason):
        sc=self.migrate(state,list(state.get("npcs",{})))
        open_rows=[g for g in sc["grievances"].get(npc_id,[]) if not g.get("resolved")]
        if not open_rows:return None
        row=open_rows[-1]; row["resolved"]=True; row["resolved_day"]=state.get("day",1); row["resolution"]=str(reason)[:180]
        return row["act_id"]
    def context(self,state,npc_id,limit=8):
        sc=self.migrate(state,list(state.get("npcs",{})))
        ids=set(sc["by_npc"].get(npc_id,[])); acts=[a for a in sc["acts"] if a["id"] in ids]
        return {"recent_acts":deepcopy(acts[-limit:]),
                "open_commitments":deepcopy([a for a in acts if a["type"] in self.OPEN_TYPES and a.get("status")=="open"][-5:]),
                "open_grievances":deepcopy([g for g in sc["grievances"].get(npc_id,[]) if not g.get("resolved")][-4:]),
                "favours":deepcopy(sc["favours"].get(npc_id,{})),
                "shared_history":deepcopy(sc["shared_history"].get(npc_id,[])[-limit:])}
    def relationship_stage(self,relationship):
        aff=int(relationship.get("affinity",0)); trust=int(relationship.get("trust",0)); fam=int(relationship.get("familiarity",0))
        if trust<=-20 or aff<=-25:return "hostile"
        if trust<0 or aff<0:return "strained"
        if fam>=35 and trust>=25 and aff>=25:return "close"
        if fam>=15 and trust>=8:return "friendly"
        if fam>=5:return "acquainted"
        return "new"
    def record_gossip(self,state,source,target,fact_id,variant,confidence):
        sc=self.migrate(state,list(state.get("npcs",{})))
        row={"day":state.get("day",1),"minute":state.get("minute",0),"source":source,"target":target,"fact_id":fact_id,"variant":variant,"confidence":round(float(confidence),3)}
        sc["gossip_log"].append(row); sc["gossip_log"]=sc["gossip_log"][-120:]; return row
    def extract_explicit_player_act(self,text):
        """Conservative deterministic extraction: only strong first-person forms."""
        raw=(text or "").strip(); low=raw.lower()
        if not raw:return None
        if re.search(r"\b(i(?:'m| am) sorry|i apologise|i apologize)\b",low): return ("apology",f"The player explicitly apologised: {raw[:170]}")
        if re.search(r"\b(i promise|i swear|i will definitely|i'll make sure)\b",low): return ("promise",f"The player made an explicit commitment: {raw[:170]}")
        if re.search(r"\b(would you like to|do you want to|will you join me|come with me)\b",low): return ("invitation",f"The player offered an invitation: {raw[:170]}")
        if re.search(r"\b(can you|could you|would you)\b",low) and "?" in raw: return ("request",f"The player made a direct request: {raw[:170]}")
        insults=("idiot","stupid","useless","liar","pathetic","shut up","hate you")
        if any(x in low for x in insults): return ("insult",f"The player spoke insultingly: {raw[:170]}")
        if re.search(r"\b(i agree|you're right|you are right|deal)\b",low): return ("agreement",f"The player explicitly agreed: {raw[:170]}")
        if re.search(r"\b(i refuse|i won't|i will not|no, i can't|no, i cannot)\b",low): return ("refusal",f"The player explicitly refused: {raw[:170]}")
        return None

SOCIAL_CONSEQUENCE_MODEL=SocialConsequenceModel()
