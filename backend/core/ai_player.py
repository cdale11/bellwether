"""v1.4.0 prerequisite-aware autonomous player with semantic candidate projection."""
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

def safe_actions(game,allow_investigation=True):
 out=[]
 for a in compact_action_surface(game.actions()):
  aid=a.get("id","");kind=a.get("kind","")
  if aid.startswith(BLOCKED_PREFIXES) or kind in BLOCKED_KINDS:continue
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
  if not has_food:return "acquire_ingredients"
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
  "acquire_ingredients":(("groceries","food","breakfast","loaf","shop"),-90),
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
  if any(x in text for x in ('basic groceries','food','cook','preserve','meal')):score-=55
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

def choose_action(game,purpose='ordinary life',memory=None,target=None):
 memory=memory or {};actions=safe_actions(game,True)
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
 def __init__(self):
  self.report_dir=Path(__file__).resolve().parents[2]/"diagnostics"; self.report_dir.mkdir(exist_ok=True)
  self.checkpoint_path=self.report_dir/"overnight_ai_player_live.jsonl"; self.report_path=self.report_dir/"overnight_ai_player_report.txt"
  self.lock=RLock();self.stop_event=Event();self._thread=None;self.status={"running":False,"stop_state":"stopped","mode":"idle","progress":0,"phase":"Idle","feed":[],"actions":0,"llm_calls":0,"successful_decisions":0,"timeouts":0,"fallbacks":0,"planner_calls":0,"goal":None,"thinking":False,"error":None,"goal_stalls":0,"stop_requested_at":None,"stop_latency_s":None,"discarded_after_stop":0}
 def snapshot(self):
  with self.lock:return deepcopy(self.status)
 def _update(self,**kw):
  with self.lock:self.status.update(kw)
 def _feed(self,text):
  with self.lock:self.status.setdefault('feed',[]).append(text);self.status['feed']=self.status['feed'][-40:]
 def _checkpoint(self,game,event):
  s=game.state; rt=s.get("ai_runtime",{}); bg=rt.get("background",{}); ps=s.get("player_status",{}); econ=s.get("economy",{}); row={"ts":time.time(),"event":event,"day":s.get("day"),"minute":s.get("minute"),"location":s.get("location"),"money":s.get("money"),"health":ps.get("health"),"hunger":ps.get("hunger"),"energy":ps.get("energy"),"warmth":ps.get("warmth"),"cottage_condition":ps.get("cottage",{}).get("condition"),"world_ticks":s.get("world_runtime",{}).get("ticks",0),"history":len(s.get("history",[])),"world_events":len(s.get("world_events",[])),"quests":s.get("quest_runtime",{}),"procedural_active":len(s.get("procedural_arcs",{}).get("active",[])),"procedural_history":len(s.get("procedural_arcs",{}).get("history",[])),"ai_runtime":rt,"provider":provider.telemetry()}
  with self.checkpoint_path.open("a",encoding="utf-8") as f:f.write(json.dumps(row,default=str)+"\n")
 def _write_report(self,game,stopped=False):
  s=game.state; snap=self.snapshot(); rt=s.get("ai_runtime",{}); ps=s.get("player_status",{}); wr=s.get("world_runtime",{}); eco=s.get("ecology_ai",{}); econ=s.get("economy",{}); q=s.get("quest_runtime",{}); version=(Path(__file__).resolve().parents[2]/"VERSION").read_text(encoding="utf-8").strip(); lines=["BELLWETHER OVERNIGHT HUMAN + AI SOAK REPORT",f"Version: {version}",f"Outcome: {'STOPPED' if stopped else 'COMPLETED'}",f"AI actions: {snap.get('actions',0)}",f"LLM calls: {snap.get('llm_calls',0)}",f"Successful decisions: {snap.get('successful_decisions',0)}",f"Timeouts: {snap.get('timeouts',0)}",f"Fallbacks: {snap.get('fallbacks',0)}",f"Stop latency: {snap.get('stop_latency_s')}","","WORLD HEALTH",f"Clock: day {s.get('day')} minute {s.get('minute')}",f"Location: {s.get('location')}",f"World ticks: {wr.get('ticks',0)}",f"World events retained: {len(s.get('world_events',[]))}",f"History entries: {len(s.get('history',[]))}","","PLAYER HEALTH",f"Health={ps.get('health')} Hunger={ps.get('hunger')} Energy={ps.get('energy')} Warmth={ps.get('warmth')}",f"Cottage={ps.get('cottage',{})}",f"Money={s.get('money')} Ledger entries={len(econ.get('ledger',[]))}","","AI RUNTIME",json.dumps(rt,indent=2,default=str),"","PROVIDER TELEMETRY",json.dumps(provider.telemetry(),indent=2,default=str),"","QUEST RUNTIME",json.dumps(q,indent=2,default=str),"","PROCEDURAL CONTENT",json.dumps(s.get('procedural_arcs',{}),indent=2,default=str),"","ECOLOGY AI",json.dumps(eco,indent=2,default=str),"","SOCIETY",json.dumps(s.get('society',{}),indent=2,default=str),"","RECENT AI FEED"]+['- '+x for x in snap.get('feed',[])]
  self.report_path.write_text("\n".join(lines),encoding="utf-8")
  self._update(report="\n".join(lines))
 def start_live(self,game,game_lock,days=7):
  with self.lock:
   if self.status.get('running'):return False
   self.stop_event.clear(); self.checkpoint_path.write_text("",encoding="utf-8");self.status={"running":True,"stop_state":"running","mode":"live","progress":0,"phase":"Planning ordinary life","feed":[],"actions":0,"llm_calls":0,"successful_decisions":0,"timeouts":0,"fallbacks":0,"planner_calls":0,"goal":None,"thinking":False,"error":None,"days":days,"goal_stalls":0,"stop_requested_at":None,"stop_latency_s":None,"discarded_after_stop":0}
  self._thread=Thread(target=self._live,args=(game,game_lock,days),daemon=True,name='bellwether-ai-player');self._thread.start();return True
 def stop(self):
  with self.lock:
   if self.status.get('running'):self.status.update(stop_state='stopping',phase='Stop requested; completed inference will be discarded',stop_requested_at=time.time())
  self.stop_event.set();return True
 def _live(self,game,game_lock,days):
  memory={"recent_actions":deque(maxlen=12),"recent_locations":deque(maxlen=10),"failed_attempts":deque(maxlen=8),"completed_subtasks":deque(maxlen=10),"blocked_actions":set()}
  try:
   start=game.state.get('day',1);goal=None;goal_actions=0;stalls=0
   while game.state.get('day',1)<start+days and not self.stop_event.is_set():
    if goal is None or goal_actions>=8 or stalls>=4:
     self._update(thinking=True,phase='Planner is choosing an intention')
     shadow=_shadow_game(game,game_lock);planned=plan_goal(shadow,memory)
     snap=self.snapshot();self._update(thinking=False,planner_calls=snap['planner_calls']+1,llm_calls=snap['llm_calls']+1);goal=planned.get('label',planned.get('id','ordinary life'));goal_actions=0;stalls=0;memory['blocked_actions'].clear();self._update(goal=goal);self._feed('Plan · '+goal)
    self._update(thinking=True,phase='AI player is choosing a legal action')
    shadow=_shadow_game(game,game_lock);action,raw,dt,meta=choose_action(shadow,goal,memory)
    snap=self.snapshot();self._update(thinking=False,llm_calls=snap['llm_calls']+(meta['outcome']=='llm_success' or 'fallback' in meta['outcome']),successful_decisions=snap['successful_decisions']+(meta['outcome']=='llm_success'),timeouts=snap['timeouts']+('timeout' in meta['outcome']),fallbacks=snap['fallbacks']+('fallback' in meta['outcome']))
    if self.stop_event.is_set():
     snap=self.snapshot();self._update(discarded_after_stop=snap.get('discarded_after_stop',0)+1);self._feed(f'Stop requested · discarded completed choice after {dt:.1f}s');break
    if not action:break
    with game_lock:
     before=(game.state.get('day'),game.state.get('minute'),game.state.get('location'),game.state.get('money'),len(game.state.get('history',[])))
     try:game.perform(action['id']);ok=True
     except Exception as exc:ok=False;memory['failed_attempts'].append(f"{action['id']}: {type(exc).__name__}")
     after=(game.state.get('day'),game.state.get('minute'),game.state.get('location'),game.state.get('money'),len(game.state.get('history',[])))
    changed=before!=after;progress=bool(meta.get('goal_progress')) and changed
    if ok and changed:memory['recent_actions'].append(action['id']);memory['recent_locations'].append(after[2]);goal_actions+=1
    else:memory['blocked_actions'].add(action['id']);memory['failed_attempts'].append(f"{action['id']}: no_effect")
    stalls=0 if progress else stalls+1;self._update(goal_stalls=stalls)
    tag=meta['outcome'];self._feed(f"Day {game.state.get('day')} {game.time_label()} · {action.get('label',action['id'])} · {tag} {dt:.1f}s"+(' · goal progress' if progress else ''))
    self._checkpoint(game,{"action":action.get("id"),"label":action.get("label"),"outcome":tag,"latency_s":round(dt,2),"changed":changed,"goal":goal})
    n=self.snapshot()['actions']+(1 if ok else 0);pct=min(99,int(100*(game.state.get('day',1)-start)/max(1,days)));self._update(actions=n,progress=pct,phase=f"AI player: {action.get('label',action['id'])}")
   stopped=self.stop_event.is_set();snap=self.snapshot();lat=(time.time()-snap['stop_requested_at']) if stopped and snap.get('stop_requested_at') else None;self._update(running=False,thinking=False,stop_state='stopped',stop_latency_s=round(lat,3) if lat is not None else None,progress=self.snapshot()['progress'] if stopped else 100,phase='AI player stopped' if stopped else 'AI player finished');self._write_report(game,stopped)
  except Exception as e:self._update(running=False,thinking=False,stop_state='stopped',error=f'{type(e).__name__}: {e}',phase='AI player failed')
AI_PLAYER=AIPlayerRunner()
