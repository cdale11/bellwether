"""Cottage-scale animal simulation.

Deterministic state owns health, hunger, trust, shelter and production.  The LLM
may choose only a bounded intention from legal candidates; applying an intention
cannot create/delete animals or directly mutate health/production.
"""
from copy import deepcopy

SPECIES={
 'chicken':{'name':'Chicken','shelter':'coop','product':'egg','product_days':1,'feed_per_day':1},
 'duck':{'name':'Duck','shelter':'coop','product':'duck_egg','product_days':2,'feed_per_day':1},
 'goat':{'name':'Goat','shelter':'goat_shed','product':'milk','product_days':2,'feed_per_day':2},
}
INTENTS={
 'forage':{'label':'Forage around the cottage boundary'},
 'shelter':{'label':'Stay close to shelter'},
 'approach_player':{'label':'Approach the player'},
 'avoid_player':{'label':'Keep distance from the player'},
 'socialise':{'label':'Stay near the other animals'},
 'rest':{'label':'Rest quietly'},
}

class AnimalModel:
 def runtime_defaults(self):
  return {'schema_version':1,'animals':{},'shelters':{'coop':False,'goat_shed':False},'feed':0,'products':{},'next_id':1,'last_daily_day':0,'intention_history':[],'last_llm_review_day':0}
 def migrate(self,s):
  rt=s.setdefault('cottage_animals',self.runtime_defaults()); d=self.runtime_defaults()
  for k,v in d.items(): rt.setdefault(k,deepcopy(v))
  for a in rt['animals'].values():
   a.setdefault('health',100);a.setdefault('hunger',0);a.setdefault('trust',0);a.setdefault('intention','rest');a.setdefault('last_product_day',s.get('day',1));a.setdefault('production_ready',False)
  return rt
 def add(self,s,species,name=None):
  rt=self.migrate(s); i=f"animal_{rt['next_id']}";rt['next_id']+=1
  rt['animals'][i]={'id':i,'species':species,'name':name or f"{SPECIES[species]['name']} {rt['next_id']-1}",'health':100,'hunger':10,'trust':0,'intention':'rest','last_product_day':s.get('day',1),'production_ready':False}
  return rt['animals'][i]
 def legal_intentions(self,s,animal_id):
  rt=self.migrate(s); a=rt['animals'].get(animal_id)
  if not a:return []
  out=['rest','shelter']
  if a['hunger']>=35:out.insert(0,'forage')
  if a['trust']>=15:out.append('approach_player')
  else:out.append('avoid_player')
  if len(rt['animals'])>1:out.append('socialise')
  return [{'id':x,'label':INTENTS[x]['label']} for x in dict.fromkeys(out)]
 def compact_context(self,s,animal_id):
  rt=self.migrate(s);a=rt['animals'][animal_id]
  return {'animal':{'species':a['species'],'health':a['health'],'hunger':a['hunger'],'trust':a['trust']},'weather':s.get('weather',{}).get('state'),'season':s.get('season',{}).get('id'),'other_animals':max(0,len(rt['animals'])-1)}
 def apply_intention(self,s,animal_id,intention,source='llm'):
  legal={x['id'] for x in self.legal_intentions(s,animal_id)}
  if intention not in legal:return False
  rt=self.migrate(s);rt['animals'][animal_id]['intention']=intention
  rt['intention_history'].append({'day':s.get('day',1),'animal_id':animal_id,'intention':intention,'source':source});rt['intention_history']=rt['intention_history'][-80:]
  return True
 def advance_day(self,s):
  rt=self.migrate(s);day=int(s.get('day',1)); events=[]
  if rt['last_daily_day']>=day:return events
  rt['last_daily_day']=day
  for a in rt['animals'].values():
   spec=SPECIES[a['species']]; fed=rt['feed']>=spec['feed_per_day']
   if fed:rt['feed']-=spec['feed_per_day'];a['hunger']=max(0,a['hunger']-35)
   else:a['hunger']=min(100,a['hunger']+28)
   sheltered=rt['shelters'].get(spec['shelter'],False)
   weather=s.get('weather',{}).get('state','')
   harsh=weather in {'storm','heavy_rain','snow','blizzard'} or s.get('weather',{}).get('temperature_c',10)<1
   if a['hunger']>=80:a['health']=max(0,a['health']-12)
   elif harsh and not sheltered:a['health']=max(0,a['health']-8)
   else:a['health']=min(100,a['health']+2)
   intent=a.get('intention','rest')
   if intent=='forage':a['hunger']=max(0,a['hunger']-12)
   elif intent=='approach_player':a['trust']=min(100,a['trust']+2)
   if a['health']>=60 and a['hunger']<65 and day-a['last_product_day']>=spec['product_days']:
    a['production_ready']=True
   if a['health']<40:events.append(f"{a['name']} is looking unwell and needs attention.")
  return events
 def collect(self,s):
  rt=self.migrate(s);day=s.get('day',1);collected={}
  for a in rt['animals'].values():
   if a.get('production_ready'):
    p=SPECIES[a['species']]['product'];rt['products'][p]=rt['products'].get(p,0)+1;collected[p]=collected.get(p,0)+1;a['production_ready']=False;a['last_product_day']=day;a['trust']=min(100,a['trust']+1)
  return collected
 def public(self,s):
  rt=self.migrate(s)
  return {'animals':[deepcopy(a) for a in rt['animals'].values()],'shelters':deepcopy(rt['shelters']),'feed':rt['feed'],'products':deepcopy(rt['products']),'recent_intentions':deepcopy(rt['intention_history'][-10:])}

ANIMAL_MODEL=AnimalModel()
