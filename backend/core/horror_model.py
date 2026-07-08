"""Part 12 systemic horror: bounded corruption of learned normality.

Anomalies are authored catalogue entries. Runtime selection can only choose eligible
entries and applies inspectable, temporary supernatural overlays to existing systems.
"""
from copy import deepcopy
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'content'/'horror'/'anomaly_catalogue.json'
class HorrorModel:
    def __init__(self,path=PATH):
        self.data=json.loads(Path(path).read_text(encoding='utf-8')); self.schema_version=int(self.data.get('schema_version',1)); self.anomalies=self.data['anomalies']; self.validate()
    def validate(self):
        valid_domains={'geography','routine','architecture','transport','memory','ecology','information'}
        for aid,a in self.anomalies.items():
            if a.get('domain') not in valid_domains: raise ValueError(f'invalid horror domain {aid}')
            if not a.get('location') or not a.get('text') or not a.get('summary'): raise ValueError(f'incomplete anomaly {aid}')
        return True
    def runtime_defaults(self):
        return {'schema_version':self.schema_version,'experienced':[],'active_overlays':{},'domain_counts':{},'last_trigger_pulse':-999,'corruption_log':[]}
    def eligible(self,state):
        loc=state.get('location'); life=state.get('player_life',{}); fam=life.get('location_familiarity',{}).get(loc,0); obs=state.get('investigation',{}).get('observation_counts',{}).get(loc,0); disruptions=state.get('psychological_state',{}).get('familiarity_disruptions',0); read=state.get('flags',{}).get('read_letter',False); seen=set(state.get('systemic_horror',{}).get('experienced',[])); out=[]
        for aid,a in self.anomalies.items():
            r=a.get('requires',{})
            if a.get('location')!=loc or aid in seen: continue
            if fam < int(r.get('familiarity',0)) or obs < int(r.get('observation_count',0)) or disruptions < int(r.get('min_disruptions',0)): continue
            if r.get('read_letter') and not read: continue
            out.append(aid)
        return out
    def apply(self,state,aid):
        if aid not in self.anomalies: return None
        rt=state.setdefault('systemic_horror',self.runtime_defaults()); a=self.anomalies[aid]; pulse=state.get('village_brain',{}).get('pulse_count',0)
        if aid in rt['experienced']: return None
        overlay={'anomaly_id':aid,'domain':a['domain'],'kind':a.get('overlay',{}).get('kind'),'strength':a.get('overlay',{}).get('strength',1),'day':state.get('day'),'pulse':pulse,'expires_pulse':pulse+3}
        rt['experienced'].append(aid); rt['active_overlays'][a['location']]=overlay; rt['domain_counts'][a['domain']]=rt['domain_counts'].get(a['domain'],0)+1; rt['last_trigger_pulse']=pulse; rt['corruption_log'].append(deepcopy(overlay)); rt['corruption_log']=rt['corruption_log'][-30:]
        state.setdefault('world_model',{}).setdefault('supernatural_overlays',{})[a['location']]=deepcopy(overlay)
        return {'id':aid,**deepcopy(a)}
    def expire(self,state):
        rt=state.setdefault('systemic_horror',self.runtime_defaults()); pulse=state.get('village_brain',{}).get('pulse_count',0); expired=[]
        for loc,o in list(rt.get('active_overlays',{}).items()):
            if pulse>=int(o.get('expires_pulse',pulse+1)):
                expired.append(loc); rt['active_overlays'].pop(loc,None); state.setdefault('world_model',{}).setdefault('supernatural_overlays',{}).pop(loc,None)
        return expired
    def location_context(self,state,location_id):
        rt=state.setdefault('systemic_horror',self.runtime_defaults())
        return deepcopy(rt.get('active_overlays',{}).get(location_id))
HORROR_MODEL=HorrorModel()
