"""v2.5 authored player romance and household progression.
Bounded to explicitly authored eligible core NPCs; no LLM can create relationship canon.
"""
from copy import deepcopy

ROUTES={
 'jonah':{'name':'Jonah','date_location':'village_green','date_label':'Spend an unhurried evening with Jonah'},
 'mara':{'name':'Mara','date_location':'riverside_path','date_label':'Take a quiet riverside walk with Mara'},
}

class RelationshipLifeModel:
 SCHEMA_VERSION=1
 def defaults(self):
  return {'schema_version':1,'routes':{nid:{'stage':'friends','dates':0,'shared_days':0,'history':[]} for nid in ROUTES},'partner':None,'cohabiting':False,'family_intent':'undiscussed','household_events':[],'last_daily_day':0}
 def migrate(self,s):
  rt=s.setdefault('relationship_life',self.defaults())
  for k,v in self.defaults().items(): rt.setdefault(k,deepcopy(v))
  for nid in ROUTES:
   row=rt['routes'].setdefault(nid,{'stage':'friends','dates':0,'shared_days':0,'history':[]})
   for k,v in {'stage':'friends','dates':0,'shared_days':0,'history':[]}.items():row.setdefault(k,deepcopy(v))
  return rt
 def _eligible(self,s,nid):
  r=s.get('relationships',{}).get(nid,{})
  return int(r.get('affinity',0))>=25 and int(r.get('trust',0))>=25 and int(r.get('familiarity',0))>=35
 def actions(self,s):
  rt=self.migrate(s); out=[]; loc=s.get('location'); partner=rt.get('partner')
  for nid,cfg in ROUTES.items():
   npc=s.get('npcs',{}).get(nid,{}); row=rt['routes'][nid]
   if npc.get('visible',True) and npc.get('location')==loc:
    if row['stage']=='friends' and self._eligible(s,nid) and not partner: out.append((f'relationship:interest:{nid}',f'Tell {cfg["name"]} you would like to spend time together'))
    elif row['stage']=='courting' and not partner: out.append((f'relationship:commit:{nid}',f'Talk honestly with {cfg["name"]} about becoming partners'))
   if row['stage'] in {'courting','partner'} and loc==cfg['date_location']: out.append((f'relationship:date:{nid}',cfg['date_label']))
  if partner and loc=='ashcroft_cottage':
   if not rt['cohabiting'] and 'upper_room' in s.get('property',{}).get('cottage_expansion',{}).get('completed',[]): out.append(('relationship:cohabit','Ask your partner to make a home with you'))
   if rt['cohabiting'] and rt['family_intent']=='undiscussed': out.append(('relationship:family_talk','Talk together about whether you want a family'))
  return out
 def perform(self,s,action):
  rt=self.migrate(s); parts=action.split(':'); kind=parts[1]; nid=parts[2] if len(parts)>2 else rt.get('partner')
  if kind=='interest' and nid in ROUTES and self._eligible(s,nid) and not rt.get('partner'):
   rt['routes'][nid]['stage']='courting'; rt['routes'][nid]['history'].append({'day':s.get('day',1),'event':'interest acknowledged'}); return True,f"You and {ROUTES[nid]['name']} agree to see what this might become, without pretending certainty.",30
  if kind=='date' and nid in ROUTES and rt['routes'][nid]['stage'] in {'courting','partner'} and s.get('location')==ROUTES[nid]['date_location']:
   row=rt['routes'][nid]; row['dates']+=1; row['history'].append({'day':s.get('day',1),'event':'spent deliberate time together'}); rel=s['relationships'][nid]; rel['affinity']=min(100,rel['affinity']+2); rel['trust']=min(100,rel['trust']+2); return True,f"The time with {ROUTES[nid]['name']} is ordinary enough to matter: attention, pauses, and things remembered later.",90
  if kind=='commit' and nid in ROUTES and rt['routes'][nid]['stage']=='courting' and rt['routes'][nid]['dates']>=2 and int(s['relationships'][nid].get('trust',0))>=30 and not rt.get('partner'):
   rt['partner']=nid; rt['routes'][nid]['stage']='partner'; rt['routes'][nid]['history'].append({'day':s.get('day',1),'event':'partnership begun'}); return True,f"You and {ROUTES[nid]['name']} choose a relationship deliberately. The village will notice in its own time.",45
  if kind=='cohabit' and rt.get('partner') and 'upper_room' in s.get('property',{}).get('cottage_expansion',{}).get('completed',[]):
   rt['cohabiting']=True; rt['household_events'].append({'day':s.get('day',1),'event':'cohabitation began','npc':rt['partner']}); return True,'Ashcroft Cottage becomes a shared household. Space, routines and obligations now belong to more than one person.',240
  if kind=='family_talk' and rt.get('cohabiting'):
   rt['family_intent']='open_to_future'; rt['household_events'].append({'day':s.get('day',1),'event':'family future discussed'}); return True,'You talk about family without turning the conversation into a promise or a deadline. The possibility is now part of your shared future.',60
  return False,'That relationship step is not available yet.',0
 def daily_tick(self,s):
  rt=self.migrate(s); day=int(s.get('day',1))
  if day<=int(rt.get('last_daily_day',0)):return None
  rt['last_daily_day']=day
  if rt.get('partner'): rt['routes'][rt['partner']]['shared_days']+=1
  return {'partner':rt.get('partner'),'cohabiting':rt.get('cohabiting',False)}
 def public(self,s):
  rt=self.migrate(s); return {'partner':rt.get('partner'),'cohabiting':rt.get('cohabiting',False),'family_intent':rt.get('family_intent'),'routes':deepcopy(rt.get('routes',{}))}
RELATIONSHIP_LIFE_MODEL=RelationshipLifeModel()
