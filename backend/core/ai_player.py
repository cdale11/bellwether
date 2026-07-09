"""v1.0.12 hierarchical autonomous player and diagnostic action policy.
Only legal public actions are selected. Authored story/endings/horror remain blocked in
leisure autoplay. Diagnostic callers can inspect timeout/fallback/outcome metadata.
"""
from copy import deepcopy
from threading import RLock, Thread, Event
from collections import deque, Counter
import time
from backend.ai.provider import provider

BLOCKED_PREFIXES=("story:","ending:","horror:","recurrence:")
BLOCKED_KINDS={"story","choice","talk"}
GOAL_WORDS={
 "movement":("travel","walk","visit","return","go to"),
 "npc_interaction":("talk","speak","help","visit"),
 "economy":("buy","sell","shop","purchase","grocer"),
 "jobs":("job","work","shift","apply"),
 "gardening":("garden","soil","weed","water","plant","sow","harvest","cottage"),
 "investigation":("observe","examine","review","lead","investigat"),
 "procedural_content":("offer to help","errand","opportunity","favour","favor"),
}

def safe_actions(game, allow_investigation=True):
    out=[]
    for a in game.actions():
        aid=a.get("id",""); kind=a.get("kind","")
        if aid.startswith(BLOCKED_PREFIXES) or kind in BLOCKED_KINDS: continue
        if not allow_investigation and (aid.startswith("investigate:") or kind=="investigate"): continue
        if kind=="free_talk": continue
        out.append(a)
    return out

def _public_context(game,memory,purpose):
    s=game.state
    return {"day":s.get("day"),"time":game.time_label(),"location":s.get("location"),"money":s.get("money"),"weather":s.get("weather"),"purpose":purpose,
      "recent_actions":list(memory.get("recent_actions",[]))[-8:],"recent_locations":list(memory.get("recent_locations",[]))[-6:],
      "failed_attempts":list(memory.get("failed_attempts",[]))[-8:],"completed_subtasks":list(memory.get("completed_subtasks",[]))[-6:],
      "recent_events":[e.get("text","") for e in s.get("world_events",[])[-4:]],"garden":s.get("player_activities",{}).get("garden",{}),
      "employment":s.get("employment",{}),"visible_opportunities":s.get("procedural_arcs",{}).get("active",[])[:3]}

def plan_goal(game,memory,guidance=None):
    candidates=[{"id":"social","label":"Build or maintain a relationship through ordinary village contact"},{"id":"livelihood","label":"Earn money or make practical progress in work"},{"id":"home_garden","label":"Care for the cottage, garden, food, or supplies"},{"id":"explore","label":"Explore familiar and less-visited parts of ordinary village life"},{"id":"community","label":"Take part in a hobby, event, errand, or community opportunity"},{"id":"investigate","label":"Follow a player-visible lead without hidden knowledge"}]
    choice=provider.ask_choice("autoplayer_planner","Choose one current intention for the next several meaningful actions. Base it only on player-visible state and avoid repeating a recently completed intention.",_public_context(game,memory,guidance or "Choose a balanced ordinary-life intention"),candidates)
    return choice or candidates[0]

def _goal_rank(action,target,recent,blocked):
    aid=action.get("id",""); text=(aid+" "+action.get("kind","")+" "+action.get("label","")).lower()
    score=recent.count(aid)*8 + (100 if aid in blocked else 0)
    if target:
        words=GOAL_WORDS.get(target,())
        if any(w in text for w in words): score-=12
        # Gardening is a prerequisite chain: first reach home, then use garden actions.
        if target=="gardening" and "ashcroft_cottage" in text: score-=18
    return (score,aid)

def choose_action(game,purpose="relaxed autonomous village life",memory=None,target=None):
    memory=memory or {}; actions=safe_actions(game,allow_investigation=True)
    if not actions:return None,None,0.0,{"outcome":"no_legal_action","provider_state":"none"}
    recent=list(memory.get("recent_actions",[]))[-8:]; blocked=set(memory.get("blocked_actions",[]))
    ranked=sorted(actions,key=lambda a:_goal_rank(a,target,recent,blocked))
    eligible=[a for a in ranked if a.get("id") not in blocked] or ranked
    candidates=[{"id":a["id"],"label":a.get("label",a["id"])} for a in eligible[:32]]
    t=time.time(); choice=provider.ask_choice("autoplayer","Choose one legal action that advances the current intention while remaining natural. Prefer meaningful progress and variety. Never repeat an action that just failed or changed nothing.",_public_context(game,memory,purpose),candidates);dt=time.time()-t
    pstate=str(getattr(provider,"last_status",{}).get("state","unknown")); cid=choice.get("id") if isinstance(choice,dict) else None
    selected=next((a for a in eligible if a["id"]==cid),None)
    if selected:return selected,choice,dt,{"outcome":"llm_success","provider_state":pstate}
    # A fallback is explicit and inspectable, never disguised as an LLM decision.
    return eligible[0],choice,dt,{"outcome":"timeout_fallback" if "timeout" in pstate else "invalid_fallback","provider_state":pstate}

