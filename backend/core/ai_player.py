"""Hierarchical autonomous player used for leisure autoplay and certification.
The planner chooses a bounded ordinary-life intention; the action player selects only
currently legal public actions. Stop is cooperative: in-flight inference may finish,
but its result is discarded and no post-stop action is applied.
"""
from copy import deepcopy
from threading import RLock, Thread, Event
from collections import deque, Counter
import time
from backend.ai.provider import provider

BLOCKED_PREFIXES=("story:","ending:","horror:","recurrence:")
BLOCKED_KINDS={"story","choice"}
PLANNER_DOMAINS={"autoplayer_planner"}

def safe_actions(game, allow_investigation=True):
    out=[]
    for a in game.actions():
        aid=a.get("id",""); kind=a.get("kind","")
        if aid.startswith(BLOCKED_PREFIXES) or kind in BLOCKED_KINDS: continue
        if not allow_investigation and (aid.startswith("investigate:") or kind=="investigate"): continue
        if kind=="free_talk": continue
        out.append(a)
    return out

def _public_context(game, memory, purpose):
    s=game.state
    return {"day":s.get("day"),"time":game.time_label(),"location":s.get("location"),"money":s.get("money"),
      "weather":s.get("weather"),"purpose":purpose,"recent_actions":list(memory.get("recent_actions",[]))[-8:],
      "recent_locations":list(memory.get("recent_locations",[]))[-6:],"recent_npcs":list(memory.get("recent_npcs",[]))[-6:],
      "failed_attempts":list(memory.get("failed_attempts",[]))[-4:],"completed_subtasks":list(memory.get("completed_subtasks",[]))[-6:],
      "recent_events":[e.get("text","") for e in s.get("world_events",[])[-4:]],
      "garden":s.get("player_activities",{}).get("garden",{}),"employment":s.get("employment",{}),
      "visible_opportunities":s.get("procedural_arcs",{}).get("active",[])[:3]}

def plan_goal(game, memory, guidance=None):
    candidates=[
      {"id":"social","label":"Build or maintain a relationship through ordinary village contact"},
      {"id":"livelihood","label":"Earn money or make practical progress in work"},
      {"id":"home_garden","label":"Care for the cottage, garden, food, or supplies"},
      {"id":"explore","label":"Explore familiar and less-visited parts of ordinary village life"},
      {"id":"community","label":"Take part in a hobby, event, errand, or community opportunity"},
      {"id":"investigate","label":"Follow a player-visible lead without hidden knowledge"},
    ]
    ctx=_public_context(game,memory,guidance or "Choose a balanced ordinary-life intention")
    choice=provider.ask_choice("autoplayer_planner","Choose one current intention for the next several meaningful actions. Base it only on player-visible state and avoid repeating a recently completed intention.",ctx,candidates)
    return choice or candidates[0]

def choose_action(game, purpose="relaxed autonomous village life", memory=None):
    memory=memory or {}
    actions=safe_actions(game,allow_investigation=True)
    if not actions:return None,None,0.0
    # Penalise immediate repetition without making the route scripted.
    recent=list(memory.get("recent_actions",[]))[-5:]
    ranked=sorted(actions,key=lambda a:(recent.count(a.get("id")), a.get("id","")))[:32]
    candidates=[{"id":a["id"],"label":a.get("label",a["id"])} for a in ranked]
    ctx=_public_context(game,memory,purpose)
    t=time.time(); choice=provider.ask_choice("autoplayer","Choose one legal action that advances the current intention while remaining natural. Prefer meaningful variety and do not bounce repeatedly between the same two actions or places.",ctx,candidates);dt=time.time()-t
    cid=choice.get("id") if isinstance(choice,dict) else None
    selected=next((a for a in actions if a["id"]==cid),ranked[0])
    return selected,choice,dt

