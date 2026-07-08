"""Part 11 investigation graph: evidence, testimony, contradictions and hypotheses."""
from copy import deepcopy
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'content'/'investigation'/'mystery_catalogue.json'
class InvestigationModel:
    def __init__(self,path=PATH):
        self.data=json.loads(Path(path).read_text(encoding='utf-8')); self.schema_version=int(self.data.get('schema_version',1)); self.mysteries=self.data['mysteries']; self.evidence_links=self.data.get('evidence_links',{}); self.fact_links=self.data.get('fact_links',{}); self.hypotheses=self.data.get('hypotheses',{}); self.validate()
    def validate(self):
        for hid,h in self.hypotheses.items():
            if h.get('mystery') not in self.mysteries: raise ValueError(f'invalid mystery for {hid}')
            if int(h.get('confirm_threshold',1))<1: raise ValueError(f'invalid threshold {hid}')
        return True
    def runtime_defaults(self):
        return {'schema_version':self.schema_version,'observations':{},'testimony':[], 'hypotheses':{},'contradictions':[], 'mystery_progress':{mid:{'evidence':[],'testimony':[],'hypotheses':[]} for mid in self.mysteries}}
    def links_for_evidence(self,eid): return list(self.evidence_links.get(eid,[]))
    def links_for_fact(self,fid): return list(self.fact_links.get(fid,[]))
    def eligible_hypotheses(self,runtime):
        tokens=set(runtime.get('observations',{}))|{f"fact:{x.get('fact_id')}" for x in runtime.get('testimony',[])}
        out=[]
        for hid,h in self.hypotheses.items():
            support=[x for x in h.get('requires_any',[]) if x in tokens]
            if support: out.append((hid,support))
        return out
    def assess(self,hid,runtime):
        if hid not in self.hypotheses: return None
        h=self.hypotheses[hid]; tokens=set(runtime.get('observations',{}))|{f"fact:{x.get('fact_id')}" for x in runtime.get('testimony',[])}
        support=[x for x in h.get('requires_any',[]) if x in tokens]; threshold=int(h.get('confirm_threshold',1))
        return {'hypothesis_id':hid,'title':h['title'],'mystery':h['mystery'],'support':support,'support_count':len(support),'threshold':threshold,'status':'supported' if len(support)>=threshold else 'tentative'}
INVESTIGATION_MODEL=InvestigationModel()
