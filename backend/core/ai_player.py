"""v1.1.0 goal-directed autonomous player with compact inference protocol."""
from copy import deepcopy
from threading import RLock,Thread,Event
from collections import deque
import time
from backend.ai.provider import provider
BLOCKED_PREFIXES=("story:","ending:","horror:","recurrence:")
BLOCKED_KINDS={"story","choice","talk"}
GOAL_WORDS={"movement":("travel","walk","visit","return","go to"),"npc_interaction":("talk","speak","help","conversation"),"relationships":("talk","speak","help","conversation"),"economy":("buy","sell","shop","purchase","support"),"jobs":("job","work","shift","apply"),"gardening":("garden","soil","weed","water","plant","sow","harvest","cottage"),"investigation":("observe","examine","review","lead","investigat"),"procedural_content":("offer to help","errand","opportunity","favour","favor")}
PASSIVE=("look around","take a moment","wait and observe","sit by","review what","observe carefully","watch for birds","make a sketch","research local history","go foraging")

def safe_actions(game,allow_investigation=True):
 out=[]
 for a in game.actions():
  aid=a.get("id","");kind=a.get("kind","")
  if aid.startswith(BLOCKED_PREFIXES) or kind in BLOCKED_KINDS:continue
  if not allow_investigation and (aid.startswith("investigate:") or kind=="investigate"):continue
  if kind=="free_talk":continue
  out.append(a)
 return out

def _compact_state(game,memory,target):
 s=game.state;recent=','.join(list(memory.get('recent_actions',[]))[-5:]);blocked=','.join(list(memory.get('blocked_actions',[]))[:5]);garden=s.get('player_activities',{}).get('garden',{});seeds=sum(garden.get('seed_stock',{}).values()) if isinstance(garden,dict) else 0
 return f"D{s.get('day')} T{s.get('minute')} AT={s.get('location')} M={s.get('money')} TARGET={target or '-'} SEEDS={seeds} RECENT={recent or '-'} BLOCKED={blocked or '-'}"

def _score(a,target,recent,blocked):
 aid=a.get('id','');text=(aid+' '+a.get('kind','')+' '+a.get('label','')).lower();score=recent.count(aid)*14+(100 if aid in blocked else 0)
 if any(p in text for p in PASSIVE):score+=8
 for w in GOAL_WORDS.get(target,()):
  if w in text:score-=20
 if target=='gardening':
  if 'ashcroft_cottage' in text:score-=30
  if any(x in text for x in ('plant','water','weed','harvest','soil')):score-=50
 if target in {'npc_interaction','relationships'} and any(x in text for x in ('talk','speak','offer to help')):score-=60
 if target=='procedural_content' and any(x in text for x in ('offer to help','opportunity','errand')):score-=60
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
 direct=_direct_progress_action(eligible,target,recent,blocked)
 if direct:return direct,{"id":direct['id']},0.0,{"outcome":"planned_step","provider_state":"local_planner","goal_progress":True}
 ranked=sorted(eligible,key=lambda a:(_score(a,target,recent,blocked),a.get('id','')))[:18]
 candidates=[{"id":a['id'],"label":a.get('label',a['id'])} for a in ranked];t=time.time();choice=provider.ask_compact_choice('autoplayer',target or purpose,_compact_state(game,memory,target),candidates);dt=time.time()-t
 cid=choice.get('id') if isinstance(choice,dict) else None;selected=next((a for a in ranked if a['id']==cid),None)
 if selected:return selected,choice,dt,{"outcome":"llm_success","provider_state":provider.last_status.get('state','unknown'),"goal_progress":_score(selected,target,recent,blocked)<0}
 # Goal-aware fallback: choose best ranked action, not a rotating legal-action cycle.
 selected=ranked[0];state=str(provider.last_status.get('state','unknown'));return selected,choice,dt,{"outcome":"timeout_fallback" if 'timeout' in state else 'invalid_fallback',"provider_state":state,"goal_progress":_score(selected,target,recent,blocked)<0}