class AIPlayerRunner:
    def __init__(self):
        self.lock=RLock(); self.stop_event=Event(); self._thread=None
        self.status={"running":False,"stop_state":"stopped","mode":"idle","progress":0,"phase":"Idle","feed":[],"actions":0,"llm_calls":0,"planner_calls":0,"goal":None,"thinking":False,"error":None}
    def snapshot(self):
        with self.lock:return deepcopy(self.status)
    def _update(self,**kw):
        with self.lock:self.status.update(kw)
    def _feed(self,text):
        with self.lock:self.status.setdefault("feed",[]).append(text);self.status["feed"]=self.status["feed"][-40:]
    def start_live(self,game,game_lock,days=7):
        with self.lock:
            if self.status.get("running"):return False
            self.stop_event.clear();self.status={"running":True,"stop_state":"running","mode":"live","progress":0,"phase":"Planning ordinary life","feed":[],"actions":0,"llm_calls":0,"planner_calls":0,"goal":None,"thinking":False,"error":None,"days":days}
        self._thread=Thread(target=self._live,args=(game,game_lock,days),daemon=True,name="bellwether-ai-player");self._thread.start();return True
    def stop(self):
        with self.lock:
            if self.status.get("running"):
                self.status["stop_state"]="stopping";self.status["phase"]="Stopping after current inference; result will be discarded"
        self.stop_event.set();return True
    def _live(self,game,game_lock,days):
        memory={"recent_actions":deque(maxlen=12),"recent_locations":deque(maxlen=10),"recent_npcs":deque(maxlen=10),"failed_attempts":deque(maxlen=8),"completed_subtasks":deque(maxlen=10)}
        try:
            start_day=game.state.get("day",1); target=start_day+days; goal=None; goal_actions=0; planned_day=start_day
            while game.state.get("day",1)<target and not self.stop_event.is_set():
                if goal is None or goal_actions>=6 or game.state.get("day",1)>planned_day:
                    self._update(thinking=True,phase="Planner is choosing an intention")
                    with game_lock: planned=plan_goal(game,memory)
                    self._update(thinking=False,planner_calls=self.snapshot()["planner_calls"]+1,llm_calls=self.snapshot()["llm_calls"]+1)
                    if self.stop_event.is_set(): break
                    goal=planned.get("label",planned.get("id","ordinary life"));goal_actions=0;planned_day=game.state.get("day",1);self._update(goal=goal);self._feed("Plan · "+goal)
                self._update(thinking=True,phase="AI player is choosing a legal action")
                with game_lock: action,raw,dt=choose_action(game,goal,memory)
                self._update(thinking=False,llm_calls=self.snapshot()["llm_calls"]+1)
                if self.stop_event.is_set():
                    self._feed(f"Stop requested · discarded completed choice after {dt:.1f}s");break
                if not action:break
                before_loc=game.state.get("location");self._feed(f"Day {game.state.get('day')} {game.time_label()} · {action.get('label',action['id'])} · thought {dt:.1f}s")
                with game_lock:
                    try: game.perform(action["id"]); ok=True
                    except Exception as exc: ok=False; memory["failed_attempts"].append(f"{action['id']}: {type(exc).__name__}")
                if ok:
                    memory["recent_actions"].append(action["id"]);memory["recent_locations"].append(game.state.get("location"));goal_actions+=1
                n=self.snapshot()["actions"]+(1 if ok else 0);pct=min(99,int(100*(game.state.get("day",1)-start_day)/max(1,days)))
                self._update(actions=n,progress=pct,phase=f"AI player: {action.get('label',action['id'])}")
            stopped=self.stop_event.is_set();self._update(running=False,thinking=False,stop_state="stopped",progress=self.snapshot()["progress"] if stopped else 100,phase="AI player stopped" if stopped else "AI player finished")
        except Exception as e:self._update(running=False,thinking=False,stop_state="stopped",error=f"{type(e).__name__}: {e}",phase="AI player failed")
AI_PLAYER=AIPlayerRunner()
