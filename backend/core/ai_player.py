"""LLM player for leisure autoplay and exhaustive disposable playtesting.
Only legal, currently visible, non-authored/non-story actions may be selected.
"""
from copy import deepcopy
from threading import RLock, Thread, Event
import time, traceback
from backend.ai.provider import provider

BLOCKED_PREFIXES=("story:","investigate:","ending:","horror:","recurrence:")
BLOCKED_KINDS={"story","choice","investigate"}

def safe_actions(game):
    out=[]
    for a in game.actions():
        aid=a.get("id",""); kind=a.get("kind","")
        if aid.startswith(BLOCKED_PREFIXES) or kind in BLOCKED_KINDS: continue
        # Free text dialogue is interactive and not safe for unattended autoplay.
        if kind=="free_talk": continue
        out.append(a)
    return out

def choose_action(game, purpose="relaxed autonomous village life"):
    actions=safe_actions(game)
    if not actions:return None,None,0.0
    candidates=[{"id":a["id"],"label":a.get("label",a["id"])} for a in actions[:28]]
    s=game.state
    ctx={"day":s.get("day"),"time":game.time_label(),"location":s.get("location"),"money":s.get("money"),
         "weather":s.get("weather"),"recent_events":[e.get("text","") for e in s.get("world_events",[])[-5:]],
         "garden":s.get("player_activities",{}).get("garden",{}),"purpose":purpose}
    t=time.time(); choice=provider.ask_choice("autoplayer","Choose one legal ordinary-life action a thoughtful player would take next. Vary activities, respond to practical needs, explore naturally, and never attempt authored story progression.",ctx,candidates);dt=time.time()-t
    cid=choice.get("id") if isinstance(choice,dict) else None
    selected=next((a for a in actions if a["id"]==cid),actions[0])
    return selected,choice,dt

class AIPlayerRunner:
    def __init__(self):
        self.lock=RLock();self.stop_event=Event();self.status={"running":False,"mode":"idle","progress":0,"phase":"Idle","feed":[],"actions":0,"llm_calls":0,"error":None}
    def snapshot(self):
        with self.lock:return deepcopy(self.status)
    def _update(self,**kw):
        with self.lock:self.status.update(kw)
    def _feed(self,text):
        with self.lock:self.status.setdefault("feed",[]).append(text);self.status["feed"]=self.status["feed"][-30:]
    def start_live(self,game,game_lock,days=7):
        with self.lock:
            if self.status.get("running"):return False
            self.stop_event.clear();self.status={"running":True,"mode":"live","progress":0,"phase":"AI player is looking around","feed":[],"actions":0,"llm_calls":0,"error":None,"days":days}
        Thread(target=self._live,args=(game,game_lock,days),daemon=True,name="bellwether-ai-player").start();return True
    def stop(self):self.stop_event.set();return True
    def _live(self,game,game_lock,days):
        try:
            start_day=game.state.get("day",1); target=start_day+days
            while game.state.get("day",1)<target and not self.stop_event.is_set():
                with game_lock: action,raw,dt=choose_action(game)
                if not action:break
                self._feed(f"Day {game.state.get('day')} {game.time_label()} · chose: {action.get('label',action['id'])} · thought for {dt:.1f}s")
                with game_lock: game.perform(action["id"])
                n=self.snapshot()["actions"]+1; calls=self.snapshot()["llm_calls"]+1;pct=min(99,int(100*(game.state.get("day",1)-start_day)/max(1,days)))
                self._update(actions=n,llm_calls=calls,progress=pct,phase=f"AI player: {action.get('label',action['id'])}")
            self._update(running=False,progress=100 if not self.stop_event.is_set() else self.snapshot()["progress"],phase="AI player finished" if not self.stop_event.is_set() else "AI player stopped")
        except Exception as e:self._update(running=False,error=f"{type(e).__name__}: {e}",phase="AI player failed")
AI_PLAYER=AIPlayerRunner()
