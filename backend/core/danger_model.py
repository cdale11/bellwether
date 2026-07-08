"""Part 14 danger, injury, death and terminal run-state architecture."""
from copy import deepcopy
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'content'/'danger'/'hazard_catalogue.json'
class DangerModel:
    def __init__(self,path=PATH):
        self.data=json.loads(Path(path).read_text()); self.schema_version=int(self.data.get('schema_version',1)); self.hazards=self.data['hazards']; self.injuries=self.data['injuries']; self.validate()
    def validate(self):
        for hid,h in self.hazards.items():
            if h.get('injury') not in self.injuries: raise ValueError(f'unknown injury {hid}')
            if not h.get('location') or int(h.get('severity',0))<1: raise ValueError(f'invalid hazard {hid}')
        return True
    def runtime_defaults(self):
        return {'schema_version':self.schema_version,'status':'alive','risk':0,'injuries':{},'warnings_seen':[],'hazard_history':[],'death':None,'terminal_reason':None,'last_hazard_pulse':-999}
    def eligible(self,state):
        rt=state.setdefault('danger',self.runtime_defaults())
        if rt.get('status')!='alive': return []
        loc=state.get('location'); pressure=int(state.get('village_brain',{}).get('supernatural_pressure',0)); anomalies=len(state.get('systemic_horror',{}).get('experienced',[])); pulse=int(state.get('village_brain',{}).get('pulse_count',0)); out=[]
        for hid,h in self.hazards.items():
            if h['location']!=loc or pressure<int(h.get('min_pressure',0)) or anomalies<int(h.get('min_anomalies',0)): continue
            if any(x.get('hazard_id')==hid for x in rt.get('hazard_history',[])): continue
            if pulse-int(rt.get('last_hazard_pulse',-999))<6: continue
            out.append(hid)
        return out
    def warn(self,state,hid):
        if hid not in self.hazards:return False
        rt=state.setdefault('danger',self.runtime_defaults())
        if hid not in rt['warnings_seen']: rt['warnings_seen'].append(hid)
        return self.hazards[hid]['warning']
    def apply(self,state,hid):
        if hid not in self.hazards:return None
        rt=state.setdefault('danger',self.runtime_defaults())
        if rt.get('status')!='alive':return None
        h=self.hazards[hid]; pulse=int(state.get('village_brain',{}).get('pulse_count',0)); injury=h['injury']; idef=self.injuries[injury]
        prior=sum(int(v.get('severity',0)) for v in rt.get('injuries',{}).values()); risk=int(rt.get('risk',0)); warned=hid in rt.get('warnings_seen',[])
        fatal = bool(h['severity']>=4 and (prior+risk)>=5 and not warned)
        entry={'hazard_id':hid,'day':state.get('day'),'minute':state.get('minute'),'location':state.get('location'),'injury':injury,'fatal':fatal,'pulse':pulse}
        rt['hazard_history'].append(entry); rt['last_hazard_pulse']=pulse
        if fatal:
            rt['status']='dead'; rt['death']=deepcopy(entry); rt['terminal_reason']='death'; state.setdefault('branch_state',{})['run_complete']=True
        else:
            rt['injuries'][injury]={'label':idef['label'],'severity':idef['severity'],'acquired_day':state.get('day'),'recovery_days':idef['recovery_days'],'treated':False}
            rt['risk']=min(10,risk+int(h['severity']))
        return {'id':hid,**deepcopy(h),'fatal':fatal}
    def recover_day(self,state):
        rt=state.setdefault('danger',self.runtime_defaults()); day=int(state.get('day',1)); healed=[]
        for iid,inj in list(rt.get('injuries',{}).items()):
            needed=int(inj.get('recovery_days',2))-(1 if inj.get('treated') else 0)
            if day-int(inj.get('acquired_day',day))>=max(1,needed): healed.append(iid); rt['injuries'].pop(iid,None); rt['risk']=max(0,int(rt.get('risk',0))-int(inj.get('severity',1)))
        return healed
    def treat(self,state):
        rt=state.setdefault('danger',self.runtime_defaults())
        untreated=[(k,v) for k,v in rt.get('injuries',{}).items() if not v.get('treated')]
        if not untreated:return None
        iid,inj=sorted(untreated,key=lambda x:int(x[1].get('severity',0)),reverse=True)[0]; inj['treated']=True; rt['risk']=max(0,int(rt.get('risk',0))-1); return iid
DANGER_MODEL=DangerModel()
