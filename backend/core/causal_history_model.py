"""Persistent causal provenance and bounded social facts for emergent simulation.

Objective events remain authoritative elsewhere. This model stores why a derived
simulation consequence happened and social facts (beliefs, obligations, tensions)
that may themselves become future causes.
"""
from copy import deepcopy

class CausalHistoryModel:
    def defaults(self):
        return {"schema_version":1,"links":[],"social_facts":[],"next_fact_id":1}
    def migrate(self,s):
        rt=s.setdefault("causal_history",deepcopy(self.defaults()))
        for k,v in self.defaults().items(): rt.setdefault(k,deepcopy(v))
        return rt
    def link(self,s,effect_type,effect_id,causes,summary,source=None):
        rt=self.migrate(s)
        row={"day":s.get("day",1),"minute":s.get("minute",0),"effect_type":effect_type,
             "effect_id":str(effect_id),"causes":[str(x) for x in causes if x][:8],
             "summary":str(summary)[:400],"source":source}
        rt["links"].append(row); rt["links"]=rt["links"][-240:]
        return row
    def add_social_fact(self,s,kind,subject,target,content,causes,source):
        rt=self.migrate(s); fid=f"sf_{rt['next_fact_id']}";rt['next_fact_id']+=1
        row={"id":fid,"day":s.get("day",1),"kind":kind,"subject":subject,"target":target,
             "content":str(content)[:300],"causes":[str(x) for x in causes if x][:8],
             "source":source,"status":"active"}
        rt["social_facts"].append(row);rt["social_facts"]=rt["social_facts"][-160:]
        self.link(s,"social_fact",fid,row["causes"],row["content"],source)
        return row
    def public(self,s):
        rt=self.migrate(s)
        return {"recent_links":deepcopy(rt["links"][-30:]),"active_social_facts":deepcopy([x for x in rt["social_facts"] if x.get("status")=="active"][-30:])}
CAUSAL_HISTORY_MODEL=CausalHistoryModel()