class AIPlayerRunner:
 def __init__(self):self.lock=RLock();self.stop_event=Event();self._thread=None;self.status={"running":False,"stop_state":"stopped","mode":"idle","progress":0,"phase":"Idle","feed":[],"actions":0,"llm_calls":0,"successful_decisions":0,"timeouts":0,"fallbacks":0,"planner_calls":0,"goal":None,"thinking":False,"error":None,"goal_stalls":0}
 def snapshot(self):
  with self.lock:return deepcopy(self.status)
 def _update(self,**kw):
  with self.lock:self.status.update(kw)
 def _feed(self,text):
  with self.lock:self.status.setdefault('feed',[]).append(text);self.status['feed']=self.status['feed'][-40:]
 def start_live(self,game,game_lock,days=7):
  with self.lock:
   if self.status.get('running'):return False
   self.stop_event.clear();self.status={"running":True,"stop_state":"running","mode":"live","progress":0,"phase":"Planning ordinary life","feed":[],"actions":0,"llm_calls":0,"successful_decisions":0,"timeouts":0,"fallbacks":0,"planner_calls":0,"goal":None,"thinking":False,"error":None,"days":days,"goal_stalls":0}
  self._thread=Thread(target=self._live,args=(game,game_lock,days),daemon=True,name='bellwether-ai-player');self._thread.start();return True
 def stop(self):
  with self.lock:
   if self.status.get('running'):self.status.update(stop_state='stopping',phase='Stop requested; completed inference will be discarded')
  self.stop_event.set();return True
 def _live(self,game,game_lock,days):
  memory={"recent_actions":deque(maxlen=12),"recent_locations":deque(maxlen=10),"failed_attempts":deque(maxlen=8),"completed_subtasks":deque(maxlen=10),"blocked_actions":set()}
  try:
   start=game.state.get('day',1);goal=None;goal_actions=0;stalls=0
   while game.state.get('day',1)<start+days and not self.stop_event.is_set():
    if goal is None or goal_actions>=8 or stalls>=4:
     self._update(thinking=True,phase='Planner is choosing an intention')
     with game_lock:planned=plan_goal(game,memory)
     snap=self.snapshot();self._update(thinking=False,planner_calls=snap['planner_calls']+1,llm_calls=snap['llm_calls']+1);goal=planned.get('label',planned.get('id','ordinary life'));goal_actions=0;stalls=0;memory['blocked_actions'].clear();self._update(goal=goal);self._feed('Plan · '+goal)
    self._update(thinking=True,phase='AI player is choosing a legal action')
    with game_lock:action,raw,dt,meta=choose_action(game,goal,memory)
    snap=self.snapshot();self._update(thinking=False,llm_calls=snap['llm_calls']+(meta['outcome']=='llm_success' or 'fallback' in meta['outcome']),successful_decisions=snap['successful_decisions']+(meta['outcome']=='llm_success'),timeouts=snap['timeouts']+('timeout' in meta['outcome']),fallbacks=snap['fallbacks']+('fallback' in meta['outcome']))
    if self.stop_event.is_set():self._feed(f'Stop requested · discarded completed choice after {dt:.1f}s');break
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
    n=self.snapshot()['actions']+(1 if ok else 0);pct=min(99,int(100*(game.state.get('day',1)-start)/max(1,days)));self._update(actions=n,progress=pct,phase=f"AI player: {action.get('label',action['id'])}")
   stopped=self.stop_event.is_set();self._update(running=False,thinking=False,stop_state='stopped',progress=self.snapshot()['progress'] if stopped else 100,phase='AI player stopped' if stopped else 'AI player finished')
  except Exception as e:self._update(running=False,thinking=False,stop_state='stopped',error=f'{type(e).__name__}: {e}',phase='AI player failed')
AI_PLAYER=AIPlayerRunner()
