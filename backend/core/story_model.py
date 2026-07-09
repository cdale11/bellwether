"""v1.0 RC1 authored story spine: deterministic gates from arrival to ending eligibility."""
from copy import deepcopy

CHAPTERS = [
 {'id':'arrival','title':'The House Left Waiting','objective':'Reach Ashcroft Cottage and read Eleanor’s letter.','location':'ashcroft_cottage'},
 {'id':'ordinary_life','title':'Learn the Shape of the Days','objective':'Live in Bellwether long enough to learn its ordinary rhythms.','location':'village_green'},
 {'id':'distributed_archive','title':'Eleanor’s Distributed Archive','objective':'Connect evidence from several places and parts of village life.','location':'ashcroft_cottage'},
 {'id':'witnesses','title':'Incompatible Witnesses','objective':'Build trust and compare what Bellwether’s residents remember.','location':'village_green'},
 {'id':'boundaries','title':'The Ways That Return','objective':'Investigate Bellwether’s routes, boundaries, records, and repeated patterns.','location':'old_quarry'},
 {'id':'chorus_shape','title':'A Shape Behind the Pattern','objective':'Bring social, geographic, ecological, historical, and recurrence evidence together.','location':'ashcroft_cottage'},
 {'id':'eleanor_method','title':'What Eleanor Was Trying to Preserve','objective':'Understand Eleanor’s method of anchoring truth across ordinary life.','location':'ashcroft_cottage'},
 {'id':'convergence','title':'The Village and the Choice','objective':'Prepare the people, knowledge, identity, and anchors needed for a final resolution.','location':'village_green'},
]

class StoryModel:
 schema_version=1
 def runtime_defaults(self):
  return {'schema_version':1,'chapter':'arrival','completed':[],'revelations':[],'ending_eligible':False,'gate_history':[],'last_gate_day':None}
 def migrate(self,state):
  rt=state.setdefault('authored_story',self.runtime_defaults())
  for k,v in self.runtime_defaults().items(): rt.setdefault(k,deepcopy(v))
  rt['schema_version']=1
  return rt
 def _metrics(self,s):
  life=s.get('player_life',{}); inv=s.get('investigation',{}); graph=s.get('mystery_investigation',{})
  rels=s.get('relationships',{})
  familiar=sum(1 for v in life.get('location_familiarity',{}).values() if v>=6)
  trusted=sum(1 for r in rels.values() if isinstance(r,dict) and r.get('trust',0)>=3)
  active=sum(1 for p in graph.get('mystery_progress',{}).values() if p.get('status')!='unopened')
  deep=sum(1 for p in graph.get('mystery_progress',{}).values() if p.get('status')=='deepening')
  supported=sum(1 for h in graph.get('hypotheses',{}).values() if isinstance(h,dict) and h.get('status')=='supported')
  rec=s.get('recurrence',{})
  anchors=sum(1 for a in rec.get('anchors',{}).values() if (a.get('strength',0) if isinstance(a,dict) else a)>=1)
  return {'ordinary':len(life.get('activity_history',[])),'familiar':familiar,'evidence':len(inv.get('evidence',[])),
   'trusted':trusted,'active_mysteries':active,'deep_mysteries':deep,'supported_hypotheses':supported,
   'disruptions':s.get('psychological_state',{}).get('familiarity_disruptions',0),'anchors':anchors,
   'recurrence_index':rec.get('run_index',rec.get('recurrence_index',0)),'story_beats':len(s.get('story_integration',{}).get('unlocked_beats',[]))}
 def gate_ready(self,s,chapter):
  m=self._metrics(s); f=s.get('flags',{})
  rules={
   'arrival': f.get('read_letter',False),
   'ordinary_life': m['ordinary']>=8 and m['familiar']>=2,
   'distributed_archive': m['evidence']>=6 and m['active_mysteries']>=3,
   'witnesses': m['trusted']>=2 and sum(r.get('familiarity',0) for r in s.get('relationships',{}).values() if isinstance(r,dict))>=16,
   'boundaries': m['active_mysteries']>=5 and m['disruptions']>=3,
   'chorus_shape': m['deep_mysteries']>=2 and (m['supported_hypotheses']>=2 or m['evidence']>=12),
   'eleanor_method': m['story_beats']>=2 and (m['anchors']>=1 or m['trusted']>=3) and m['evidence']>=12,
   'convergence': m['active_mysteries']>=6 and m['trusted']>=3 and m['familiar']>=4 and m['ordinary']>=20 and m['disruptions']>=4,
  }
  return bool(rules.get(chapter,False))
 def current(self,state):
  rt=self.migrate(state); return next((c for c in CHAPTERS if c['id']==rt['chapter']),CHAPTERS[-1])
 def advance_if_ready(self,state):
  rt=self.migrate(state); cid=rt['chapter']
  if rt.get('ending_eligible') or not self.gate_ready(state,cid): return None
  idx=next(i for i,c in enumerate(CHAPTERS) if c['id']==cid)
  if cid not in rt['completed']: rt['completed'].append(cid)
  messages={
   'arrival':('Eleanor’s letter is not an explanation. It is an invitation to learn the village before judging it.','ordinary_life'),
   'ordinary_life':('Because you know the ordinary days now, the small contradictions have somewhere to stand. Eleanor hid her work among ordinary things.','distributed_archive'),
   'distributed_archive':('No single notebook contains Eleanor’s argument. The archive is distributed across places, routines, records, objects, and people.','witnesses'),
   'witnesses':('The contradictions are not identical from person to person. Bellwether seems to preserve some kinds of memory while correcting others.','boundaries'),
   'boundaries':('Roads, records, walls, and recollections disagree in patterned ways. The boundary is not merely geographic.','chorus_shape'),
   'chorus_shape':('The pattern behaves less like a haunting than a network: memory, routine, place, and emotion reinforcing one another.','eleanor_method'),
   'eleanor_method':('Eleanor’s method becomes legible: independent relationships, records, routines, and meaningful objects can anchor one another against correction.','convergence'),
   'convergence':('You have lived enough of Bellwether to understand that no final choice can be only about escape. The conditions for resolution are now present.',None),
  }
  text,nxt=messages[cid]
  rt['revelations'].append({'id':cid,'day':state.get('day'),'text':text}); rt['gate_history'].append({'chapter':cid,'day':state.get('day')}); rt['last_gate_day']=state.get('day')
  if nxt: rt['chapter']=nxt
  else: rt['ending_eligible']=True
  return {'completed':cid,'next':nxt,'text':text,'ending_eligible':rt['ending_eligible']}
 def public(self,state):
  rt=self.migrate(state); cur=self.current(state)
  return {'chapter':cur['id'],'title':cur['title'],'objective':cur['objective'],'completed':list(rt['completed']),
   'revelations':deepcopy(rt['revelations']),'ending_eligible':bool(rt['ending_eligible'])}

STORY_MODEL=StoryModel()
