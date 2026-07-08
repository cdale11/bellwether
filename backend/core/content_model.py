"""Part 16 content and prose integration layer.

Deepens ordinary life with cooking and cottage restoration, and provides bounded
season/weather prose variants. Canon remains authored; runtime progression is save state.
"""
RECIPES={
 'radish_toast':{'name':'Radish and butter toast','requires':{'radish':2},'household':{'bread_loaf':1},'minutes':25,'meals':1,'skill':2},
 'garden_salad':{'name':'Garden salad','requires':{'lettuce':1,'radish':1},'household':{},'minutes':20,'meals':1,'skill':2},
 'carrot_soup':{'name':'Carrot soup','requires':{'carrot':3},'household':{'groceries':1},'minutes':45,'meals':2,'skill':4},
 'bean_stew':{'name':'Broad bean stew','requires':{'broad_bean':3},'household':{'groceries':1},'minutes':50,'meals':2,'skill':5},
}
REPAIRS={
 'kitchen_stove':{'name':'service the old kitchen stove','cost_supplies':1,'minutes':60,'care':12},
 'bedroom_window':{'name':'seal the draughty bedroom window','cost_supplies':1,'minutes':50,'care':10},
 'garden_gate':{'name':'repair the garden gate','cost_supplies':1,'minutes':45,'care':10},
}
SEASONAL_COTTAGE={
 'early_spring':'Cold light finds every smear on the old glass. Damp earth smells newly awake beyond the back door.',
 'late_spring':'The hedge is noisy with nesting birds, and the kitchen window stands open without making the room cold.',
 'early_summer':'Long light rests on the floorboards. The garden presses green against the windows.',
 'high_summer':'The cottage holds the day’s warmth in its stone walls while insects tick softly against the evening glass.',
 'late_summer':'The rooms smell faintly of dry herbs and warm dust; dusk arrives a little earlier than you expect.',
 'early_autumn':'Leaves gather against the garden wall and the kettle feels useful again.',
 'late_autumn':'Rain works patiently at the windows. The cottage seems smaller, warmer, and more separate from the lanes outside.',
 'early_winter':'The rooms cool quickly when the stove dies down. Every repaired draught now matters.',
 'deep_winter':'Frost feathers the outside of the glass. Indoors, small routines become a kind of architecture.',
 'late_winter':'The light is returning, though the cottage still wakes cold and the garden remains mostly patient earth.',
}
class ContentModel:
 def runtime_defaults(self):
  return {'schema_version':1,'cooking':{'recipes_known':list(RECIPES),'meals_cooked':0,'history':[]},'home_restoration':{'completed':[],'history':[]},'content_beats':[]}
 def cooking_actions(self,state):
  if state.get('location')!='ashcroft_cottage': return []
  rt=state.setdefault('content_progression',self.runtime_defaults()); store=state['player_activities']['garden']['harvest_store']; house=state['economy']['household']; out=[]
  for rid in rt['cooking']['recipes_known']:
   r=RECIPES[rid]
   if all(store.get(k,0)>=v for k,v in r['requires'].items()) and all(house.get(k,0)>=v for k,v in r['household'].items()): out.append((f'content:cook:{rid}',f"Cook {r['name']}"))
  return out
 def repair_actions(self,state):
  if state.get('location')!='ashcroft_cottage': return []
  done=set(state.setdefault('content_progression',self.runtime_defaults())['home_restoration']['completed']); supplies=state['economy']['household'].get('repair_supplies',0)
  if supplies<=0:return []
  return [(f'content:repair:{rid}',f"Repair: {r['name'].title()}") for rid,r in REPAIRS.items() if rid not in done]
 def cook(self,state,rid):
  if rid not in RECIPES or state.get('location')!='ashcroft_cottage':return False,'You cannot cook that here.',0
  r=RECIPES[rid]; store=state['player_activities']['garden']['harvest_store']; house=state['economy']['household']
  if not all(store.get(k,0)>=v for k,v in r['requires'].items()) or not all(house.get(k,0)>=v for k,v in r['household'].items()):return False,'You no longer have the ingredients.',0
  for k,v in r['requires'].items():store[k]-=v
  for k,v in r['household'].items():house[k]-=v
  rt=state['content_progression']['cooking']; rt['meals_cooked']+=1; rt['history'].append({'day':state['day'],'recipe':rid}); rt['history']=rt['history'][-40:]
  state['player_life']['meals']+=r['meals']; state['player_activities']['skills']['cooking']+=r['skill']
  return True,f"You cook {r['name']}. The work is ordinary and absorbing, and the cottage smells inhabited afterward.",r['minutes']
 def repair(self,state,rid):
  if rid not in REPAIRS or state.get('location')!='ashcroft_cottage':return False,'You cannot repair that here.',0
  rt=state['content_progression']['home_restoration']; r=REPAIRS[rid]
  if rid in rt['completed']:return False,'That repair is already finished.',0
  house=state['economy']['household']
  if house.get('repair_supplies',0)<r['cost_supplies']:return False,'You need repair supplies.',0
  house['repair_supplies']-=r['cost_supplies']; rt['completed'].append(rid); rt['history'].append({'day':state['day'],'repair':rid})
  state['player_life']['cottage_care']=min(100,state['player_life']['cottage_care']+r['care']); state['player_activities']['skills']['home_care']+=3
  return True,f"You {r['name']}. It takes patience, but afterward the change is tangible.",r['minutes']
 def seasonal_cottage_text(self,state):return SEASONAL_COTTAGE.get(state.get('season',{}).get('id'),'The cottage settles around you.')
