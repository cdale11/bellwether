"""v3.13.0 seven-day human-like autonomous playtester with interrupt-safe evidence reporting."""
from copy import deepcopy
from threading import RLock,Thread,Event
from collections import deque
import time
import json
from pathlib import Path
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

def choose_action(game,purpose='ordinary life',memory=None,target=None,comprehensive=False):
 memory=memory or {};actions=safe_actions(game,True,comprehensive=comprehensive)
 if not actions:return None,None,0.0,{"outcome":"no_legal_action","provider_state":"none","goal_progress":False}
 recent=list(memory.get('recent_actions',[]))[-10:];blocked=set(memory.get('blocked_actions',[]));eligible=[a for a in actions if a.get('id') not in blocked] or actions
 projected,stage=project_actions(game,eligible,target,recent,blocked,12)
 direct=_direct_progress_action(projected,target,recent,blocked)
 if direct:return direct,{"id":direct['id']},0.0,{"outcome":"planned_step","provider_state":"local_planner","goal_progress":True,"goal_stage":stage}
 ranked=projected
 candidates=[{"id":a['id'],"label":a.get('label',a['id'])} for a in ranked];t=time.time();choice=provider.ask_compact_choice('autoplayer',target or purpose,_compact_state(game,memory,target),candidates);dt=time.time()-t
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
  return {"running":False,"stop_state":"stopped","mode":"idle","progress":0,"phase":"Idle","feed":[],"actions":0,"llm_calls":0,"successful_decisions":0,"timeouts":0,"fallbacks":0,"planner_calls":0,"goal":None,"thinking":False,"error":None,"goal_stalls":0,"stop_requested_at":None,"stop_latency_s":None,"discarded_after_stop":0,"coverage":{},"anomalies":[],"unique_actions":0,"unique_locations":0,"save_reload_checks":0,"days_completed":0,"day_summaries":[],"action_counts":{},"semantic_findings":[]}
 def snapshot(self):
  with self.lock:return deepcopy(self.status)
 def _update(self,**kw):
  with self.lock:self.status.update(kw)
 def _feed(self,text):
  with self.lock:self.status.setdefault('feed',[]).append(text);self.status['feed']=self.status['feed'][-80:]
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
 def _checkpoint(self,game,event,coverage,anomalies,visited,unique_actions):
  s=game.state;row={"ts":time.time(),"event":event,"state":self._state_digest(s),"coverage":coverage,"anomaly_count":len(anomalies),"visited_locations":sorted(visited),"unique_actions":len(unique_actions),"provider":provider.telemetry()}
  with self.checkpoint_path.open("a",encoding="utf-8") as f:f.write(json.dumps(row,default=str)+"\n")
  self._write_live_report(game,coverage,anomalies,visited,unique_actions,event)
 def _report_lines(self,game,coverage,anomalies,visited,unique_actions,outcome,event=None):
  s=game.state;snap=self.snapshot();version=(Path(__file__).resolve().parents[2]/"VERSION").read_text().strip();done=sum(1 for v in coverage.values() if v.get('status')=='certified');total=len(coverage)
  severity={"fatal":0,"error":0,"warning":0}
  for x in anomalies: severity[x.get("severity","warning")]=severity.get(x.get("severity","warning"),0)+1
  lines=["BELLWETHER 7-DAY AI/LLM HUMAN-LIKE PLAYTEST REPORT",f"Version: {version}",f"Outcome: {outcome}","", "EXECUTIVE SUMMARY",f"- Simulated days completed: {snap.get('days_completed',0)} / {snap.get('days',7)}",f"- Coverage: {done}/{total} gameplay domains certified",f"- Actions executed: {snap.get('actions',0)} across {len(unique_actions)} unique actions",f"- World traversal: {len(visited)} unique locations",f"- LLM decisions: {snap.get('successful_decisions',0)} successful / {snap.get('llm_calls',0)} calls; {snap.get('timeouts',0)} timeouts; {snap.get('fallbacks',0)} fallbacks",f"- Findings: {severity.get('fatal',0)} fatal, {severity.get('error',0)} errors, {severity.get('warning',0)} warnings",f"- Save/reload checks: {snap.get('save_reload_checks',0)}",f"- Final clock: Day {s.get('day')} minute {s.get('minute')} at {s.get('location')}",""]
  lines += ["DEVELOPER PRIORITIES"]
  if severity.get('fatal',0) or severity.get('error',0): lines.append("- HIGH: inspect fatal/error findings before adding features.")
  gaps=[k for k,v in coverage.items() if v.get('status')!='certified']
  if gaps: lines.append("- COVERAGE GAPS: "+", ".join(gaps))
  if snap.get('timeouts',0): lines.append(f"- AI RUNTIME: {snap.get('timeouts',0)} timeout(s) observed; compare queue wait and inference latency.")
  if not (severity.get('fatal',0) or severity.get('error',0) or gaps or snap.get('timeouts',0)): lines.append("- No release-blocking signal detected by the autonomous campaign; review warnings and semantic notes below.")
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
  seen_texts=set(); day_stats={}; coverage={k:{"status":"untested","attempts":0,"acted":0,"successes":0,"deferrals":0,"last_gap":"","last_evidence":"","note":v} for k,v in self.COVERAGE_GOALS.items()};anomalies=[];visited={game.state.get('location')};unique_actions=set();goal_cursor=0
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
    shadow=_shadow_game(game,game_lock);action,raw,dt,meta=choose_action(shadow,goal,memory,target=goal_key,comprehensive=True)
    snap=self.snapshot();llm_used=(meta['outcome']=='llm_success' or 'fallback' in meta['outcome']);self._update(thinking=False,llm_calls=snap['llm_calls']+int(llm_used),successful_decisions=snap['successful_decisions']+int(meta['outcome']=='llm_success'),timeouts=snap['timeouts']+int('timeout' in meta['outcome']),fallbacks=snap['fallbacks']+int('fallback' in meta['outcome']))
    if self.stop_event.is_set():self._update(discarded_after_stop=self.snapshot().get('discarded_after_stop',0)+1);break
    if not action:
     anomalies.append({"severity":"error","type":"no_legal_action","action":None,"detail":f"No legal public action while pursuing {goal_key}."});break
    aid=action['id'];label=action.get('label',aid);coverage[goal_key]['attempts']+=1;unique_actions.add(aid)
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
    n=self.snapshot()['actions']+1;done=sum(1 for v in coverage.values() if v['status']=='certified');pct=min(99,int(100*done/max(1,len(coverage))));event={"action":aid,"label":label,"target":goal_key,"outcome":meta.get('outcome'),"latency_s":round(dt,2),"ok":ok,"diff":diff,"new_anomalies":found}
    self._update(actions=n,progress=pct,phase=f"Executed {label}",coverage=deepcopy(coverage),anomalies=deepcopy(anomalies[-100:]),unique_actions=len(unique_actions),unique_locations=len(visited),goal_stalls=stalls)
    self._feed(f"Day {game.state.get('day')} {game.time_label()} · {goal_key} · {label} · {'changed: '+', '.join(diff) if diff else 'NO MONITORED EFFECT'}")
    self._checkpoint(game,event,coverage,anomalies,visited,unique_actions)
   ds=day_stats.get(game.state.get('day'),{"actions":0,"goals":set(),"locations":set(),"findings":0}); summaries=self.snapshot().get('day_summaries',[])
   if ds['actions'] and not any(x.get('day')==game.state.get('day') for x in summaries): summaries=summaries+[{"day":game.state.get('day'),"actions":ds['actions'],"goals":sorted(ds['goals']),"locations":sorted(x for x in ds['locations'] if x),"findings":ds['findings']}]
   stopped=self.stop_event.is_set();snap=self.snapshot();lat=(time.time()-snap['stop_requested_at']) if stopped and snap.get('stop_requested_at') else None;self._update(running=False,thinking=False,stop_state='stopped',stop_latency_s=round(lat,3) if lat is not None else None,progress=self.snapshot()['progress'] if stopped else 100,phase='Diagnostic AI player stopped' if stopped else 'Diagnostic AI player finished',day_summaries=summaries[-14:],days_completed=max(0,game.state.get('day',start)-start));self._write_report(game,coverage,anomalies,visited,unique_actions,stopped)
  except Exception as e:
   anomalies.append({"severity":"fatal","type":"runner_exception","action":None,"detail":f"{type(e).__name__}: {e}"});self._update(running=False,thinking=False,stop_state='stopped',error=f'{type(e).__name__}: {e}',phase='Diagnostic AI player failed',anomalies=deepcopy(anomalies[-100:]));self._write_report(game,coverage,anomalies,visited,unique_actions,True)
AI_PLAYER=AIPlayerRunner()
