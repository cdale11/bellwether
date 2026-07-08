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
