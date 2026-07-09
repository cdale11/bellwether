"""v1.3.0 Society and Generational Time.
Deterministic slow social change for lightweight residents: ties, households,
employment pressure, migration signals, aging bands and village continuity.
"""
from copy import deepcopy

class SocietyModel:
    SCHEMA_VERSION=1
    def runtime_defaults(self):
        return {'schema_version':1,'last_day':0,'last_week':0,'years_elapsed':0.0,
                'migration':{'arrivals':0,'departures':0,'pressure':0.0,'history':[]},
                'employment':{'employed':0,'seeking':0,'retired':0,'students':0,'history':[]},
                'social':{'encounters':0,'new_ties':0,'strong_ties':0,'isolated':0,'history':[]},
                'households':{},'demography':{'age_transitions':0,'rare_events':[]},'weekly_snapshots':[]}
    def migrate(self,state):
        rt=state.setdefault('society',self.runtime_defaults()); d=self.runtime_defaults()
        for k,v in d.items(): rt.setdefault(k,deepcopy(v))
        for k in ('migration','employment','social','demography'):
            for kk,v in d[k].items(): rt[k].setdefault(kk,deepcopy(v))
        return rt
    def advance_day(self,state,population):
        rt=self.migrate(state); day=int(state.get('day',1))
        if rt['last_day']==day:return
        rt['last_day']=day; rt['years_elapsed']=round(max(0,day-1)/365.0,3)
        residents=population.migrate(state)['residents']; econ=state.get('economy',{}).get('market',{}).get('businesses',{})
        stressed=sum(1 for b in econ.values() if float(b.get('pressure',0))>=50)
        rt['migration']['pressure']=round(min(1.0, stressed*.15 + max(0,len(residents)-22)*.03),2)
        employed=seeking=retired=students=0
        households={}
        for r in residents.values():
            households.setdefault(r.get('household','unknown'),[]).append(r['id'])
            occ=str(r.get('occupation','')).lower(); age=r.get('age_band','')
            if 'retir' in occ or age=='elder': retired+=1
            elif r.get('routine')=='student': students+=1
            elif r.get('routine') in {'commuter','shift_worker','shop_worker','early_worker','mobile_worker','home_worker'}: employed+=1
            else: seeking+=1
        rt['households']={k:{'members':v,'size':len(v)} for k,v in households.items()}
        rt['employment'].update(employed=employed,seeking=seeking,retired=retired,students=students)
        links=[len(r.get('social_links',[])) for r in residents.values()]; rt['social']['strong_ties']=sum(1 for n in links if n>=4);rt['social']['isolated']=sum(1 for n in links if n==0)
        if day%7==0 and rt['last_week']!=day//7:
            rt['last_week']=day//7; snap={'day':day,'population':len(residents),'employed':employed,'seeking':seeking,'strong_ties':rt['social']['strong_ties'],'isolated':rt['social']['isolated'],'migration_pressure':rt['migration']['pressure']};rt['weekly_snapshots'].append(snap);rt['weekly_snapshots']=rt['weekly_snapshots'][-52:]
    def note_encounter(self,state,resident_id):
        rt=self.migrate(state);rt['social']['encounters']+=1;rt['social']['history'].append({'day':state.get('day'),'resident':resident_id});rt['social']['history']=rt['social']['history'][-100:]
    def public(self,state): return deepcopy(self.migrate(state))
SOCIETY_MODEL=SocietyModel()
