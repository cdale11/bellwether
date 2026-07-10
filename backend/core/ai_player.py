"""v3.20.0 autonomous QA laboratory with unified evidence-based morning reporting."""
from copy import deepcopy
from threading import RLock,Thread,Event
from collections import deque
import time
import json
import os
import subprocess
from pathlib import Path
from backend.ai.async_runtime import ASYNC_AI_RUNTIME
from backend.ai.provider import provider
from backend.core.action_surface import compact as compact_action_surface
BLOCKED_PREFIXES=("story:","ending:","horror:","recurrence:")
BLOCKED_KINDS={"story","choice","talk"}
GOAL_WORDS={"movement":("travel","walk","visit","return","go to"),"npc_interaction":("talk","speak","help","conversation"),"relationships":("talk","speak","help","conversation"),"economy":("buy","sell","shop","purchase","support"),"jobs":("job","work","shift","apply"),"gardening":("garden","soil","weed","water","plant","sow","harvest","cottage"),"investigation":("observe","examine","review","lead","investigat"),"procedural_content":("offer to help","errand","opportunity","favour","favor"),"cooking":("cook","preserve","meal","food"),"hobbies":("hobby","fish","forage","bird","sketch","history"),"community":("community","workday","care walk","churchyard upkeep","share a simple meal"),"society":("exchange a few words","resident","community","social"),"employment_change":("job","work","shift","apply","leave job") }
PASSIVE=("look around","take a moment","wait and observe","sit by","review what","observe carefully","watch for birds","make a sketch","research local history","go foraging")

def safe_actions(game,allow_investigation=True,comprehensive=False):
 out=[]
 for a in compact_action_surface(game.actions()):
  aid=a.get("id","");kind=a.get("kind","")
  if not comprehensive and (aid.startswith(BLOCKED_PREFIXES) or kind in BLOCKED_KINDS):continue
  if not allow_investigation and (aid.startswith("investigate:") or kind=="investigate"):continue
  if kind=="free_talk":continue
  out.append(a)
 return out

def _compact_state(game,memory,target):
 s=game.state;recent=','.join(list(memory.get('recent_actions',[]))[-5:]);blocked=','.join(list(memory.get('blocked_actions',[]))[:5]);garden=s.get('player_activities',{}).get('garden',{});seeds=sum(garden.get('seed_stock',{}).values()) if isinstance(garden,dict) else 0
 return f"D{s.get('day')} T{s.get('minute')} AT={s.get('location')} M={s.get('money')} TARGET={target or '-'} SEEDS={seeds} RECENT={recent or '-'} BLOCKED={blocked or '-'}"

def _action_text(a):
 return (a.get("id","")+" "+a.get("kind","")+" "+a.get("label","")).lower()

def _goal_stage(game,target,actions):
 """Return an inspectable prerequisite stage; never invent actions that are not legal."""
 s=game.state; loc=s.get("location"); texts=[_action_text(a) for a in actions]
 if target=="cooking":
  if any(a.get("id","").startswith(("content:cook:","lifesim:preserve:")) for a in actions): return "perform_cooking"
  pantry=s.get("life_simulation",{}).get("pantry",{}); household=s.get("economy",{}).get("household",{})
  has_food=sum(int(v or 0) for v in pantry.values())>0 or int(household.get("groceries",0) or 0)>0
  store=s.get("player_activities",{}).get("garden",{}).get("harvest_store",{})
  has_recipe_crop=any(int(store.get(k,0) or 0)>0 for k in ("radish","lettuce","carrot","broad_bean"))
  if not has_recipe_crop:return "acquire_ingredients"
  if loc!="ashcroft_cottage":return "return_home"
  return "inspect_cooking_availability"
 if target=="community":
  if any(a.get("id","").startswith("lifesim:community:") or a.get("id")=="lifesim:share_meal" for a in actions):return "participate"
  return "reach_community_surface"
 if target=="procedural_content":
  if any(a.get("id","").startswith("arc:help:") for a in actions):return "engage_arc"
  arcs=s.get("procedural_arcs",{}).get("active",[])
  if arcs:return "reach_arc_location"
  return "await_or_trigger_opportunity"
 if target in {"npc_interaction","relationships","society"}:
  if any(a.get("id","").startswith(("social:greet:","society:greet:")) for a in actions):return "social_contact"
  return "find_people"
 if target=="gardening":
  if any(a.get("id","").startswith("garden:") for a in actions):return "garden_action"
  return "return_home" if loc!="ashcroft_cottage" else "inspect_garden"
 return "pursue"

def _stage_score(a,target,stage):
 text=_action_text(a); aid=a.get("id",""); score=0
 rules={
  "perform_cooking":(("cook","preserve","meal"),-120),
  "acquire_ingredients":(("radish bunch","radish","produce","village shop","shop"),-110),
  "return_home":(("ashcroft cottage","ashcroft_cottage"),-110),
  "inspect_cooking_availability":(("kitchen","cook","meal","pantry"),-100),
  "participate":(("community","workday","care walk","upkeep","share a simple meal"),-120),
  "reach_community_surface":(("village green","churchyard","riverside"),-75),
  "engage_arc":(("offer to help","arc:help"),-130),
  "reach_arc_location":(("visit","walk","return","go to"),-55),
  "social_contact":(("exchange a few words","talk","speak"),-120),
  "find_people":(("visit","walk","green","shop","bakery"),-55),
  "garden_action":(("garden","soil","weed","water","plant","sow","harvest"),-120),
  "inspect_garden":(("inspect the garden","garden"),-100),
 }
 words,weight=rules.get(stage,((),0))
 if any(w in text for w in words):score+=weight
 # Strongly suppress semantically adjacent but goal-irrelevant domestic/passive actions.
 if target in {"cooking","community","procedural_content"} and any(x in text for x in PASSIVE):score+=35
 if target=="cooking" and any(x in text for x in ("laundry","tidy","air the rooms","sketch","bird","garden beds","sow ")):score+=45
 return score

def project_actions(game,actions,target,recent,blocked,limit=12):
 stage=_goal_stage(game,target,actions)
 ranked=sorted(actions,key=lambda a:(_score(a,target,recent,blocked)+_stage_score(a,target,stage),a.get("id","")))
 # Keep a compact relevant surface plus a few escape/navigation alternatives.
 return ranked[:limit],stage

def _score(a,target,recent,blocked):
 aid=a.get('id','');text=(aid+' '+a.get('kind','')+' '+a.get('label','')).lower();score=recent.count(aid)*14+(100 if aid in blocked else 0)
 if any(p in text for p in PASSIVE):score+=8
 for w in GOAL_WORDS.get(target,()):
  if w in text:score-=20
 if target=='gardening':
  if 'ashcroft_cottage' in text:score-=30
  if any(x in text for x in ('plant','water','weed','harvest','soil')):score-=50
 if target in {'npc_interaction','relationships'} and (aid.startswith('social:greet:') or any(x in text for x in ('talk','speak','offer to help','exchange a few words'))):score-=80
 if target=='procedural_content' and any(x in text for x in ('offer to help','opportunity','errand')):score-=60
 if target=='cooking':
  if any(x in text for x in ('radish bunch','radish','produce','cook','preserve','recipe')):score-=70
  if 'ashcroft_cottage' in text:score-=35
 if target=='community' and any(x in text for x in ('village green','churchyard','riverside','community','workday','care walk','upkeep','share a simple meal')):score-=45
 if target=='society' and ('society:greet:' in aid or 'exchange a few words' in text):score-=80
 return score

def _direct_progress_action(actions,target,recent,blocked):
 ranked=sorted(actions,key=lambda a:(_score(a,target,recent,blocked),a.get('id','')))
 if ranked and _score(ranked[0],target,recent,blocked)<=-25:return ranked[0]
 return None

