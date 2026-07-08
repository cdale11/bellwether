"""v0.5.1 persistent lightweight resident population and batched simulation.

Lightweight residents are stable run entities with strict schema. They are kept
separate from the deeply simulated authored core cast so population scale does
not multiply LLM calls or core social-web costs.
"""
from copy import deepcopy
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
DATA_PATH=ROOT/'content'/'npcs'/'lightweight_resident_seeds.json'

class PopulationModel:
    SCHEMA_VERSION=1
    ROUTINES={'mobile_worker','home_errands','early_worker','shift_worker','student','home_worker','community','commuter','shop_worker'}
    REQUIRED={'id','name','age_band','household','occupation','home_area','routine','traits','interests'}
    def __init__(self,path=DATA_PATH):
        self.data=json.loads(Path(path).read_text(encoding='utf-8'))
        self.residents=self.data['residents']; self.validate()
    def validate(self):
        ids=set(); errors=[]
        for r in self.residents:
            miss=self.REQUIRED-set(r)
            if miss: errors.append(f"{r.get('id','?')}: missing {sorted(miss)}")
            if r.get('id') in ids: errors.append(f"duplicate {r.get('id')}")
            ids.add(r.get('id'))
            if r.get('routine') not in self.ROUTINES: errors.append(f"{r.get('id')}: invalid routine")
            if not (1 <= len(r.get('traits',[])) <= 4): errors.append(f"{r.get('id')}: traits")
            if not (1 <= len(r.get('interests',[])) <= 4): errors.append(f"{r.get('id')}: interests")
        if not 20 <= len(self.residents) <= 25: errors.append('population must contain 20-25 residents')
        if errors: raise ValueError('Invalid lightweight population: '+'; '.join(errors))
        return True
    def runtime_defaults(self):
        return {'schema_version':self.SCHEMA_VERSION,'last_batch_day':1,'last_batch_hour':-1,'batch_count':0,
                'residents':{r['id']:{**deepcopy(r),'tier':'lightweight','location':r['home_area'],'activity':'at home','visible':True,
                    'social_links':[],'history':[],'reputation':0,'current_concern':None,'last_update':None} for r in self.residents}}
    def migrate(self,state):
        pop=state.setdefault('population',self.runtime_defaults())
        defaults=self.runtime_defaults()
        for k,v in defaults.items(): pop.setdefault(k,deepcopy(v))
        for rid,row in defaults['residents'].items():
            slot=pop['residents'].setdefault(rid,deepcopy(row))
            for k,v in row.items(): slot.setdefault(k,deepcopy(v))
        return pop
    def _schedule(self,r,hour,day):
        routine=r['routine']; weekend=(day%7) in (0,6)
        if hour < 6: return r['home_area'],'sleeping'
        if routine=='early_worker' and 6<=hour<15: return ('village_green' if hour%2 else 'village_road'),'working outdoors'
        if routine=='shop_worker' and 8<=hour<17: return 'village_shop','working a shop shift'
        if routine=='mobile_worker' and 7<=hour<17: return ('village_road' if hour%3 else 'village_green'),'making rounds through the village'
        if routine=='commuter' and not weekend and 7<=hour<18: return 'away','working outside Bellwether'
        if routine=='student' and not weekend and 8<=hour<16: return 'away','at school outside the village'
        if routine=='shift_worker' and 7<=hour<16: return 'away','working a shift outside the village'
        if routine=='home_worker' and 9<=hour<16: return r['home_area'],'working from home'
        if routine=='community' and 9<=hour<15: return ('churchyard' if (day+hour)%2 else 'village_green'),'helping with a community task'
        if routine=='home_errands' and 10<=hour<15: return ('village_shop' if hour%2 else 'village_green'),'out on ordinary errands'
        if 16<=hour<19: return ['village_shop','village_green','riverside_path'][(day+hour+len(r['id']))%3],'out for an evening errand'
        if 19<=hour<21 and (day+len(r['id']))%4==0: return 'village_green','spending time around the green'
        return r['home_area'],'at home'
    def advance_batch(self,state):
        pop=self.migrate(state); hour=int(state.get('minute',0))//60; day=int(state.get('day',1))
        if pop['last_batch_day']==day and pop['last_batch_hour']==hour: return []
        pop['last_batch_day']=day; pop['last_batch_hour']=hour; pop['batch_count']+=1; changes=[]
        for rid,r in pop['residents'].items():
            loc,activity=self._schedule(r,hour,day)
            if (r.get('location'),r.get('activity')) != (loc,activity):
                changes.append((rid,r.get('location'),loc))
            r['location']=loc; r['activity']=activity; r['last_update']={'day':day,'minute':state.get('minute',0)}
        # Cheap persistent social traces: co-located residents acquire stable links.
        byloc={}
        for rid,r in pop['residents'].items():
            if r['location']!='away': byloc.setdefault(r['location'],[]).append(rid)
        for loc,ids in byloc.items():
            ids=sorted(ids)
            for i in range(0,len(ids)-1,2):
                a,b=ids[i],ids[i+1]
                for x,y in ((a,b),(b,a)):
                    links=pop['residents'][x]['social_links']
                    if y not in links: links.append(y); del links[:-12]
        return changes
    def present(self,state,location):
        pop=self.migrate(state)
        return [deepcopy(r) for r in pop['residents'].values() if r.get('visible',True) and r.get('location')==location]
    def summary(self,state):
        pop=self.migrate(state); residents=pop['residents']; active=sum(1 for r in residents.values() if r.get('location')!='away')
        return {'count':len(residents),'currently_in_village':active,'batch_count':pop['batch_count']}

POPULATION_MODEL=PopulationModel()
