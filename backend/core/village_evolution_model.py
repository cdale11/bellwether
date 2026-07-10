"""v2.8.0 long-term village evolution.

Sparse deterministic structural change layered over population, society, economy,
property and NPC-life state. It records migration, household moves, enterprise
openings/closures and land-use changes without rewriting authored story canon.
"""
from copy import deepcopy

class VillageEvolutionModel:
    SCHEMA_VERSION=1
    def runtime_defaults(self):
        return {'schema_version':1,'last_day':0,'last_week':0,'events':[],
                'resident_status':{},'ventures':{},'land_use':{},
                'summary':{'arrivals':0,'departures':0,'moves':0,'openings':0,'closures':0,'land_changes':0}}
    def migrate(self,state):
        rt=state.setdefault('village_evolution',self.runtime_defaults()); d=self.runtime_defaults()
        for k,v in d.items(): rt.setdefault(k,deepcopy(v))
        for rid,r in state.get('population',{}).get('residents',{}).items():
            rt['resident_status'].setdefault(rid,{'present':True,'household':r.get('household','unknown'),'since_day':1,'last_change':None})
        return rt
    def _event(self,rt,state,kind,text,details=None):
        row={'day':int(state.get('day',1)),'kind':kind,'text':text,'details':details or {}}
        rt['events'].append(row); rt['events']=rt['events'][-240:]; return row
    def advance_day(self,state):
        rt=self.migrate(state); day=int(state.get('day',1))
        if rt['last_day']>=day:return []
        rt['last_day']=day
        if day<7 or day//7==rt['last_week']:return []
        rt['last_week']=day//7; events=[]
        pop=state.get('population',{}).get('residents',{}); society=state.get('society',{}); pressure=float(society.get('migration',{}).get('pressure',0) or 0)
        market=state.get('economy',{}).get('market',{}); businesses=market.get('businesses',{}); outlook=market.get('village_outlook','stable')
        # Migration is sparse and reversible: residents remain persistent entities but may be away from the village.
        present=[rid for rid,s in rt['resident_status'].items() if s.get('present',True)]
        away=[rid for rid,s in rt['resident_status'].items() if not s.get('present',True)]
        if pressure>=.45 and len(present)>20 and day%28==0:
            rid=sorted(present)[(day//28)%len(present)]; status=rt['resident_status'][rid]; status.update(present=False,last_change=day)
            if rid in pop: pop[rid]['visible']=False
            rt['summary']['departures']+=1; society.setdefault('migration',{}).setdefault('history',[]).append({'day':day,'kind':'departure','resident':rid})
            events.append(self._event(rt,state,'departure',f"{pop.get(rid,{}).get('name',rid)} has left Bellwether for now.",{'resident':rid}))
        elif away and pressure<=.2 and outlook=='stable' and day%21==0:
            rid=sorted(away)[(day//21)%len(away)]; status=rt['resident_status'][rid]; status.update(present=True,last_change=day)
            if rid in pop: pop[rid]['visible']=True
            rt['summary']['arrivals']+=1; society.setdefault('migration',{}).setdefault('history',[]).append({'day':day,'kind':'return','resident':rid})
            events.append(self._event(rt,state,'return',f"{pop.get(rid,{}).get('name',rid)} has returned to Bellwether.",{'resident':rid}))
        # Household changes materialise earlier NPC-life considerations into actual, auditable moves.
        considerations=[e for e in state.get('npc_autonomous_lives',{}).get('life_events',[]) if e.get('kind')=='household_consideration' and int(e.get('day',0))<day]
        if considerations and day%35==0:
            rid=considerations[-1].get('actor'); r=pop.get(rid)
            if r:
                old=r.get('household','unknown'); new=f"household_{rid}_independent"; r['household']=new
                rt['resident_status'][rid].update(household=new,last_change=day); rt['summary']['moves']+=1
                events.append(self._event(rt,state,'household_move',f"{r.get('name',rid)} has changed household arrangements.",{'resident':rid,'from':old,'to':new}))
        # Existing business health can produce a structural closure record; recovery can reopen it.
        for bid,b in businesses.items():
            v=rt['ventures'].setdefault(bid,{'kind':'established','status':'open','opened_day':1,'closed_day':None})
            if float(b.get('health',100))<=8 and v['status']=='open':
                v.update(status='closed',closed_day=day);rt['summary']['closures']+=1
                events.append(self._event(rt,state,'business_closure',f"A village business has closed under sustained strain.",{'business':bid}))
            elif float(b.get('health',0))>=35 and v['status']=='closed' and day-int(v.get('closed_day') or day)>=14:
                v.update(status='open',opened_day=day);rt['summary']['openings']+=1
                events.append(self._event(rt,state,'business_reopening',f"A previously closed village business has reopened.",{'business':bid}))
        # New small ventures emerge from stable conditions and resident self-employment signals.
        self_employed=[rid for rid,r in pop.items() if 'self-employed' in str(r.get('occupation','')).lower() and rt['resident_status'].get(rid,{}).get('present',True)]
        if self_employed and outlook=='stable' and day%42==0:
            rid=sorted(self_employed)[0]; vid=f"resident_venture_{rid}"
            if vid not in rt['ventures']:
                rt['ventures'][vid]={'kind':'resident_venture','owner':rid,'status':'open','opened_day':day,'closed_day':None};rt['summary']['openings']+=1
                events.append(self._event(rt,state,'business_opening',f"A resident has begun a small independent village venture.",{'venture':vid,'owner':rid}))
        # Land use changes only after sustained time, and remain presentation/simulation state rather than world-map rewrites.
        if day%56==0:
            key=['lower_meadow_edge','old_orchard_margin','workshop_yard_rear'][(day//56)%3]; old=rt['land_use'].get(key,'underused'); new='cultivated' if outlook=='stable' else 'neglected'
            if new!=old:
                rt['land_use'][key]=new;rt['summary']['land_changes']+=1
                events.append(self._event(rt,state,'land_use_change',f"The use of a small piece of village land has visibly changed.",{'parcel':key,'from':old,'to':new}))
        return events
    def public(self,state):
        rt=self.migrate(state);return {'summary':deepcopy(rt['summary']),'ventures':deepcopy(rt['ventures']),'land_use':deepcopy(rt['land_use']),'recent_events':deepcopy(rt['events'][-20:])}
VILLAGE_EVOLUTION_MODEL=VillageEvolutionModel()