CONTENT_MODEL=ContentModel()

# v0.4.0 ordinary-life layer. Kept in the existing content domain so cottage,
# cooking and restoration share one persistent source of truth.
DAILY_HOME_ACTIONS = {
 'air_rooms': {'label':'Open the Windows and Air the Rooms','minutes':15,'care':2,'comfort':3},
 'laundry': {'label':'Wash and Hang a Load of Laundry','minutes':55,'care':4,'comfort':4},
 'sweep_hearth': {'label':'Sweep the Hearth and Set the Room Right','minutes':25,'care':3,'comfort':3},
 'plan_day': {'label':'Plan the Day at the Kitchen Table','minutes':15,'care':0,'comfort':2},
}

def _v040_migrate(self, state):
 rt=state.setdefault('content_progression', self.runtime_defaults())
 rt.setdefault('schema_version',2)
 daily=rt.setdefault('daily_life',{})
 daily.setdefault('comfort',20)
 daily.setdefault('routine_streak',0)
 daily.setdefault('last_active_day',0)
 daily.setdefault('today',{'day':state.get('day',1),'home':0,'garden':0,'cooked':0,'social':0,'work':0})
 daily.setdefault('day_log',[])
 daily.setdefault('chores_done',{})
 return rt

def _v040_home_actions(self,state):
 if state.get('location')!='ashcroft_cottage': return []
 rt=_v040_migrate(self,state); daily=rt['daily_life']; day=str(state.get('day',1)); done=set(daily['chores_done'].get(day,[]))
 out=[]
 for aid,spec in DAILY_HOME_ACTIONS.items():
  if aid not in done: out.append((f'content:home:{aid}',spec['label']))
 return out

def _v040_home_action(self,state,aid):
 if state.get('location')!='ashcroft_cottage' or aid not in DAILY_HOME_ACTIONS:return False,'You cannot do that here.',0
 rt=_v040_migrate(self,state); daily=rt['daily_life']; day=str(state.get('day',1)); done=daily['chores_done'].setdefault(day,[])
 if aid in done:return False,'You have already done that today.',0
 spec=DAILY_HOME_ACTIONS[aid]; done.append(aid); daily['comfort']=min(100,daily['comfort']+spec['comfort']); daily['today']['home']+=1
 state['player_life']['cottage_care']=min(100,state['player_life'].get('cottage_care',0)+spec['care'])
 state['player_activities']['skills']['home_care']=min(100,state['player_activities']['skills'].get('home_care',0)+1)
 prose={
  'air_rooms':'You unlatch the windows one by one. Cool air moves through the cottage, carrying out the closed-up smell and bringing in birdsong and damp earth.',
  'laundry':'You work through a basin of washing, wring each piece by hand, and hang the line in the garden. By the end, the cottage feels less borrowed.',
  'sweep_hearth':'You sweep ash, straighten the chairs and clear the small drift of everyday clutter. The room answers care with comfort.',
  'plan_day':'You sit with tea and a scrap of paper, balancing weather, errands, work and the garden. The day begins to have a shape.'}
 return True,prose[aid],spec['minutes']

def _v040_note_activity(self,state,kind):
 rt=_v040_migrate(self,state); today=rt['daily_life']['today']
 if today.get('day')!=state.get('day'):
  rt['daily_life']['today']={'day':state.get('day',1),'home':0,'garden':0,'cooked':0,'social':0,'work':0}; today=rt['daily_life']['today']
 if kind in today: today[kind]+=1

def _v040_close_day(self,state):
 rt=_v040_migrate(self,state); d=rt['daily_life']; today=d['today']; active=sum(today.get(k,0) for k in ('home','garden','cooked','social','work'))
 varied=sum(1 for k in ('home','garden','cooked','social','work') if today.get(k,0)>0)
 if active>=2: d['routine_streak']=d.get('routine_streak',0)+1; d['last_active_day']=today['day']
 else: d['routine_streak']=0
 d['comfort']=max(0,min(100,d['comfort'] + varied - 1))
 summary={'day':today['day'],'activities':active,'variety':varied,'comfort':d['comfort'],'routine_streak':d['routine_streak']}
 d['day_log'].append(summary); d['day_log']=d['day_log'][-14:]
 d['today']={'day':state.get('day',1)+1,'home':0,'garden':0,'cooked':0,'social':0,'work':0}
 return summary

ContentModel.migrate_v040=_v040_migrate
ContentModel.home_actions=_v040_home_actions
ContentModel.home_action=_v040_home_action
ContentModel.note_activity=_v040_note_activity
ContentModel.close_day=_v040_close_day
