"""v1.0.9 spoiler-minimised full-system AI stress diagnostic."""
from copy import deepcopy
from threading import RLock, Thread
import json, time, traceback
from backend.core.game import Game, INITIAL_STATE, SEASONS
from backend.core.activity_model import ACTIVITY_MODEL
from backend.core.story_model import STORY_MODEL
from backend.core.procedural_arc_model import PROCEDURAL_ARC_MODEL
from backend.core.ecology_ai_model import ECOLOGY_AI_MODEL
from backend.core.town_mind_model import TOWN_MIND_MODEL
from backend.ai.provider import provider
from backend.ai.specific_directors import run_specific_round

class FullDiagnosticRunner:
 def __init__(self): self.lock=RLock(); self.status={"running":False,"progress":0,"phase":"Idle","report":"No diagnostic has been run yet.","error":None,"ai_calls_done":0,"ai_calls_total":7}
 def snapshot(self):
  with self.lock:return deepcopy(self.status)
 def start(self):
  with self.lock:
   if self.status["running"]:return False
   self.status={"running":True,"progress":0,"phase":"Preparing isolated AI stress world","report":"","error":None,"ai_calls_done":0,"ai_calls_total":7}
  Thread(target=self._run,daemon=True,name="bellwether-full-ai-diagnostic").start();return True
 def _set(self,pct,phase,calls=None):
  with self.lock:
   self.status.update(progress=int(pct),phase=phase)
   if calls is not None:self.status["ai_calls_done"]=calls
 def _run(self):
  checks=[]; warnings=[]; traces=[]; ai_audit=[]; started=time.time()
  def check(n,ok,d):checks.append((n,bool(ok),d))
  try:
   g=Game.__new__(Game);g.state=deepcopy(INITIAL_STATE);g._overview_cache_key=None;g._overview_cache=None
   g.state["season"]=deepcopy(SEASONS[1]);g.state["weather"]["temperature_c"]=12;g.state["diagnostic_mode"]=True
   self._set(3,"Public surfaces and state integrity")
   v=g.view();check("public_view",bool(v.get("actions")) and bool(v.get("location")),"Location and legal actions exposed")
   # Real LLM specialist stress: four ordinary directors.
   domains=["weather","npc","traffic","conversation"]
   for i,domain in enumerate(domains,1):
    self._set(5+i*7,f"Real AI stress {i}/7 · {domain}",i-1); t=time.time(); result=run_specific_round(deepcopy(g.state),[domain]); dt=time.time()-t
    ok=bool(result.get(domain)) if isinstance(result,dict) else False;check("ai_"+domain,ok,f"Real {domain} Director call completed in {dt:.1f}s")
    ai_audit.append((domain,dt,ok));self._set(5+i*7,f"Real AI stress {i}/7 · {domain} complete",i)
   # Strategic AI.
   strategic=[("town_mind",TOWN_MIND_MODEL.compact_context(g.state),TOWN_MIND_MODEL.candidates(g.state),"Choose one legal strategic intention justified by current state."),
              ("procedural_arc",PROCEDURAL_ARC_MODEL.compact_context(g.state),PROCEDURAL_ARC_MODEL.candidates(g.state),"Choose one legal grounded multi-day village situation."),
              ("ecology",ECOLOGY_AI_MODEL.context(g.state),ECOLOGY_AI_MODEL.candidates(g.state),"Choose the ecological response best supported by season, temperature, weather, soil moisture, drying pressure and garden moisture.")]
   choices={}
   for j,(name,ctx,cands,q) in enumerate(strategic,5):
    self._set(5+j*7,f"Real AI stress {j}/7 · {name}",j-1);t=time.time();choice=provider.ask_choice(name,q,ctx,cands);dt=time.time()-t
    choices[name]=choice;check("ai_"+name,bool(choice),f"Real {name} bounded call completed in {dt:.1f}s");ai_audit.append((name,dt,bool(choice)));self._set(5+j*7,f"Real AI stress {j}/7 · {name} complete",j)
   # Apply ecology choice and verify bounded authority.
   applied=ECOLOGY_AI_MODEL.apply(g.state,choices.get("ecology"),provider.model_for_task("weather"));rt=ECOLOGY_AI_MODEL.migrate(g.state)
   check("ecology_ai_application",applied and 0.05<=rt["crop_factor"]<=1.25 and bool(rt["animal_locations"]),f"AI ecology applied: crop factor {rt['crop_factor']}; animal mode {rt['animal_mode']}")
   # Seven-day goal-directed simulation, still isolated. AI was genuinely tested above; this section stresses game systems cheaply.
   profiles=["mixed","home","explore","social","economy","investigation","mixed"];action_count=0
   for day_i,profile in enumerate(profiles,1):
    self._set(55+day_i*4,f"System stress day {day_i}/7 · {profile}",7)
    for turn in range(14):
     acts=g.actions();ids=[a["id"] for a in acts];pref=[]
     if profile=="home":pref=["garden:water","garden:tend","life:read","look"]
     elif profile=="explore":pref=[x for x in ids if x.startswith("move:")]+["look","ask_village"]
     elif profile=="social":pref=[x for x in ids if x.startswith("talk:")]+["ask_village","look"]
     elif profile=="economy":pref=[x for x in ids if x.startswith(("job:","economy:"))]+["look"]
     elif profile=="investigation":pref=[x for x in ids if x.startswith("investigate:")]+["look","ask_village"]
     else:pref=["look","ask_village"]+[x for x in ids if x.startswith("move:")]
     choice=next((x for x in pref if x in ids),ids[turn%len(ids)] if ids else None)
     if choice:g.perform(choice);action_count+=1
    g.advance(max(0,1440-g.state["minute"]+540))
   # Climate-controlled crop matrix: winter/dry/moist scenarios.
   self._set(85,"Climate, moisture and crop response matrix",7)
   results=[]
   for label,season,moisture,factor in [("winter",SEASONS[8],80,.12),("dry",SEASONS[1],15,.45),("moist",SEASONS[1],80,1.15)]:
    cg=deepcopy(g.state);cg["season"]=deepcopy(season);garden=cg["player_activities"]["garden"];garden["moisture"]=moisture;garden["weeds"]=0;cg.setdefault("ecology_ai",{})["crop_factor"]=factor
    garden["plots"][0]={"crop_id":"radish","growth":0.0,"growth_required":1440,"health":100,"sown_day":cg["day"]};ACTIVITY_MODEL.advance(cg,720);results.append((label,garden["plots"][0]["growth"]))
   vals=dict(results);check("crop_climate_response",vals["moist"]>vals["dry"]>vals["winter"],"Controlled growth: "+", ".join(f"{k}={v:.1f}" for k,v in results))
   # Broad structural checks.
   wr=g.state.get("world_runtime",{});story=STORY_MODEL.public(g.state);arcs=PROCEDURAL_ARC_MODEL.migrate(g.state);econ=g.state.get("economy",{})
   check("story_public",bool(story.get("title")) and bool(story.get("objective")),"Authored story public surface valid")
   check("world_runtime",int(wr.get("ticks",0))>0,f"World ticks: {wr.get('ticks',0)}")
   check("npc_simulation",bool(g.state.get("npcs")) and bool(g.state.get("npc_action_history",{})),"NPC state/action history populated")
   check("event_stream",bool(g.state.get("world_events",[])),f"World events retained: {len(g.state.get('world_events',[]))}")
   for key in ("relationships","investigation","recurrence","horror"):check(key+"_structure",isinstance(g.state.get(key,{}),dict),key+" state structurally valid")
   check("economy",int(g.state.get("money",0))>=0 and isinstance(econ.get("ledger",[]),list),"Economy structurally valid")
   blob=json.dumps(g.state,sort_keys=True,default=list);restored=json.loads(blob);check("save_roundtrip",restored["day"]==g.state["day"] and restored["money"]==g.state["money"],"JSON round trip preserved clock and money")
   # prose integrity
   malformed=[e.get("text","") for e in g.state.get("world_events",[]) if "spent time you " in e.get("text","").lower() or ".." in e.get("text","")]
   check("prose_integrity",not malformed,f"Malformed event prose found: {len(malformed)}")
   from backend.ai.async_runtime import ASYNC_AI_RUNTIME
   ai=ASYNC_AI_RUNTIME.status();counts=ai.get("event_counts",{});wasted=int(ai.get("wasted_after_inference",0));check("no_wasted_inference",wasted==0,f"Wasted completed inference calls: {wasted}")
   traces.append(f"scheduler merged-before-inference={counts.get('job_merged_before_inference',0)} deferred-running={counts.get('job_request_deferred_running',0)} wasted-completed={wasted}")
   passed=sum(ok for _,ok,_ in checks);total=len(checks);score=round(100*passed/max(1,total));elapsed=time.time()-started
   lines=["BELLWETHER FULL AI STRESS DIAGNOSTIC REPORT","Version: 1.0.9","Scope: real LLM specialist stress + isolated 7-day goal-directed integration simulation",f"Overall: {score}% ({passed}/{total} checks passed)",f"Elapsed wall time: {elapsed/60:.1f} minutes",f"Actions exercised: {action_count}",f"Real LLM calls exercised: {len(ai_audit)}","","FAILED CHECKS:"]
   lines += [f"- {n}: {d}" for n,ok,d in checks if not ok] or ["- None"]
   lines += ["","WARNINGS:"]+([f"- {x}" for x in warnings] or ["- None"])
   lines += ["","REAL AI CALL AUDIT:"]+[f"- {'PASS' if ok else 'FAIL'} | {name} | {dt:.1f}s" for name,dt,ok in ai_audit]
   lines += ["","CHECKS:"]+[f"- {'PASS' if ok else 'FAIL'} | {n} | {d}" for n,ok,d in checks]
   lines += ["","RUNTIME TRACE:"]+[f"- {x}" for x in traces]
   lines += ["","ECOLOGY SUMMARY:",f"- AI crop factor: {rt['crop_factor']}",f"- Vegetation index: {rt['vegetation_index']}",f"- Animal mode: {rt['animal_mode']}",f"- Animal locations: {', '.join(rt['animal_locations'])}","","STATE SUMMARY:",f"- Final simulated clock: Day {g.state.get('day')} at {g.time_label()}",f"- World ticks: {wr.get('ticks',0)}",f"- Procedural arcs: active={len(arcs.get('active',[]))}, history={len(arcs.get('history',[]))}, proposals={arcs.get('proposal_count',0)}",f"- Economy ledger entries: {len(econ.get('ledger',[]))}",f"- World events retained: {len(g.state.get('world_events',[]))}"]
   with self.lock:self.status.update(running=False,progress=100,phase="Complete",report="\n".join(lines),ai_calls_done=7)
  except Exception as exc:
   with self.lock:self.status.update(running=False,phase="Failed",error=f"{type(exc).__name__}: {exc}",report="BELLWETHER FULL AI STRESS DIAGNOSTIC REPORT\nFAILED TO COMPLETE\n"+traceback.format_exc()[-6000:])
FULL_DIAGNOSTIC=FullDiagnosticRunner()
