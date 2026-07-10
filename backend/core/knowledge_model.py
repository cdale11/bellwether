"""Part 10 bounded NPC knowledge, gossip and information propagation."""
from copy import deepcopy
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'content'/'social'/'knowledge_catalogue.json'
class KnowledgeModel:
    def __init__(self,path=PATH):
        self.data=json.loads(Path(path).read_text(encoding='utf-8')); self.schema_version=int(self.data.get('schema_version',1)); self.facts=self.data['facts']; self.initial=self.data.get('initial_knowledge',{}); self.validate()
    def validate(self):
        for fid,f in self.facts.items():
            if not f.get('truth') or not isinstance(f.get('domains'),list): raise ValueError(f'invalid fact {fid}')
            if not 0<=float(f.get('sensitivity',0))<=1: raise ValueError(f'invalid sensitivity {fid}')
        return True
    def runtime_defaults(self,npc_ids):
        out={}
        for nid in npc_ids:
            beliefs={}
            for fid,conf in self.initial.get(nid,{}).items(): beliefs[fid]={"confidence":float(conf),"variant":"truth","source":"authored","heard_count":1,"last_heard_minute":None}
            out[nid]={"schema_version":self.schema_version,"beliefs":beliefs,"withheld":[],"transmission_log":[]}
        return {"schema_version":self.schema_version,"npcs":out,"propagation_log":[]}
    def context(self,npc_id,runtime):
        beliefs=runtime.get('npcs',{}).get(npc_id,{}).get('beliefs',{})
        return [{"fact_id":fid,"text":self.text(fid,b.get('variant','truth')),"confidence":b.get('confidence',0)} for fid,b in sorted(beliefs.items(),key=lambda x:-x[1].get('confidence',0))[:8] if fid in self.facts]
    def text(self,fid,variant):
        f=self.facts[fid]
        if variant=='truth': return f['truth']
        ds=f.get('distortions',[])
        try: return ds[int(str(variant).split(':')[-1])]
        except Exception: return f['truth']
    def choose_transfer(self,source,target,edge_state,runtime,absolute_minute):
        src=runtime['npcs'].get(source,{}).get('beliefs',{}); dst=runtime['npcs'].get(target,{}).get('beliefs',{})
        trust=float(edge_state.get('trust',0)); tension=float(edge_state.get('tension',0))
        for fid,b in sorted(src.items(),key=lambda x:-x[1].get('confidence',0)):
            if fid not in self.facts or fid in dst: continue
            sensitivity=float(self.facts[fid].get('sensitivity',0))
            if trust < sensitivity*80-10 or tension>65: continue
            variant=b.get('variant','truth')
            # Deterministic bounded distortion: low trust and repeated hearsay can select catalogue variant only.
            if variant=='truth' and self.facts[fid].get('distortions') and trust<25 and sensitivity>=0.3:
                variant='distortion:0'
            conf=max(.2,min(.95,float(b.get('confidence',.5))*(.72+max(-.1,min(.15,trust/400)))))
            return fid,{"confidence":round(conf,3),"variant":variant,"source":source,"heard_count":1,"last_heard_minute":absolute_minute}
        return None,None
KNOWLEDGE_MODEL=KnowledgeModel()