class AIPlayerRunner:
    def __init__(self):
        self.lock=RLock();self.stop_event=Event();self._thread=None
        self.status={"running":False,"stop_state":"stopped","mode":"idle","progress":0,"phase":"Idle","feed":[],"actions":0,"llm_calls":0,"successful_decisions":0,"timeouts":0,"fallbacks":0,"planner_calls":0,"goal":None,"thinking":False,"error":None}
    def snapshot(self):
        with self.lock:return deepcopy(self.status)
    def _update(self,**kw):
        with self.lock:self.status.update(kw)
    def _feed(self,text):
        with self.lock:self.status.setdefault("feed",[]).append(text);self.status["feed"]=self.status["feed"][-40:]
    def start_live(self,game,game_lock,days=7):
        with self.lock:
            if self.status.get("running"):return False
            self.stop_event.clear();self.status={"running":True,"stop_state":"running","mode":"live","progress":0,"phase":"Planning ordinary life","feed":[],"actions":0,"llm_calls":0,"successful_decisions":0,"timeouts":0,"fallbacks":0,"planner_calls":0,"goal":None,"thinking":False,"error":None,"days":days}
        self._thread=Thread(target=self._live,args=(game,game_lock,days),daemon=True,name="bellwether-ai-player");self._thread.start();return True
    def stop(self):
        with self.lock:
            if self.status.get("running"):self.status.update(stop_state="stopping",phase="Stop requested; current inference result will not be applied")
        self.stop_event.set();return True
    def _live(self,game,game_lock,days):
        memory={"recent_actions":deque(maxlen=12),"recent_locations":deque(maxlen=10),"failed_attempts":deque(maxlen=8),"completed_subtasks":deque(maxlen=10),"blocked_actions":set()}
        try:
            start_day=game.state.get("day",1);target_day=start_day+days;goal=None;goal_actions=0;planned_day=start_day
            while game.state.get("day",1)<target_day and not self.stop_event.is_set():
                if goal is None or goal_actions>=6 or game.state.get("day",1)>planned_day:
                    self._update(thinking=True,phase="Planner is choosing an intention")
                    with game_lock:planned=plan_goal(game,memory)
                    self._update(thinking=False,planner_calls=self.snapshot()["planner_calls"]+1,llm_calls=self.snapshot()["llm_calls"]+1)
                    if self.stop_event.is_set():break
                    goal=planned.get("label",planned.get("id","ordinary life"));goal_actions=0;planned_day=game.state.get("day",1);memory["blocked_actions"].clear();self._update(goal=goal);self._feed("Plan · "+goal)
                self._update(thinking=True,phase="AI player is choosing a legal action")
                with game_lock:action,raw,dt,meta=choose_action(game,goal,memory)
                snap=self.snapshot(); self._update(thinking=False,llm_calls=snap["llm_calls"]+1,successful_decisions=snap["successful_decisions"]+(meta["outcome"]=="llm_success"),timeouts=snap["timeouts"]+("timeout" in meta["outcome"]),fallbacks=snap["fallbacks"]+("fallback" in meta["outcome"]))
                if self.stop_event.is_set():self._feed(f"Stop requested · discarded completed choice after {dt:.1f}s");break
                if not action:break
                with game_lock:
                    before=(game.state.get("day"),game.state.get("minute"),game.state.get("location"),game.state.get("money"),len(game.state.get("history",[])))
                    try:game.perform(action["id"]);ok=True
                    except Exception as exc:ok=False;memory["failed_attempts"].append(f"{action['id']}: {type(exc).__name__}")
                    after=(game.state.get("day"),game.state.get("minute"),game.state.get("location"),game.state.get("money"),len(game.state.get("history",[])))
                changed=before!=after
                if ok and changed:memory["recent_actions"].append(action["id"]);memory["recent_locations"].append(after[2]);goal_actions+=1
                else:memory["blocked_actions"].add(action["id"]);memory["failed_attempts"].append(f"{action['id']}: no_effect" if ok else f"{action['id']}: failed")
                tag={"llm_success":"LLM","timeout_fallback":"timeout→fallback","invalid_fallback":"invalid→fallback"}.get(meta["outcome"],meta["outcome"])
                self._feed(f"Day {game.state.get('day')} {game.time_label()} · {action.get('label',action['id'])} · {tag} {dt:.1f}s"+(" · no effect" if not changed else ""))
                n=self.snapshot()["actions"]+(1 if ok else 0);pct=min(99,int(100*(game.state.get("day",1)-start_day)/max(1,days)));self._update(actions=n,progress=pct,phase=f"AI player: {action.get('label',action['id'])}")
            stopped=self.stop_event.is_set();self._update(running=False,thinking=False,stop_state="stopped",progress=self.snapshot()["progress"] if stopped else 100,phase="AI player stopped" if stopped else "AI player finished")
        except Exception as e:self._update(running=False,thinking=False,stop_state="stopped",error=f"{type(e).__name__}: {e}",phase="AI player failed")
AI_PLAYER=AIPlayerRunner()
