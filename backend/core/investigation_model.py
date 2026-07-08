"""Investigation graph: evidence, testimony, contradictions, hypotheses and cross-mystery connections."""
from copy import deepcopy
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'content'/'investigation'/'mystery_catalogue.json'
class InvestigationModel:
    def __init__(self,path=PATH):
        self.data=json.loads(Path(path).read_text(encoding='utf-8'))
        self.schema_version=int(self.data.get('schema_version',1)); self.mysteries=self.data['mysteries']
        self.evidence_links=self.data.get('evidence_links',{}); self.fact_links=self.data.get('fact_links',{}); self.hypotheses=self.data.get('hypotheses',{})
        self.validate()
    def validate(self):
        for mid,m in self.mysteries.items():
            for other in m.get('related_mysteries',[]):
                if other not in self.mysteries: raise ValueError(f'invalid related mystery {mid}:{other}')
        for eid,mids in self.evidence_links.items():
            if not mids or any(mid not in self.mysteries for mid in mids): raise ValueError(f'invalid evidence links {eid}')
        for fid,mids in self.fact_links.items():
            if any(mid not in self.mysteries for mid in mids): raise ValueError(f'invalid fact links {fid}')
        for hid,h in self.hypotheses.items():
            if h.get('mystery') not in self.mysteries: raise ValueError(f'invalid mystery for {hid}')
            if int(h.get('confirm_threshold',1))<1: raise ValueError(f'invalid threshold {hid}')
            if int(h.get('confirm_threshold',1))>len(h.get('requires_any',[])): raise ValueError(f'unreachable threshold {hid}')
        return True
    def runtime_defaults(self):
        return {'schema_version':self.schema_version,'observations':{},'testimony':[],'hypotheses':{},'contradictions':[],'connections':[],
          'mystery_progress':{mid:{'evidence':[],'testimony':[],'hypotheses':[],'status':'unopened'} for mid in self.mysteries}}
    def links_for_evidence(self,eid): return list(self.evidence_links.get(eid,[]))
    def links_for_fact(self,fid): return list(self.fact_links.get(fid,[]))
    def tokens(self,runtime): return set(runtime.get('observations',{}))|{f"fact:{x.get('fact_id')}" for x in runtime.get('testimony',[])}
    def eligible_hypotheses(self,runtime):
        tokens=self.tokens(runtime); out=[]
        for hid,h in self.hypotheses.items():
            support=[x for x in h.get('requires_any',[]) if x in tokens]
            if support: out.append((hid,support))
        return out
    def assess(self,hid,runtime):
        if hid not in self.hypotheses: return None
        h=self.hypotheses[hid]; tokens=self.tokens(runtime); support=[x for x in h.get('requires_any',[]) if x in tokens]; threshold=int(h.get('confirm_threshold',1))
        return {'hypothesis_id':hid,'title':h['title'],'mystery':h['mystery'],'support':support,'support_count':len(support),'threshold':threshold,'status':'supported' if len(support)>=threshold else 'tentative'}
    def refresh(self,runtime):
        runtime['schema_version']=self.schema_version; runtime.setdefault('connections',[])
        for mid in self.mysteries:
            p=runtime.setdefault('mystery_progress',{}).setdefault(mid,{'evidence':[],'testimony':[],'hypotheses':[],'status':'unopened'})
            p.setdefault('evidence',[]); p.setdefault('testimony',[]); p.setdefault('hypotheses',[])
            count=len(p['evidence'])+len(p['testimony'])+len(p['hypotheses'])
            p['status']='deepening' if count>=5 else 'active' if count>=1 else 'unopened'
        found=[]
        active={m for m,p in runtime['mystery_progress'].items() if p.get('status')!='unopened'}
        for mid in sorted(active):
            for other in self.mysteries[mid].get('related_mysteries',[]):
                if other in active:
                    key='|'.join(sorted((mid,other)))
                    if key not in found: found.append(key)
        runtime['connections']=found
        return runtime
    def public_overview(self,runtime):
        self.refresh(runtime)
        return {'mysteries':{mid:{'title':self.mysteries[mid]['title'],'summary':self.mysteries[mid]['summary'],'status':runtime['mystery_progress'][mid]['status'],'evidence_count':len(runtime['mystery_progress'][mid]['evidence']),'testimony_count':len(runtime['mystery_progress'][mid]['testimony'])} for mid in self.mysteries},'eligible_hypotheses':[{'id':h,'support':s} for h,s in self.eligible_hypotheses(runtime)],'hypotheses':deepcopy(runtime.get('hypotheses',{})),'contradictions':deepcopy(runtime.get('contradictions',[])),'connections':deepcopy(runtime.get('connections',[]))}
INVESTIGATION_MODEL=InvestigationModel()
