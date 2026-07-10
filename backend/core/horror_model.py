"""Bounded systemic and adaptive horror.

Authored anomalies remain the only supernatural events.  Adaptation changes selection,
pacing and pressure emphasis from authoritative player behaviour; it never invents an
anomaly, changes canon, or bypasses eligibility.
"""
from copy import deepcopy
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'content'/'horror'/'anomaly_catalogue.json'

DOMAIN_BY_STYLE={
    'pattern_seeking':['information','memory','geography','routine'],
    'withdrawal':['architecture','geography','routine','transport'],
    'connection':['memory','information','routine','transport'],
    'practical_routine':['routine','ecology','architecture','information'],
    'self_reliance':['geography','transport','architecture','ecology'],
    'unformed':['routine','geography','ecology','information'],
}

class HorrorModel:
    def __init__(self,path=PATH):
        self.data=json.loads(Path(path).read_text(encoding='utf-8')); self.schema_version=max(2,int(self.data.get('schema_version',1))); self.anomalies=self.data['anomalies']; self.validate()
    def validate(self):
        valid_domains={'geography','routine','architecture','transport','memory','ecology','information'}
        for aid,a in self.anomalies.items():
            if a.get('domain') not in valid_domains: raise ValueError(f'invalid horror domain {aid}')
            if not a.get('location') or not a.get('text') or not a.get('summary'): raise ValueError(f'incomplete anomaly {aid}')
        return True
    def runtime_defaults(self):
        return {'schema_version':self.schema_version,'experienced':[],'active_overlays':{},'domain_counts':{},'last_trigger_pulse':-999,'corruption_log':[],
                'adaptive':{'profile':'unformed','preferred_domains':[],'pressure_band':'quiet','quiet_until_pulse':0,'last_profile_pulse':-999,'selection_log':[],'suppressed_count':0}}
    def migrate(self,state):
        rt=state.setdefault('systemic_horror',self.runtime_defaults())
        for k,v in self.runtime_defaults().items(): rt.setdefault(k,deepcopy(v))
        ad=rt.setdefault('adaptive',deepcopy(self.runtime_defaults()['adaptive']))
        for k,v in self.runtime_defaults()['adaptive'].items(): ad.setdefault(k,deepcopy(v))
        rt['schema_version']=self.schema_version
        return rt
    def refresh_adaptive_profile(self,state):
        rt=self.migrate(state); ad=rt['adaptive']; pulse=int(state.get('village_brain',{}).get('pulse_count',0))
        ident=state.get('player_identity',{}); style=ident.get('coping_style','unformed'); traits=ident.get('traits',{})
        preferred=list(DOMAIN_BY_STYLE.get(style,DOMAIN_BY_STYLE['unformed']))
        # Behavioural refinements are deterministic and inspectable.
        if int(traits.get('social',0))>=45:
            preferred=['memory','information','routine']+[x for x in preferred if x not in {'memory','information','routine'}]
        elif int(traits.get('inquiry',0))>=45:
            preferred=['information','geography','memory']+[x for x in preferred if x not in {'information','geography','memory'}]
        elif int(traits.get('routine',0))>=45:
            preferred=['routine','architecture','ecology']+[x for x in preferred if x not in {'routine','architecture','ecology'}]
        ad['profile']=style; ad['preferred_domains']=preferred[:5]; ad['last_profile_pulse']=pulse
        psych=state.get('psychological_state',{}); unease=int(psych.get('unease',0))
        if pulse < int(ad.get('quiet_until_pulse',0)): ad['pressure_band']='quiet'
        elif unease>=70: ad['pressure_band']='recovery'
        elif len(rt.get('experienced',[]))>=3: ad['pressure_band']='established'
        else: ad['pressure_band']='subtle'
        return ad
    def eligible(self,state):
        loc=state.get('location'); life=state.get('player_life',{}); fam=life.get('location_familiarity',{}).get(loc,0); obs=state.get('investigation',{}).get('observation_counts',{}).get(loc,0); disruptions=state.get('psychological_state',{}).get('familiarity_disruptions',0); read=state.get('flags',{}).get('read_letter',False); seen=set(self.migrate(state).get('experienced',[])); out=[]
        for aid,a in self.anomalies.items():
            r=a.get('requires',{})
            if a.get('location')!=loc or aid in seen: continue
            if fam < int(r.get('familiarity',0)) or obs < int(r.get('observation_count',0)) or disruptions < int(r.get('min_disruptions',0)): continue
            if r.get('read_letter') and not read: continue
            out.append(aid)
        return out
    def choose(self,state,candidates):
        """Choose only among already-eligible authored anomalies, adapting emphasis."""
        if not candidates:return None
        rt=self.migrate(state); ad=self.refresh_adaptive_profile(state); pulse=int(state.get('village_brain',{}).get('pulse_count',0))
        if pulse < int(ad.get('quiet_until_pulse',0)):
            ad['suppressed_count']=int(ad.get('suppressed_count',0))+1; return None
        pref=ad.get('preferred_domains',[]); counts=rt.get('domain_counts',{})
        def score(aid):
            dom=self.anomalies[aid]['domain']
            rank=(len(pref)-pref.index(dom))*10 if dom in pref else 0
            diversity=-int(counts.get(dom,0))*4
            return (rank+diversity, aid)
        chosen=max(candidates,key=score)
        ad['selection_log'].append({'pulse':pulse,'profile':ad.get('profile'),'eligible':list(candidates),'chosen':chosen,'domain':self.anomalies[chosen]['domain']})
        ad['selection_log']=ad['selection_log'][-30:]
        return chosen
    def set_quiet_period(self,state,pulses=6,reason='recovery'):
        rt=self.migrate(state); ad=rt['adaptive']; pulse=int(state.get('village_brain',{}).get('pulse_count',0))
        ad['quiet_until_pulse']=max(int(ad.get('quiet_until_pulse',0)),pulse+max(1,int(pulses))); ad['pressure_band']='quiet'; ad['quiet_reason']=reason
    def apply(self,state,aid):
        if aid not in self.anomalies:return None
        rt=self.migrate(state); a=self.anomalies[aid]; pulse=state.get('village_brain',{}).get('pulse_count',0)
        if aid in rt['experienced']:return None
        overlay={'anomaly_id':aid,'domain':a['domain'],'kind':a.get('overlay',{}).get('kind'),'strength':a.get('overlay',{}).get('strength',1),'day':state.get('day'),'pulse':pulse,'expires_pulse':pulse+3}
        rt['experienced'].append(aid); rt['active_overlays'][a['location']]=overlay; rt['domain_counts'][a['domain']]=rt['domain_counts'].get(a['domain'],0)+1; rt['last_trigger_pulse']=pulse; rt['corruption_log'].append(deepcopy(overlay)); rt['corruption_log']=rt['corruption_log'][-30:]
        state.setdefault('world_model',{}).setdefault('supernatural_overlays',{})[a['location']]=deepcopy(overlay)
        # Mandatory breathing room: higher unease earns a longer recovery window.
        unease=int(state.get('psychological_state',{}).get('unease',0)); self.set_quiet_period(state,10 if unease>=55 else 6,'post_anomaly_recovery')
        return {'id':aid,**deepcopy(a)}
    def expire(self,state):
        rt=self.migrate(state); pulse=state.get('village_brain',{}).get('pulse_count',0); expired=[]
        for loc,o in list(rt.get('active_overlays',{}).items()):
            if pulse>=int(o.get('expires_pulse',pulse+1)):
                expired.append(loc); rt['active_overlays'].pop(loc,None); state.setdefault('world_model',{}).setdefault('supernatural_overlays',{}).pop(loc,None)
        return expired
    def location_context(self,state,location_id):
        return deepcopy(self.migrate(state).get('active_overlays',{}).get(location_id))
    def developer_context(self,state):
        rt=self.migrate(state); ad=self.refresh_adaptive_profile(state)
        return {'profile':ad.get('profile'),'preferred_domains':deepcopy(ad.get('preferred_domains',[])),'pressure_band':ad.get('pressure_band'),'quiet_until_pulse':ad.get('quiet_until_pulse'),'suppressed_count':ad.get('suppressed_count',0),'recent_selections':deepcopy(ad.get('selection_log',[])[-5:])}
HORROR_MODEL=HorrorModel()
