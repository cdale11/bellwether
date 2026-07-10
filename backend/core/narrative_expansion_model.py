"""v2.9.0 authored narrative expansion.

Deterministic, spoiler-bounded connective scenes. This layer never lets an LLM create
canon: it observes authoritative story/simulation state and emits authored scenes once.
"""
from copy import deepcopy

SCENES = {
 "arrival_after_letter": {"chapter":"arrival","speaker":"Eleanor's Letter","text":"Learn the ordinary shape of the place first. A contradiction means little until you know what it contradicts.","requires":{"flag":"read_letter"}},
 "ordinary_first_roots": {"chapter":"ordinary_life","speaker":"Narrator","text":"Bellwether begins to separate into habits: who opens early, which paths stay muddy, where people pause before answering. Familiarity makes the first wrong detail harder to dismiss.","requires":{"ordinary":6,"familiar":1}},
 "archive_crosscheck": {"chapter":"distributed_archive","speaker":"Notebook","text":"Eleanor did not leave one archive. She left checks against checks: a place against a record, a routine against a recollection, one person's certainty against another's.","requires":{"evidence":5,"active":2}},
 "witness_mara": {"chapter":"witnesses","speaker":"Mara","text":"I can tell you what I remember. I can't promise the village remembers it the same way.","requires":{"npc":"mara","trust":3}},
 "witness_jonah": {"chapter":"witnesses","speaker":"Jonah","text":"Timetables are useful because they are meant to agree with themselves. Around here, that makes them unusually honest witnesses.","requires":{"npc":"jonah","trust":3}},
 "boundary_return": {"chapter":"boundaries","speaker":"Notebook","text":"The recurring mistake is to treat every contradiction as an isolated event. Roads, records and recollections may be different surfaces of the same correction.","requires":{"active":4,"disruptions":2}},
 "chorus_living_pattern": {"chapter":"chorus_shape","speaker":"Narrator","text":"The pattern is clearest when nothing dramatic happens. A habit shifts, a bird route changes, a story loses one detail, and three unrelated systems lean in the same direction.","requires":{"deep":1,"connections":2}},
 "eleanor_anchor_method": {"chapter":"eleanor_method","speaker":"Eleanor's Notes","text":"Do not trust a single anchor. Make ordinary things corroborate one another. A person, a place, a written record, a repeated task. Correction has more work to do when truth is distributed.","requires":{"evidence":10,"trusted":2}},
 "convergence_choice": {"chapter":"convergence","speaker":"Narrator","text":"You understand now why Eleanor's work looked so domestic. A life can be evidence. A friendship can be a boundary. Routine can conceal you, or teach the village exactly where to press.","requires":{"ordinary":18,"trusted":3}},
}

class NarrativeExpansionModel:
 def runtime_defaults(self): return {"schema_version":1,"seen":[],"history":[],"chapter_entries":[]}
 def migrate(self,state):
  rt=state.setdefault("authored_narrative",self.runtime_defaults())
  for k,v in self.runtime_defaults().items(): rt.setdefault(k,deepcopy(v))
  return rt
 def metrics(self,s):
  life=s.get('player_life',{}); inv=s.get('investigation',{}); graph=s.get('mystery_investigation',{}); rel=s.get('relationships',{})
  return {"ordinary":len(life.get('activity_history',[])),"familiar":sum(v>=6 for v in life.get('location_familiarity',{}).values()),"evidence":len(inv.get('evidence',[])),"active":sum(p.get('status')!='unopened' for p in graph.get('mystery_progress',{}).values()),"deep":sum(p.get('status')=='deepening' for p in graph.get('mystery_progress',{}).values()),"connections":len(graph.get('connections',[])),"disruptions":s.get('psychological_state',{}).get('familiarity_disruptions',0),"trusted":sum(isinstance(r,dict) and r.get('trust',0)>=3 for r in rel.values())}
 def ready(self,s,scene):
  req=scene.get('requires',{}); m=self.metrics(s)
  if req.get('flag') and not s.get('flags',{}).get(req['flag']): return False
  for k in ('ordinary','familiar','evidence','active','deep','connections','disruptions','trusted'):
   if k in req and m[k] < req[k]: return False
  if 'npc' in req:
   r=s.get('relationships',{}).get(req['npc'],{})
   if r.get('trust',0)<req.get('trust',0): return False
  return True
 def evaluate(self,state):
  rt=self.migrate(state); chapter=state.get('authored_story',{}).get('chapter','arrival'); out=[]
  if chapter not in rt['chapter_entries']:
   rt['chapter_entries'].append(chapter)
  for sid,scene in SCENES.items():
   if sid in rt['seen'] or scene['chapter']!=chapter or not self.ready(state,scene): continue
   rt['seen'].append(sid); row={"id":sid,"chapter":chapter,"day":state.get('day'),"speaker":scene['speaker'],"text":scene['text']}; rt['history'].append(row); out.append(row)
  rt['history']=rt['history'][-60:]
  return out
 def public(self,state):
  rt=self.migrate(state); return {"seen_count":len(rt['seen']),"recent":[{"id":x['id'],"chapter":x['chapter'],"day":x['day']} for x in rt['history'][-8:]]}

NARRATIVE_EXPANSION_MODEL=NarrativeExpansionModel()