def plan_goal(game,memory,guidance=None):
 candidates=[{"id":"social","label":"Build a relationship through ordinary contact"},{"id":"livelihood","label":"Earn money or make practical work progress"},{"id":"home_garden","label":"Care for cottage, garden, food or supplies"},{"id":"explore","label":"Explore less-visited ordinary village places"},{"id":"community","label":"Take part in a visible event, errand or opportunity"},{"id":"investigate","label":"Follow a player-visible lead"}]
 state=_compact_state(game,memory,guidance);return provider.ask_compact_choice('autoplayer_planner',guidance or 'balanced ordinary life',state,candidates,timeout_override=75) or candidates[0]

QA_ROLES=("human_player","completionist","chaos_player")
PLAYER_ARCHETYPES=("social_anchor","cottage_isolation","practical_grinder","cautious_investigator","story_avoider")

def _player_archetype(action_count):
 # Long blocks give Town Mind and Chorus enough behavioural evidence to revise models.
 return PLAYER_ARCHETYPES[(int(action_count)//30)%len(PLAYER_ARCHETYPES)]

ARCHETYPE_GUIDANCE={
 "social_anchor":"Prioritise relationships, conversation, helping residents and returning to trusted people after uncertainty.",
 "cottage_isolation":"Prefer home, gardening, cottage work and solitary routines; minimise social contact unless necessary.",
 "practical_grinder":"Prioritise money, jobs, production, property and efficient practical progress; avoid unnecessary investigation.",
 "cautious_investigator":"Follow evidence, compare records, investigate carefully and triangulate testimony without reckless horror-seeking.",
 "story_avoider":"Prefer ordinary life, work, hobbies and home improvement; avoid visible story, horror and investigation paths where legal alternatives exist.",
}


def _qa_role(action_count):
 # Rotate in long enough blocks to preserve intention while still exercising contrasting behaviour.
 return QA_ROLES[(int(action_count)//18)%len(QA_ROLES)]

def _chaos_action(actions,recent):
 # Deterministic adversarial policy: prefer repeats, costly/commitment-changing actions, then unusual legal actions.
 scored=[]
 for a in actions:
  t=_action_text(a); aid=a.get("id","")
  score=0
  if aid in recent: score-=35
  if any(w in t for w in ("buy","lease","leave job","sleep","repair","accept","help")): score-=25
  if any(w in t for w in ("look around","wait and observe")): score+=20
  scored.append((score,aid,a))
 return sorted(scored,key=lambda x:(x[0],x[1]))[0][2] if scored else None

def choose_action(game,purpose='ordinary life',memory=None,target=None,comprehensive=False,qa_role='completionist'):
 memory=memory or {};actions=safe_actions(game,True,comprehensive=comprehensive)
 if not actions:return None,None,0.0,{"outcome":"no_legal_action","provider_state":"none","goal_progress":False}
 recent=list(memory.get('recent_actions',[]))[-10:];blocked=set(memory.get('blocked_actions',[]));eligible=[a for a in actions if a.get('id') not in blocked] or actions
 projected,stage=project_actions(game,eligible,target,recent,blocked,12)
 if qa_role=='chaos_player':
  selected=_chaos_action(eligible,recent)
  return selected,{'id':selected.get('id') if selected else None},0.0,{'outcome':'chaos_policy','provider_state':'deterministic_adversary','goal_progress':False,'goal_stage':stage}
 direct=_direct_progress_action(projected,target,recent,blocked) if qa_role=='completionist' else None
 if direct:return direct,{"id":direct['id']},0.0,{"outcome":"planned_step","provider_state":"local_planner","goal_progress":True,"goal_stage":stage}
 ranked=projected
 candidates=[{"id":a['id'],"label":a.get('label',a['id'])} for a in ranked];t=time.time();role_prompt=(f'HUMAN CAMPAIGN: preserve a coherent intention, avoid pointless repetition. TEST TARGET={target or "ordinary life"}. {purpose}' if qa_role=='human_player' else f'TEST TARGET={target or "ordinary life"}. {purpose}');choice=provider.ask_compact_choice('autoplayer',role_prompt,_compact_state(game,memory,target),candidates);dt=time.time()-t
 cid=choice.get('id') if isinstance(choice,dict) else None;selected=next((a for a in ranked if a['id']==cid),None)
 if selected:return selected,choice,dt,{"outcome":"llm_success","provider_state":provider.last_status.get('state','unknown'),"goal_progress":(_score(selected,target,recent,blocked)+_stage_score(selected,target,stage))<0,"goal_stage":stage}
 # Goal-aware fallback: choose best ranked action, not a rotating legal-action cycle.
 selected=ranked[0];state=str(provider.last_status.get('state','unknown'))
 if 'timeout' in state: provider.reset_session('autoplayer')
 return selected,choice,dt,{"outcome":"timeout_fallback" if 'timeout' in state else 'invalid_fallback',"provider_state":state,"goal_progress":_score(selected,target,recent,blocked)<0}

def _shadow_game(game,game_lock):
 """Snapshot authoritative state briefly; never hold the game lock during inference."""
 with game_lock:
  shadow=game.__class__.__new__(game.__class__);shadow.state=deepcopy(game.state);shadow._overview_cache_key=None;shadow._overview_cache=None
 return shadow

def _rss_mb(pid):
 try:
  with open(f"/proc/{pid}/status",encoding="utf-8") as f:
   for line in f:
    if line.startswith("VmRSS:"): return round(int(line.split()[1])/1024,1)
 except Exception:return None
 return None

def _ollama_rss_mb():
 try:
  out=subprocess.check_output(["ps","-C","ollama","-o","rss="],text=True,timeout=2)
  return round(sum(int(x.strip()) for x in out.splitlines() if x.strip())/1024,1)
 except Exception:return None

def _swap_used_mb():
 try:
  d={}
  for line in Path('/proc/meminfo').read_text().splitlines():
   k,v=line.split(':',1);d[k]=int(v.strip().split()[0])
  return round((d.get('SwapTotal',0)-d.get('SwapFree',0))/1024,1)
 except Exception:return None

class AIPlayerRunner:
 """Coverage-driven autonomous QA player.

 The runner uses the same public action grammar and Game.perform pathway as a human,
 but maintains a live evidence ledger, anomaly journal and resumable expository report.
 """
 COVERAGE_GOALS={
  "movement":"Explore locations and routes, including returning home.",
  "economy":"Earn and spend money; verify ledger and balance changes.",
  "food_survival":"Acquire and consume food; exercise hunger, energy, warmth and health changes.",
  "jobs":"Find work, perform shifts and exercise employment transitions.",
  "gardening":"Exercise soil, planting, watering, tending, growth and harvest pathways.",
  "cooking":"Acquire ingredients and cook, preserve or eat prepared food.",
  "fishing_foraging":"Fish, forage and verify inventory/collection consequences.",
  "cottage":"Inspect condition and exercise staged maintenance/repair pathways.",
  "relationships":"Interact with core and background residents and observe relationship consequences.",
  "community_society":"Participate in community and society actions and observe persistent social state.",
  "procedural_content":"Discover, accept/progress and resolve grounded procedural opportunities.",
  "quests_story":"Exercise visible quest/story actions and verify lifecycle progression without report spoilers.",
  "investigation":"Follow visible leads and verify investigation state changes.",
  "weather_ecology":"Advance enough time to observe weather/ecology response and contradictions.",
  "horror_failure_recovery":"Exercise eligible horror, danger, failure and recovery surfaces when naturally reachable.",
  "save_reload":"Periodically serialize and restore state, then continue play.",
  "action_contract":"Continuously verify legal actions execute or fail with explicit evidence rather than silent no-effect.",
 }
 def __init__(self):
  self.report_dir=Path(__file__).resolve().parents[2]/"diagnostics"; self.report_dir.mkdir(exist_ok=True)
  self.checkpoint_path=self.report_dir/"diagnostic_ai_player_live.jsonl"; self.report_path=self.report_dir/"diagnostic_ai_player_report.txt"; self.live_report_path=self.report_dir/"diagnostic_ai_player_live_report.txt"
  self.lock=RLock();self.stop_event=Event();self._thread=None;self.status=self._blank_status()
 def _blank_status(self):
  return {"running":False,"stop_state":"stopped","mode":"idle","progress":0,"phase":"Idle","feed":[],"actions":0,"llm_calls":0,"successful_decisions":0,"timeouts":0,"fallbacks":0,"planner_calls":0,"goal":None,"thinking":False,"error":None,"goal_stalls":0,"stop_requested_at":None,"stop_latency_s":None,"discarded_after_stop":0,"coverage":{},"anomalies":[],"unique_actions":0,"unique_locations":0,"save_reload_checks":0,"days_completed":0,"day_summaries":[],"action_counts":{},"semantic_findings":[],"fallback_reasons":{},"memory_samples":[],"target_mismatches":0,"repetition_warnings":0,"backpressure_waits":0,"plan_history":[],"qa_role":"completionist","role_action_counts":{},"role_findings":{},"story_critic_reviews":0,"irritation_findings":[],"village_observer_samples":[],"village_observer_findings":[],"observer_reviews":0,"player_archetype":"social_anchor","archetype_action_counts":{},"adaptation_snapshots":[],"adaptation_findings":[],"adaptation_reviews":0,"action_evidence":[]}
 def snapshot(self):
  with self.lock:return deepcopy(self.status)
 def _update(self,**kw):
  with self.lock:self.status.update(kw)
 def _feed(self,text):
  with self.lock:self.status.setdefault('feed',[]).append(text);self.status['feed']=self.status['feed'][-80:]
 def _village_observer_sample(self, game):
  s=game.state
  econ=s.get("economy",{}) or {}; businesses=econ.get("businesses",{}) or {}
  npcs=s.get("npcs",{}) or {}; events=s.get("world_events",[]) or []
  obligations=s.get("social_obligations",{}) or {}; facts=s.get("social_facts",{}) or {}
  projects=s.get("npc_epistemic_projects",{}) or {}; intentions=s.get("npc_intention_history",{}) or {}
  def n(x): return len(x) if hasattr(x,"__len__") else 0
  return {"ts":time.time(),"day":s.get("day"),"minute":s.get("minute"),"money":s.get("money"),"npc_count":n(npcs),"world_events":n(events),"businesses":n(businesses),"social_facts":n(facts),"obligations":n(obligations),"npc_projects":n(projects),"intention_histories":n(intentions),"history_len":n(s.get("history",[])),"presentation_entries":n((s.get("presentation_ledger",{}) or {}).get("entries",[])),"state_json_bytes":len(json.dumps(s,default=str))}
 def _village_observer_findings(self, samples):
  out=[]
  if len(samples)<3:return out
  a,b=samples[0],samples[-1]
  if b.get("day")==a.get("day") and len(samples)>=12: out.append({"severity":"warning","type":"observer_time_stall","detail":"Village observer collected many samples without advancing a simulated day."})
  for key in ("world_events","social_facts","obligations"):
   vals=[int(x.get(key,0) or 0) for x in samples[-20:]]
   if len(vals)>=10 and all(y>=x for x,y in zip(vals,vals[1:])) and vals[-1]>max(20,vals[0]*2): out.append({"severity":"warning","type":"observer_runaway_"+key,"detail":f"{key} grew monotonically from {vals[0]} to {vals[-1]} in the recent observer window."})
  sizes=[int(x.get("state_json_bytes",0) or 0) for x in samples[-20:]]
  if len(sizes)>=10 and sizes[0] and sizes[-1]>sizes[0]*1.75: out.append({"severity":"warning","type":"observer_state_growth","detail":f"Serialized state grew from {sizes[0]} to {sizes[-1]} bytes in the recent observer window."})
  return out
 def _adaptation_snapshot(self,game,archetype):
  s=game.state; obs=(s.get("interpretation_system",{}) or {}).get("observers",{}) or {}
  tm=s.get("town_mind",{}) or {}; pressure=s.get("town_pressure",{}) or {}
  def hyps(name):
   return [str(x.get("text") or x.get("hypothesis") or x)[:240] for x in (obs.get(name,{}) or {}).get("hypotheses",[])[-4:]]
  return {"ts":time.time(),"day":s.get("day"),"minute":s.get("minute"),"archetype":archetype,
   "town_hypotheses":hyps("town_mind"),"chorus_hypotheses":hyps("chorus"),
   "town_strategy":deepcopy((tm.get("strategy",{}) or {}).get("active_strategy")),
   "town_intentions":[str(x.get("id") if isinstance(x,dict) else x) for x in (tm.get("active_intentions",[]) or [])[-5:]],
   "pressure_strategy":deepcopy(pressure.get("strategy") or pressure.get("active_strategy")),
   "resistance":deepcopy(s.get("resistance",{}))}
 def _adaptation_findings(self,samples):
  out=[]
  groups={}
  for x in samples: groups.setdefault(x.get("archetype"),[]).append(x)
  if len(groups)<2:return out
  signatures={}
  for k,rows in groups.items():
   sig=set()
   for r in rows:
    sig.update(r.get("town_intentions",[]));
    if r.get("town_strategy"):sig.add("strategy:"+str(r.get("town_strategy")))
    if r.get("pressure_strategy"):sig.add("pressure:"+str(r.get("pressure_strategy")))
   signatures[k]=sig
  names=sorted(signatures)
  identical=[]
  for i,a in enumerate(names):
   for b in names[i+1:]:
    if signatures[a] and signatures[a]==signatures[b]: identical.append((a,b))
  if identical: out.append({"severity":"warning","type":"adaptation_signature_collision","detail":"Contrasting archetypes produced identical strategic signatures: "+str(identical[:5])})
  theory_counts={k:sum(len(r.get("town_hypotheses",[]))+len(r.get("chorus_hypotheses",[])) for r in rows) for k,rows in groups.items()}
  if len(groups)>=3 and sum(1 for v in theory_counts.values() if v==0)>=2: out.append({"severity":"warning","type":"adaptation_theory_inactivity","detail":"Multiple archetypes accumulated no Town/Chorus theory evidence: "+json.dumps(theory_counts)})
  return out
 def _state_digest(self,s):
  return {"day":s.get("day"),"minute":s.get("minute"),"location":s.get("location"),"money":s.get("money"),"inventory":deepcopy(s.get("inventory",[])),"player_status":deepcopy(s.get("player_status",{})),"relationships":deepcopy(s.get("relationships",{})),"quests":deepcopy(s.get("quest_runtime",{})),"arcs":deepcopy(s.get("procedural_arcs",{})),"garden":deepcopy(s.get("player_activities",{}).get("garden",{})),"employment":deepcopy(s.get("life_simulation",{}).get("employment",{})),"investigation":deepcopy(s.get("investigation",{})),"failure":deepcopy(s.get("failure_recovery",{})),"weather":deepcopy(s.get("weather",{})),"player_life":deepcopy(s.get("player_life",{})),"hobby_collections":deepcopy(s.get("player_activities",{}).get("hobbies",{}).get("collections",{})),"economy_ledger_len":len(s.get("economy",{}).get("ledger",[])),"history_len":len(s.get("history",[])),"world_events_len":len(s.get("world_events",[]))}
 def _diff(self,b,a):
  out=[]
  for k in b:
   if b[k]!=a.get(k):
    if k in {"inventory","relationships","quests","arcs","garden","employment","investigation","failure","player_status","weather","player_life","hobby_collections"}:out.append(k+" changed")
    else:out.append(f"{k}: {b[k]} -> {a.get(k)}")
  return out
 def _coverage_for_action(self,aid,label,diff):
  """Classify which domains an action actually touched; this is evidence, not certification."""
  t=(aid+' '+label).lower();hits=set()
  rules={"movement":("travel","walk","visit","return"),"economy":("buy","sell","shop","purchase","work","shift"),"food_survival":("eat","food","meal","bread","breakfast"),"jobs":("job","work","shift","employment","apply"),"gardening":("garden","soil","plant","sow","water","weed","harvest"),"cooking":("cook","preserve","recipe","meal"),"fishing_foraging":("fish","forag","bird","sketch","hobby"),"cottage":("cottage","repair","maint","inspect"),"relationships":("talk","greet","social","help"),"community_society":("community","society","resident","workday","churchyard"),"procedural_content":("arc:","errand","opportunity","favour","favor"),"quests_story":("quest","story:","choice"),"investigation":("investigat","lead","examine","observe"),"horror_failure_recovery":("horror:","danger","failure","recover","recurrence","ending:")}
  for goal,words in rules.items():
   if any(w in t for w in words):hits.add(goal)
  if diff:hits.add("action_contract")
  return hits
 def _certification_evidence(self,goal,aid,label,before,after,diff,ok):
  """Return (certified, reason). Certification requires domain-specific observable evidence."""
  if not ok:return False,"action failed"
  t=(aid+' '+label).lower(); changed=set(diff)
  if goal=="movement":return (before.get('location')!=after.get('location'),"location changed" if before.get('location')!=after.get('location') else "no location transition")
  if goal=="economy":return (before.get('money')!=after.get('money'),"money balance changed" if before.get('money')!=after.get('money') else "no money mutation")
  if goal=="food_survival":
   bp=before.get('player_status') or {};ap=after.get('player_status') or {}; inv=before.get('inventory')!=after.get('inventory')
   ok2=any(bp.get(k)!=ap.get(k) for k in ('hunger','energy','health','warmth')) and any(w in t for w in ('eat','food','meal','bread','breakfast'))
   return ok2,("survival stat changed through food action" if ok2 else "needs food action plus survival-stat mutation")
  if goal=="jobs":
   ok2=before.get('employment')!=after.get('employment') or (before.get('money')!=after.get('money') and any(w in t for w in ('job','work','shift')))
   return ok2,("employment or wage consequence observed" if ok2 else "needs employment transition or wage consequence")
  if goal=="gardening":return (before.get('garden')!=after.get('garden'),"garden state changed" if before.get('garden')!=after.get('garden') else "no garden-state mutation")
  if goal=="cooking":
   ok2=any(w in t for w in ('cook','preserve','recipe')) and (before.get('garden')!=after.get('garden') or before.get('player_life')!=after.get('player_life') or before.get('player_status')!=after.get('player_status'))
   return ok2,("cooking action consumed ingredients or changed meal/life state" if ok2 else "needs actual cook/preserve action with ingredient/product/life consequence")
  if goal=="fishing_foraging":
   ok2=any(w in t for w in ('fish','forag')) and (before.get('inventory')!=after.get('inventory') or before.get('hobby_collections')!=after.get('hobby_collections'))
   return ok2,("fishing inventory or foraging collection state changed" if ok2 else "needs fishing inventory or foraging collection consequence; probabilistic fishing may require bounded retries")
  if goal=="cottage":
   bc=(before.get('player_status') or {}).get('cottage');ac=(after.get('player_status') or {}).get('cottage');ok2=bc!=ac
   return ok2,("cottage state changed" if ok2 else "needs cottage condition/repair-stage mutation")
  if goal=="relationships":return (before.get('relationships')!=after.get('relationships'),"relationship state changed" if before.get('relationships')!=after.get('relationships') else "needs persistent relationship mutation")
  if goal=="community_society":
   ok2=any(w in t for w in ('community','society','resident','workday','churchyard')) and bool(diff)
   return ok2,("community/society action produced persistent change" if ok2 else "needs relevant social action with persistent consequence")
  if goal=="procedural_content":return (before.get('arcs')!=after.get('arcs'),"procedural arc state changed" if before.get('arcs')!=after.get('arcs') else "needs arc discovery/progression/resolution mutation")
  if goal=="quests_story":return (before.get('quests')!=after.get('quests'),"quest lifecycle state changed" if before.get('quests')!=after.get('quests') else "needs visible quest/story action with lifecycle mutation")
  if goal=="investigation":return (before.get('investigation')!=after.get('investigation'),"investigation state changed" if before.get('investigation')!=after.get('investigation') else "needs lead/evidence progression mutation")
  if goal=="weather_ecology":
   ok2=before.get('weather')!=after.get('weather') or after.get('day')!=before.get('day')
   return ok2,("weather/day progression observed" if ok2 else "needs environmental progression")
  if goal=="horror_failure_recovery":return (before.get('failure')!=after.get('failure'),"failure/recovery state changed" if before.get('failure')!=after.get('failure') else "needs eligible danger/failure/recovery state transition")
  if goal=="action_contract":return (bool(diff),"successful action produced monitored authoritative delta" if diff else "successful action had no monitored authoritative delta")
  return False,"no certification contract"
 def _coverage_reason(self,key,v):
  if v.get('status')=='certified':return v.get('last_evidence') or 'domain contract satisfied'
  if v.get('status')=='deferred':return v.get('last_gap') or 'effort budget exhausted; revisit after state changes'
  if v.get('attempts',0)==0:return 'not attempted yet'
  if v.get('acted',0)==0:return f"{v.get('attempts',0)} planning attempts; no semantically relevant domain action executed"
  return f"{v.get('attempts',0)} planning attempts, {v.get('acted',0)} relevant actions, but certification contract not met; last gap: {v.get('last_gap','unknown')}"
 def _semantic_findings(self, game, seen_texts):
  """Inspect newly presented text for player-visible quality failures without judging story truth."""
  out=[]
  ledger=game.state.get('presentation_ledger',{}).get('entries',[])
  for row in ledger[-80:]:
   eid=str(row.get('entry_id') or row.get('id') or '')
   if eid and eid in seen_texts: continue
   if eid: seen_texts.add(eid)
   text=str(row.get('text') or '').strip(); low=text.lower()
   if not text: continue
   if any(x in low for x in ('metadata on its own line','system prompt','assistant:','json schema','do not reveal')):
    out.append({"severity":"error","type":"player_visible_ai_boilerplate","detail":text[:240]})
   if len(text)>700:
    out.append({"severity":"warning","type":"overlong_player_text","detail":f"{len(text)} characters: {text[:180]}"})
   if text.count('{')>=2 and text.count('}')>=2:
    out.append({"severity":"warning","type":"raw_structured_text_visible","detail":text[:240]})
  return out


 def _story_critic_review(self, game, recent_events):
  """Use the LLM for semantic UX judgement; deterministic detectors remain authoritative for contracts."""
  if not recent_events:return []
  context="\n".join(f"{e.get('target')} | {e.get('label')} | {', '.join(e.get('diff',[])[:5])}" for e in recent_events[-10:])
  instruction=("Act as a strict game UX and narrative critic. Review this recent player-visible/action sequence. "
   "Identify only concrete irritation: confusing intent, tedious repetition, misleading labels, incoherent progression, "
   "poor feedback, dialogue/narration mismatch, or action consequence that would annoy a human player. "
   "Return up to 3 findings, one per line, exactly: SEVERITY|TYPE|DETAIL. SEVERITY is warning or error. "
   "If there is no concrete issue return NONE. Be concise and evidence-grounded.")
  try: raw=provider.ask_text('qa_story_critic',instruction,context,max_tokens=180) or ''
  except Exception as exc:return [{"severity":"warning","type":"story_critic_failure","action":"qa_story_critic","detail":str(exc)[:180]}]
  out=[]
  for line in str(raw).splitlines():
   line=line.strip().lstrip('- ').strip()
   if not line or line.upper()=='NONE':continue
   parts=line.split('|',2)
   if len(parts)!=3:continue
   sev,typ,detail=(x.strip() for x in parts)
   sev=sev.lower() if sev.lower() in {'warning','error'} else 'warning'
   out.append({"severity":sev,"type":"story_critic_"+typ.lower().replace(' ','_')[:50],"action":"qa_story_critic","detail":detail[:500]})
  return out[:3]

 def _detect_anomalies(self,b,a,aid,ok,diff,error=None):
  found=[]
  if not ok:found.append({"severity":"error","type":"action_exception","action":aid,"detail":error or "unknown exception"})
  informational={"investigate:review"}
  if ok and not diff and aid not in informational:found.append({"severity":"warning","type":"silent_no_effect","action":aid,"detail":"Action returned successfully but monitored authoritative state did not change."})
  wb=b.get('weather') or {};wa=a.get('weather') or {};temp=wa.get('temperature_c');prec=str(wa.get('condition') or wa.get('precipitation') or '').lower()
  if isinstance(temp,(int,float)) and temp<=0 and 'rain' in prec:found.append({"severity":"warning","type":"weather_consistency","action":aid,"detail":f"Rain-like condition at {temp} C; inspect precipitation rules."})
  if isinstance(a.get('money'),(int,float)) and a['money']<0:found.append({"severity":"error","type":"negative_money","action":aid,"detail":f"Money became {a['money']}"})
  ps=a.get('player_status') or {}
  for stat in ('health','hunger','energy','warmth'):
   v=ps.get(stat)
   if isinstance(v,(int,float)) and not 0<=v<=100:found.append({"severity":"error","type":"status_bounds","action":aid,"detail":f"{stat} out of bounds: {v}"})
  return found
 def _memory_sample(self,game):
  raw=len(json.dumps(game.state,separators=(",",":"),default=str).encode("utf-8"))/(1024*1024)
  ai=ASYNC_AI_RUNTIME.status()
  return {"ts":round(time.time(),2),"actions":self.snapshot().get("actions",0),"day":game.state.get("day"),"minute":game.state.get("minute"),"game_rss_mb":_rss_mb(os.getpid()),"ollama_rss_mb":_ollama_rss_mb(),"swap_used_mb":_swap_used_mb(),"state_json_mb":round(raw,3),"ai_queued":ai.get("queued",0),"ai_running":ai.get("running",0),"ai_completed_waiting":ai.get("completed_waiting",0)}
 def _wait_for_backpressure(self,game):
  waited=0
  while not self.stop_event.is_set():
   ai=ASYNC_AI_RUNTIME.status(); pressure=int(ai.get('queued',0) or 0)+int(ai.get('completed_waiting',0) or 0)
   if pressure<=2:break
   if ai.get('completed_waiting'): game.harvest_async_ai_results()
   time.sleep(0.5);waited+=1
   if waited>=120:break
  if waited:self._update(backpressure_waits=self.snapshot().get('backpressure_waits',0)+1)
 def _target_action_mismatch(self,target,aid,label,meta):
  if meta.get('goal_progress'):return False
  hits=self._coverage_for_action(aid,label,[])
  return target not in hits and target not in {'weather_ecology','save_reload','action_contract'}

 def _checkpoint(self,game,event,coverage,anomalies,visited,unique_actions):
  s=game.state;sample=self._memory_sample(game);samples=self.snapshot().get("memory_samples",[])+[sample];self._update(memory_samples=samples[-240:]);row={"ts":time.time(),"event":event,"memory":sample,"state":self._state_digest(s),"coverage":coverage,"anomaly_count":len(anomalies),"visited_locations":sorted(visited),"unique_actions":len(unique_actions),"provider":provider.telemetry()}
  with self.checkpoint_path.open("a",encoding="utf-8") as f:f.write(json.dumps(row,default=str)+"\n")
  self._write_live_report(game,coverage,anomalies,visited,unique_actions,event)
 def _unified_findings(self,coverage,anomalies):
  snap=self.snapshot(); findings=[]
  for x in anomalies:
   findings.append({"severity":x.get("severity","warning"),"type":x.get("type","anomaly"),"detail":x.get("detail",""),"action":x.get("action"),"source":"detector"})
  for x in snap.get("irritation_findings",[]):
   findings.append({"severity":x.get("severity","warning"),"type":x.get("type","player_irritation"),"detail":x.get("detail",str(x)),"action":x.get("action"),"source":"story_critic"})
  for k,v in coverage.items():
   if v.get("status") != "certified" and v.get("attempts",0)>=6:
    findings.append({"severity":"error" if v.get("status")=="deferred" else "warning","type":"coverage_reachability_gap","detail":f"{k}: {self._coverage_reason(k,v)}","action":None,"source":"coverage"})
  rank={"fatal":0,"error":1,"warning":2,"info":3}
  dedup=[];seen=set()
  for x in sorted(findings,key=lambda z:rank.get(z.get("severity"),2)):
   key=(x.get("type"),x.get("detail"))
   if key not in seen: seen.add(key);dedup.append(x)
  return dedup
 def _root_cause_groups(self,findings):
  groups={"reachability_and_progression":[],"semantic_and_ui_friction":[],"ai_runtime_and_planning":[],"simulation_and_state_growth":[],"adaptation_and_emergence":[],"other":[]}
  for x in findings:
   t=(x.get("type") or "").lower(); d=(x.get("detail") or "").lower()
   if any(w in t+d for w in ("coverage","reachability","quest","prerequisite","progress")): g="reachability_and_progression"
   elif any(w in t+d for w in ("irrit","semantic","repeat","label","dialog","narrat","ui","confus")): g="semantic_and_ui_friction"
   elif any(w in t+d for w in ("fallback","timeout","queue","planner","target_action","llm")): g="ai_runtime_and_planning"
   elif any(w in t+d for w in ("memory","rss","swap","growth","stall","observer","state")): g="simulation_and_state_growth"
   elif any(w in t+d for w in ("adaptation","archetype","theory","chorus","town")): g="adaptation_and_emergence"
   else:g="other"
   groups[g].append(x)
  return groups
 def _release_assessment(self,findings,coverage):
  sev={k:sum(1 for x in findings if x.get("severity")==k) for k in ("fatal","error","warning")}
  gaps=sum(1 for v in coverage.values() if v.get("status")!='certified')
  if sev["fatal"] or sev["error"]>=2:return "NOT READY"
  if sev["error"] or sev["warning"]>=5 or gaps>=4:return "NEEDS CORRECTION"
  if sev["warning"] or gaps:return "CONDITIONALLY READY"
  return "NO BLOCKING SIGNAL DETECTED"
 def _reproduction_lines(self,findings):
  evidence=self.snapshot().get("action_evidence",[]); out=[]
  for i,f in enumerate(findings[:12],1):
   aid=f.get("action"); candidates=[e for e in evidence if not aid or e.get("action")==aid]
   trace=candidates[-3:] if candidates else evidence[-3:]
   out.append(f"{i}. [{f.get('severity','warning').upper()}] {f.get('type')} — {f.get('detail')}")
   for e in trace: out.append("   TRACE: "+json.dumps({k:e.get(k) for k in ('day','minute','role','archetype','target','action','label','ok','diff')},default=str))
  return out
 def _report_lines(self,game,coverage,anomalies,visited,unique_actions,outcome,event=None):
  s=game.state;snap=self.snapshot();version=(Path(__file__).resolve().parents[2]/"VERSION").read_text().strip();done=sum(1 for v in coverage.values() if v.get('status')=='certified');total=len(coverage)
  severity={"fatal":0,"error":0,"warning":0}
  for x in anomalies: severity[x.get("severity","warning")]=severity.get(x.get("severity","warning"),0)+1
  findings=self._unified_findings(coverage,anomalies); groups=self._root_cause_groups(findings); assessment=self._release_assessment(findings,coverage)
  lines=["BELLWETHER AUTONOMOUS QA LABORATORY — UNIFIED MORNING REPORT",f"Version: {version}",f"Outcome: {outcome}","",f"RELEASE ASSESSMENT: {assessment}",f"- Prioritized findings: {len(findings)}",f"- Fatal: {sum(1 for x in findings if x.get('severity')=='fatal')} | Errors: {sum(1 for x in findings if x.get('severity')=='error')} | Warnings: {sum(1 for x in findings if x.get('severity')=='warning')}","", "EXECUTIVE SUMMARY",f"- Simulated days completed: {snap.get('days_completed',0)} / {snap.get('days',7)}",f"- Coverage: {done}/{total} gameplay domains certified",f"- Actions executed: {snap.get('actions',0)} across {len(unique_actions)} unique actions",f"- World traversal: {len(visited)} unique locations",f"- LLM decisions: {snap.get('successful_decisions',0)} successful / {snap.get('llm_calls',0)} calls; {snap.get('timeouts',0)} timeouts; {snap.get('fallbacks',0)} fallbacks",f"- Findings: {severity.get('fatal',0)} fatal, {severity.get('error',0)} errors, {severity.get('warning',0)} warnings",f"- Save/reload checks: {snap.get('save_reload_checks',0)}",f"- Final clock: Day {s.get('day')} minute {s.get('minute')} at {s.get('location')}",""]
  lines += ["DEVELOPER PRIORITIES"]
  if severity.get('fatal',0) or severity.get('error',0): lines.append("- HIGH: inspect fatal/error findings before adding features.")
  gaps=[k for k,v in coverage.items() if v.get('status')!='certified']
  if gaps: lines.append("- COVERAGE GAPS: "+", ".join(gaps))
  if snap.get('timeouts',0): lines.append(f"- AI RUNTIME: {snap.get('timeouts',0)} timeout(s) observed; compare queue wait and inference latency.")
  if not (severity.get('fatal',0) or severity.get('error',0) or gaps or snap.get('timeouts',0)): lines.append("- No release-blocking signal detected by the autonomous campaign; review warnings and semantic notes below.")
  lines += ["", "TOP PRIORITIZED FINDINGS"]
  if findings:
   for i,x in enumerate(findings[:20],1): lines.append(f"{i}. [{x.get('severity','warning').upper()}] {x.get('type')} | {x.get('detail')} | source={x.get('source')}")
  else: lines.append("- No prioritized finding generated.")
  lines += ["", "LIKELY ROOT-CAUSE GROUPS"]
  for name,items in groups.items():
   if items: lines.append(f"- {name}: {len(items)} finding(s) — "+", ".join(sorted(set(str(x.get('type')) for x in items))[:8]))
  lines += ["", "REPRODUCTION EVIDENCE"] + self._reproduction_lines(findings)
  lines += ["", "CROSS-AGENT / ARCHETYPE COMPARISON", "- QA role actions: "+json.dumps(snap.get('role_action_counts',{}),default=str), "- QA role findings: "+json.dumps(snap.get('role_findings',{}),default=str), "- Archetype actions: "+json.dumps(snap.get('archetype_action_counts',{}),default=str)]
  lines += ["", "TEST DIRECTOR ROLE SUMMARY", "- Active role: "+str(snap.get("qa_role")), "- Role action counts: "+json.dumps(snap.get("role_action_counts",{}),default=str), "- Role findings: "+json.dumps(snap.get("role_findings",{}),default=str), "", "MULTI-ARCHETYPE ADAPTATION TESTING", "- Active player archetype: "+str(snap.get("player_archetype")), "- Archetype action counts: "+json.dumps(snap.get("archetype_action_counts",{}),default=str), f"- Adaptation snapshots: {len(snap.get('adaptation_snapshots',[]))}", f"- Adaptation reviews: {snap.get('adaptation_reviews',0)}", *["- "+json.dumps(x,default=str) for x in snap.get("adaptation_findings",[])[-20:]], "", "STORY CRITIC / PLAYER IRRITATION",f"- LLM critic reviews: {snap.get('story_critic_reviews',0)}",f"- Irritation findings retained: {len(snap.get('irritation_findings',[]))}",*["- "+json.dumps(x,default=str) for x in snap.get('irritation_findings',[])[-20:]],"", "VILLAGE OBSERVER / SOAK ANALYSIS",f"- Observer samples: {len(snap.get('village_observer_samples',[]))}",f"- Observer reviews: {snap.get('observer_reviews',0)}",f"- Observer findings: {len(snap.get('village_observer_findings',[]))}",*["- "+json.dumps(x,default=str) for x in snap.get('village_observer_findings',[])[-20:]],"", "AUTONOMOUS QA DIAGNOSTICS",f"- Semantic target/action mismatches: {snap.get('target_mismatches',0)}",f"- Repetition warnings: {snap.get('repetition_warnings',0)}",f"- Backpressure waits: {snap.get('backpressure_waits',0)}","- Fallback reasons: "+json.dumps(snap.get("fallback_reasons",{}),default=str),"", "MEMORY / QUEUE SAMPLES"]
  for m in snap.get("memory_samples",[])[-30:]: lines.append("- "+json.dumps(m,default=str))
  lines += ["", "DAY-BY-DAY CAMPAIGN SUMMARY"]
  for row in snap.get('day_summaries',[]): lines.append(f"- Day {row.get('day')}: {row.get('actions',0)} actions; goals={', '.join(row.get('goals',[])) or 'none'}; locations={', '.join(row.get('locations',[])) or 'none'}; new findings={row.get('findings',0)}")
  if not snap.get('day_summaries'): lines.append("- No completed day summary yet; use the live checkpoint sections below.")
  lines += ["", "ACTION DIVERSITY"]
  for aid,count in sorted((snap.get('action_counts') or {}).items(),key=lambda x:(-x[1],x[0]))[:40]: lines.append(f"- {aid}: {count}")
  if event:lines += ["LATEST ACTION EVIDENCE",json.dumps(event,indent=2,default=str),""]
  lines += ["COVERAGE LEDGER"]
  for k,v in coverage.items():lines.append(f"- {k}: {v.get('status')} | planning_attempts={v.get('attempts',0)} | relevant_actions={v.get('acted',0)} | certifications={v.get('successes',0)} | deferrals={v.get('deferrals',0)} | WHY: {self._coverage_reason(k,v)} | CONTRACT: {v.get('note','')}")
  lines += ["","ISSUE / ANOMALY JOURNAL"]
  if anomalies:
   for i,x in enumerate(anomalies[-100:],1):lines.append(f"{i}. [{x.get('severity','warning').upper()}] {x.get('type')} | action={x.get('action')} | {x.get('detail')}")
  else:lines.append("- No anomalies recorded by current detectors.")
  lines += ["","VISITED LOCATIONS",*['- '+str(x) for x in sorted(visited)],"","RECENT LIVE TRACE",*['- '+x for x in snap.get('feed',[])],"","PROVIDER TELEMETRY",json.dumps(provider.telemetry(),indent=2,default=str)]
  return lines
 def _write_live_report(self,game,coverage,anomalies,visited,unique_actions,event=None):
  text='\n'.join(self._report_lines(game,coverage,anomalies,visited,unique_actions,'RUNNING / INTERRUPT-SAFE CHECKPOINT',event));tmp=self.live_report_path.with_suffix('.tmp');tmp.write_text(text,encoding='utf-8');tmp.replace(self.live_report_path);self._update(report=text)
 def _write_report(self,game,coverage,anomalies,visited,unique_actions,stopped=False):
  text='\n'.join(self._report_lines(game,coverage,anomalies,visited,unique_actions,'STOPPED' if stopped else 'COMPLETED'));self.report_path.write_text(text,encoding='utf-8');self.live_report_path.write_text(text,encoding='utf-8');self._update(report=text)
 def start_live(self,game,game_lock,days=14,mutate_live=False):
  with self.lock:
   if self.status.get('running'):return False
   self.stop_event.clear();self.checkpoint_path.write_text('',encoding='utf-8');self.status=self._blank_status();self.status.update(running=True,stop_state='running',mode='live_village_play' if mutate_live else 'isolated_overnight_qa',phase='Building coverage ledger',days=days,mutates_player_state=bool(mutate_live))
  if mutate_live:
   # Intentional autonomous-play mode: operate on the authoritative game object and lock.
   # This preserves the long-standing 'Let AI Play the Village' functionality and all
   # consequences are real player-campaign consequences.
   test_game=game;test_lock=game_lock
  else:
   # Diagnostic overnight campaign: isolated clone, safe for stress testing without consuming the save.
   test_game=game.__class__.__new__(game.__class__)
   with game_lock: test_game.state=deepcopy(game.state)
   test_game._overview_cache_key=None;test_game._overview_cache=None
   test_lock=RLock()
  thread_name='bellwether-live-village-ai-player' if mutate_live else 'bellwether-diagnostic-ai-player'
  self._thread=Thread(target=self._live,args=(test_game,test_lock,days),daemon=True,name=thread_name);self._thread.start();return True
 def stop(self):
  with self.lock:
   if self.status.get('running'):self.status.update(stop_state='stopping',phase='Stop requested; current inference result will be discarded',stop_requested_at=time.time())
  self.stop_event.set();return True
 def _live(self,game,game_lock,days):
  memory={"recent_actions":deque(maxlen=20),"recent_locations":deque(maxlen=20),"failed_attempts":deque(maxlen=20),"completed_subtasks":deque(maxlen=30),"blocked_actions":set()}
  seen_texts=set();recent_critic_events=[]; day_stats={}; coverage={k:{"status":"untested","attempts":0,"acted":0,"successes":0,"deferrals":0,"last_gap":"","last_evidence":"","note":v} for k,v in self.COVERAGE_GOALS.items()};anomalies=[];visited={game.state.get('location')};unique_actions=set();goal_cursor=0
  try:
   start=game.state.get('day',1);last_day=start;goal=None;goal_key=None;goal_actions=0;stalls=0
   self._write_live_report(game,coverage,anomalies,visited,unique_actions)
   while game.state.get('day',1)<start+days and not self.stop_event.is_set():
    # Periodic real serialization round trip on authoritative state, then continue.
    if self.snapshot()['actions'] and self.snapshot()['actions']%20==0 and coverage['save_reload']['attempts']<max(2,days//2):
     with game_lock:
      before=deepcopy(game.state);blob=json.dumps(before,default=str);restored=json.loads(blob);ok=(restored.get('day')==before.get('day') and restored.get('location')==before.get('location') and restored.get('money')==before.get('money'))
     coverage['save_reload']['attempts']+=1;coverage['save_reload']['successes']+=int(ok);coverage['save_reload']['status']='certified' if ok else 'failed';coverage['save_reload']['acted']+=1;coverage['save_reload']['last_evidence']='JSON round trip preserved clock, location and money' if ok else '';coverage['save_reload']['last_gap']='round-trip mismatch' if not ok else '';self._update(save_reload_checks=self.snapshot().get('save_reload_checks',0)+1)
     if not ok:anomalies.append({"severity":"error","type":"save_reload_roundtrip","action":"save_reload","detail":"Core clock/location/money changed across JSON round trip."})
    current_day=game.state.get('day',1)
    if current_day!=last_day:
     ds=day_stats.get(last_day,{"actions":0,"goals":set(),"locations":set(),"findings":0})
     summaries=self.snapshot().get('day_summaries',[])+[{"day":last_day,"actions":ds['actions'],"goals":sorted(ds['goals']),"locations":sorted(x for x in ds['locations'] if x),"findings":ds['findings']}]
     self._update(day_summaries=summaries[-14:],days_completed=max(0,current_day-start));last_day=current_day
    # Passive environment certification: weather/ecology is observed through ordinary time progression.
    if coverage['weather_ecology']['status']!='certified':
     coverage['weather_ecology']['attempts']+=1
     env_ok,env_reason=self._certification_evidence('weather_ecology','passive:environment','Passive environment observation',self._state_digest(game.state),self._state_digest(game.state),[],True)
     # Day/weather changes are checked per action below; this heartbeat records observation effort only.
     coverage['weather_ecology']['last_gap']=env_reason
    missing=[k for k,v in coverage.items() if v['status'] not in {'certified','deferred'} and k not in {'save_reload','weather_ecology'}]
    if goal is None or goal_actions>=10 or stalls>=4:
     goal_key=missing[goal_cursor%len(missing)] if missing else list(self.COVERAGE_GOALS)[goal_cursor%len(self.COVERAGE_GOALS)];goal_cursor+=1;goal=self.COVERAGE_GOALS[goal_key];goal_actions=0;stalls=0;memory['blocked_actions'].clear();self._update(goal=goal_key,planner_calls=self.snapshot()['planner_calls']+1);self._feed(f"Coverage target · {goal_key} · {goal}")
    self._update(thinking=True,phase=f'Choosing legal action for {goal_key}')
    role=_qa_role(self.snapshot().get('actions',0)); archetype=_player_archetype(self.snapshot().get('actions',0)); self._update(qa_role=role,player_archetype=archetype,phase=f'{role}/{archetype}: choosing legal action for {goal_key}');shadow=_shadow_game(game,game_lock);action,raw,dt,meta=choose_action(shadow,goal+' ARCHETYPE: '+ARCHETYPE_GUIDANCE[archetype],memory,target=goal_key,comprehensive=True,qa_role=role)
    snap=self.snapshot();llm_used=(meta['outcome']=='llm_success' or 'fallback' in meta['outcome']);reasons=dict(snap.get('fallback_reasons',{}));reason=(meta.get('provider_state') or provider.last_status.get('last_error') or 'unknown');reasons[reason]=reasons.get(reason,0)+int('fallback' in meta['outcome']);self._update(thinking=False,llm_calls=snap['llm_calls']+int(llm_used),successful_decisions=snap['successful_decisions']+int(meta['outcome']=='llm_success'),timeouts=snap['timeouts']+int('timeout' in meta['outcome']),fallbacks=snap['fallbacks']+int('fallback' in meta['outcome']),fallback_reasons=reasons)
    if self.stop_event.is_set():self._update(discarded_after_stop=self.snapshot().get('discarded_after_stop',0)+1);break
    if not action:
     anomalies.append({"severity":"error","type":"no_legal_action","action":None,"detail":f"No legal public action while pursuing {goal_key}."});break
    aid=action['id'];label=action.get('label',aid);coverage[goal_key]['attempts']+=1;unique_actions.add(aid)
    if self._target_action_mismatch(goal_key,aid,label,meta):
     anomalies.append({'severity':'warning','type':'semantic_target_action_mismatch','action':aid,'detail':f'Target {goal_key} selected unrelated action: {label}'});self._update(target_mismatches=self.snapshot().get('target_mismatches',0)+1)
    if list(memory['recent_actions'])[-3:].count(aid)>=3:
     anomalies.append({'severity':'warning','type':'repetitive_interaction','action':aid,'detail':f'Action repeated at least four times in a short window: {label}'});self._update(repetition_warnings=self.snapshot().get('repetition_warnings',0)+1)
    self._wait_for_backpressure(game)
    with game_lock:
     before=self._state_digest(game.state);err=None
     try:game.perform(aid);ok=True
     except Exception as exc:ok=False;err=f"{type(exc).__name__}: {exc}"
     after=self._state_digest(game.state)
    diff=self._diff(before,after);found=self._detect_anomalies(before,after,aid,ok,diff,err);semantic=self._semantic_findings(game,seen_texts);found.extend(semantic);anomalies.extend(found);visited.add(after.get('location'));hits=self._coverage_for_action(aid,label,diff)
    ds=day_stats.setdefault(after.get('day'),{"actions":0,"goals":set(),"locations":set(),"findings":0});ds['actions']+=1;ds['goals'].add(goal_key);ds['locations'].add(after.get('location'));ds['findings']+=len(found)
    counts=self.snapshot().get('action_counts',{});counts=dict(counts);counts[aid]=counts.get(aid,0)+1;self._update(action_counts=counts,semantic_findings=deepcopy([x for x in anomalies if x.get('type') in {'player_visible_ai_boilerplate','overlong_player_text','raw_structured_text_visible'}][-40:]))
    env_ok,env_reason=self._certification_evidence('weather_ecology',aid,label,before,after,diff,ok)
    if env_ok:
     coverage['weather_ecology']['acted']+=1;coverage['weather_ecology']['successes']+=1;coverage['weather_ecology']['status']='certified';coverage['weather_ecology']['last_evidence']=env_reason;coverage['weather_ecology']['last_gap']=''
    # Attempted, acted and certified are deliberately separate concepts.
    for h in hits:
     if h!=goal_key:coverage[h]['attempts']+=1
     coverage[h]['acted']+=1
     certified,reason=self._certification_evidence(h,aid,label,before,after,diff,ok)
     if certified:
      coverage[h]['successes']+=1;coverage[h]['status']='certified';coverage[h]['last_evidence']=reason;coverage[h]['last_gap']=''
     else:coverage[h]['last_gap']=reason
    certified,reason=self._certification_evidence(goal_key,aid,label,before,after,diff,ok)
    if goal_key not in hits and bool(meta.get('goal_progress')):coverage[goal_key]['last_gap']=f"planner considered action progress, but domain contract says: {reason}"
    elif not certified:coverage[goal_key]['last_gap']=reason
    if certified:
     if goal_key not in hits:coverage[goal_key]['acted']+=1
     coverage[goal_key]['successes']+=1;coverage[goal_key]['status']='certified';coverage[goal_key]['last_evidence']=reason;coverage[goal_key]['last_gap']='';stalls=0
    else:stalls+=1
    if ok and diff:memory['recent_actions'].append(aid);memory['recent_locations'].append(after.get('location'))
    else:memory['blocked_actions'].add(aid);memory['failed_attempts'].append(f"{aid}: {err or 'no_effect'}")
    goal_actions+=1
    if coverage[goal_key]['status']!='certified' and coverage[goal_key]['attempts']>=18:
     coverage[goal_key]['status']='deferred';coverage[goal_key]['deferrals']+=1;coverage[goal_key]['last_gap']=f"effort budget exhausted after {coverage[goal_key]['attempts']} attempts; campaign reallocated to other domains";goal=None
    n=self.snapshot()['actions']+1;rc=dict(self.snapshot().get('role_action_counts',{}));rc[role]=rc.get(role,0)+1;rf=dict(self.snapshot().get('role_findings',{}));rf[role]=rf.get(role,0)+len(found);ac=dict(self.snapshot().get('archetype_action_counts',{}));ac[archetype]=ac.get(archetype,0)+1;self._update(role_action_counts=rc,role_findings=rf,archetype_action_counts=ac);done=sum(1 for v in coverage.values() if v['status']=='certified');pct=min(99,int(100*done/max(1,len(coverage))));event={"day":game.state.get("day"),"minute":game.state.get("minute"),"role":role,"archetype":archetype,"action":aid,"label":label,"target":goal_key,"outcome":meta.get('outcome'),"latency_s":round(dt,2),"ok":ok,"diff":diff,"new_anomalies":found}
    ae=self.snapshot().get("action_evidence",[])+[event];self._update(action_evidence=ae[-500:])
    recent_critic_events.append(event);recent_critic_events=recent_critic_events[-20:]
    if n%8==0:
     critic=self._story_critic_review(game,recent_critic_events);anomalies.extend(critic);ir=self.snapshot().get('irritation_findings',[])+critic;self._update(story_critic_reviews=self.snapshot().get('story_critic_reviews',0)+1,irritation_findings=ir[-80:])
    self._update(actions=n,progress=pct,phase=f"Executed {label}",coverage=deepcopy(coverage),anomalies=deepcopy(anomalies[-100:]),unique_actions=len(unique_actions),unique_locations=len(visited),goal_stalls=stalls)
    self._feed(f"Day {game.state.get('day')} {game.time_label()} · {goal_key} · {label} · {'changed: '+', '.join(diff) if diff else 'NO MONITORED EFFECT'}")
    self._checkpoint(game,event,coverage,anomalies,visited,unique_actions)
    if n%12==0:
     ads=self.snapshot().get("adaptation_snapshots",[])+[self._adaptation_snapshot(game,archetype)];ads=ads[-240:]
     af=self._adaptation_findings(ads);self._update(adaptation_snapshots=ads,adaptation_findings=af[-80:],adaptation_reviews=self.snapshot().get("adaptation_reviews",0)+1)
     if af:
      known={(x.get('type'),x.get('detail')) for x in anomalies}; anomalies.extend([x for x in af if (x.get('type'),x.get('detail')) not in known])
    if n%4==0:
     obs=self.snapshot().get("village_observer_samples",[])+[self._village_observer_sample(game)]; obs=obs[-360:]
     of=self._village_observer_findings(obs); existing=self.snapshot().get("village_observer_findings",[])
     known={(x.get("type"),x.get("detail")) for x in existing}; fresh=[x for x in of if (x.get("type"),x.get("detail")) not in known]
     if fresh: anomalies.extend(fresh)
     self._update(village_observer_samples=obs,village_observer_findings=(existing+fresh)[-100:],observer_reviews=self.snapshot().get("observer_reviews",0)+1)
   ds=day_stats.get(game.state.get('day'),{"actions":0,"goals":set(),"locations":set(),"findings":0}); summaries=self.snapshot().get('day_summaries',[])
   if ds['actions'] and not any(x.get('day')==game.state.get('day') for x in summaries): summaries=summaries+[{"day":game.state.get('day'),"actions":ds['actions'],"goals":sorted(ds['goals']),"locations":sorted(x for x in ds['locations'] if x),"findings":ds['findings']}]
   stopped=self.stop_event.is_set();snap=self.snapshot();lat=(time.time()-snap['stop_requested_at']) if stopped and snap.get('stop_requested_at') else None;self._update(running=False,thinking=False,stop_state='stopped',stop_latency_s=round(lat,3) if lat is not None else None,progress=self.snapshot()['progress'] if stopped else 100,phase='Diagnostic AI player stopped' if stopped else 'Diagnostic AI player finished',day_summaries=summaries[-14:],days_completed=max(0,game.state.get('day',start)-start));self._write_report(game,coverage,anomalies,visited,unique_actions,stopped)
  except Exception as e:
   anomalies.append({"severity":"fatal","type":"runner_exception","action":None,"detail":f"{type(e).__name__}: {e}"});self._update(running=False,thinking=False,stop_state='stopped',error=f'{type(e).__name__}: {e}',phase='Diagnostic AI player failed',anomalies=deepcopy(anomalies[-100:]));self._write_report(game,coverage,anomalies,visited,unique_actions,True)
AI_PLAYER=AIPlayerRunner()
