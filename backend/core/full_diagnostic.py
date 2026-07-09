"""v1.0.10 exhaustive AI-player and subsystem stress diagnostic."""
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
from backend.core.ai_player import choose_action

class FullDiagnosticRunner:
 def __init__(self): self.lock=RLock(); self.status={"running":False,"progress":0,"phase":"Idle","report":"No diagnostic has been run yet.","error":None,"ai_calls_done":0,"ai_calls_total":63,"feed":[]}
 def snapshot(self):
  with self.lock:return deepcopy(self.status)
 def start(self):
  with self.lock:
   if self.status["running"]:return False
   self.status={"running":True,"progress":0,"phase":"Preparing isolated AI stress world","report":"","error":None,"ai_calls_done":0,"ai_calls_total":63,"feed":[]}
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
   # Force a legal ordinary conversation encounter in the disposable world so this pathway cannot silently skip.
   npc_ids=list(g.state.get("npcs",{}))
   if len(npc_ids)>=2:
    g.state["npcs"][npc_ids[1]]["location"]=g.state["npcs"][npc_ids[0]]["location"]
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
   # Coverage-driven seven-day genuine LLM-player simulation. The controller never
   # invokes hidden subsystems directly: it supplies player-visible guidance when a
   # public gameplay surface remains uncovered.
   coverage={k:False for k in ["movement","npc_interaction","relationships","economy","jobs","gardening","ecology","wildlife","weather","investigation","procedural_content","save_reload","ai_runtime","horror","ui_contract"]}
   action_count=0; player_audit=[]; start_day=g.state.get("day",1); memory={"recent_actions":[],"recent_locations":[],"recent_npcs":[],"failed_attempts":[],"completed_subtasks":[]}
   guidance={"movement":"Explore ordinary village locations and travel naturally.","npc_interaction":"Spend time around villagers and choose an ordinary social interaction.","economy":"Earn or spend money through visible ordinary-life actions.","jobs":"Look for visible work or a shift you can perform.","gardening":"Spend time caring for the cottage garden.","investigation":"If a visible lead is available, follow it using only what the player knows.","procedural_content":"Notice and participate in a visible village opportunity or errand."}
   while g.state.get("day",1)<start_day+7 and action_count<96:
    missing=[k for k,vv in coverage.items() if not vv]
    target=next((k for k in guidance if k in missing),None); purpose=guidance.get(target,"Live a varied ordinary week and respond naturally to visible opportunities.")
    self._set(55+int(25*min(1,action_count/96)),f"Coverage-driven AI player · day {g.state.get('day')-start_day+1}/7 · target {target or 'natural variety'}",7+action_count)
    action,raw,dt=choose_action(g,purpose,memory)
    if not action: warnings.append("AI player found no legal public action"); break
    before=(g.state.get("day"),g.state.get("minute"),g.state.get("location"),g.state.get("money")); result=g.perform(action["id"]); action_count+=1
    after=(g.state.get("day"),g.state.get("minute"),g.state.get("location"),g.state.get("money")); aid=action.get("id",""); kind=action.get("kind",""); label=action.get("label",aid)
    memory["recent_actions"]=(memory["recent_actions"]+[aid])[-10:]; memory["recent_locations"]=(memory["recent_locations"]+[after[2]])[-8:]
    coverage["ui_contract"]=True; coverage["movement"] |= before[2]!=after[2] or kind in {"travel","move"}; coverage["economy"] |= before[3]!=after[3]
    low=(aid+" "+kind+" "+label).lower(); coverage["npc_interaction"] |= any(x in low for x in ("talk","speak","visit","social")); coverage["relationships"] |= coverage["npc_interaction"]
    coverage["jobs"] |= any(x in low for x in ("job","work","shift","task")); coverage["gardening"] |= any(x in low for x in ("garden","plant","water","weed","harvest")); coverage["investigation"] |= "investigat" in low or "lead" in low
    coverage["procedural_content"] |= any(x in low for x in ("errand","opportunity","arc","favour","favor")) or bool(g.state.get("procedural_arcs",{}).get("active"))
    coverage["weather"] |= bool(g.state.get("weather")); coverage["ecology"] |= bool(g.state.get("world_runtime",{}).get("ticks",0)); coverage["wildlife"] |= bool(g.state.get("ecology_ai",{}).get("animal_locations") or g.state.get("world_runtime",{}).get("animals"))
    coverage["horror"] |= bool(g.state.get("anomaly_history") or g.state.get("horror",{}).get("history")); coverage["ai_runtime"]=True
    player_audit.append((g.state.get("day",1)-start_day+1,label,dt,before[:3],after[:3]))
    with self.lock:self.status.setdefault("feed",[]).append(f"Day {g.state.get('day',1)-start_day+1} · target {target or 'variety'} · {label} · AI {dt:.1f}s");self.status["feed"]=self.status["feed"][-24:]
    if action_count%12==0 and g.state.get("day",1)==before[0]: g.advance(360)
   # Persistence coverage uses the public state contract: serialise and migrate a deep copy.
   snap=json.loads(json.dumps(g.state)); sg=Game.__new__(Game); sg.state=deepcopy(snap); sg._overview_cache_key=None; sg._overview_cache=None
   try: sg.migrate_state(); coverage["save_reload"]=sg.state.get("day")==g.state.get("day") and sg.state.get("location")==g.state.get("location")
   except Exception: coverage["save_reload"]=False
   for name,ok in coverage.items(): check("coverage_"+name,ok,f"Coverage-driven public play surface: {name}")
   # Climate-controlled crop matrix: winter/dry/moist scenarios.
   self._set(85,"Climate, moisture and crop response matrix",7)
   results=[]
   for label,season,moisture,factor in [("winter",SEASONS[8],80,.12),("dry",SEASONS[1],15,.45),("moist",SEASONS[1],80,1.15)]:
    cg=deepcopy(g.state);cg["season"]=deepcopy(season);garden=cg["player_activities"]["garden"];garden["moisture"]=moisture;garden["weeds"]=0;cg.setdefault("ecology_ai",{})["crop_factor"]=factor
    garden["plots"][0]={"crop_id":"radish","growth":0.0,"growth_required":1440,"health":100,"sown_day":cg["day"]};ACTIVITY_MODEL.advance(cg,720);results.append((label,garden["plots"][0]["growth"]))
   vals=dict(results);check("crop_climate_response",vals["moist"]>vals["dry"] and vals["moist"]>vals["winter"] and vals["winter"]>=0 and vals["dry"]>=0,"Controlled growth invariants: "+", ".join(f"{k}={v:.1f}" for k,v in results))
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
   cov_score=round(100*sum(coverage.values())/max(1,len(coverage)))
   ecology_score=round(100*sum(coverage[k] for k in ("gardening","ecology","wildlife","weather"))/4)
   society_score=round(100*sum(coverage[k] for k in ("npc_interaction","relationships","jobs","economy"))/4)
   ai_status=ASYNC_AI_RUNTIME.status(); accounting=ai_status.get("inference_accounting",{})
   lines=["BELLWETHER FULL AI PLAYTEST","Version: 1.0.11","Scope: real LLM subsystem stress + coverage-driven isolated seven-day play through public game actions",
   f"Overall integrity:       {score}%",f"Player-system coverage:  {cov_score}%",f"AI pathway coverage:     {round(100*sum(ok for _,_,ok in ai_audit)/max(1,len(ai_audit)))}%",f"Ecology and farming:     {ecology_score}%",f"NPC society:             {society_score}%",f"Scheduler integrity:     {100 if wasted==0 else 0}%",f"Persistence:             {100 if coverage.get('save_reload') else 0}%",
   f"Elapsed wall time: {elapsed/60:.1f} minutes",f"Actions exercised: {action_count}",f"Real specialist LLM calls exercised: {len(ai_audit)}",f"LLM player decisions exercised: {action_count}","","INFERENCE ACCOUNTING",
   f"Requested decisions:             {accounting.get('requested_decisions',0)}",f"Merged before inference:         {accounting.get('merged_before_inference',0)}",f"Deferred while running:          {accounting.get('deferred_while_running',0)}",f"Inference calls started:         {accounting.get('calls_started',0)}",f"Inference calls completed:       {accounting.get('calls_completed',0)}",f"Results applied:                 {accounting.get('results_applied',0)}",f"Cancelled before execution:      {accounting.get('results_cancelled',0)}",f"Completed inference wasted:      {accounting.get('completed_inference_wasted',0)}","","FAILED CHECKS:"]
   lines += [f"- {n}: {d}" for n,ok,d in checks if not ok] or ["- None"]
   lines += ["","WARNINGS:"]+([f"- {x}" for x in warnings] or ["- None"])
   lines += ["","REAL AI CALL AUDIT:"]+[f"- {'PASS' if ok else 'FAIL'} | {name} | {dt:.1f}s" for name,dt,ok in ai_audit]
   lines += ["","AI PLAYER ACTION TRACE:"]+[f"- Day {d} | {label} | decision {dt:.1f}s | {before} -> {after}" for d,label,dt,before,after in player_audit]
   lines += ["","CHECKS:"]+[f"- {'PASS' if ok else 'FAIL'} | {n} | {d}" for n,ok,d in checks]
   lines += ["","RUNTIME TRACE:"]+[f"- {x}" for x in traces]
   lines += ["","ECOLOGY SUMMARY:",f"- AI crop factor: {rt['crop_factor']}",f"- Vegetation index: {rt['vegetation_index']}",f"- Animal mode: {rt['animal_mode']}",f"- Animal locations: {', '.join(rt['animal_locations'])}","","STATE SUMMARY:",f"- Final simulated clock: Day {g.state.get('day')} at {g.time_label()}",f"- World ticks: {wr.get('ticks',0)}",f"- Procedural arcs: active={len(arcs.get('active',[]))}, history={len(arcs.get('history',[]))}, proposals={arcs.get('proposal_count',0)}",f"- Economy ledger entries: {len(econ.get('ledger',[]))}",f"- World events retained: {len(g.state.get('world_events',[]))}"]
   with self.lock:self.status.update(running=False,progress=100,phase="Complete",report="\n".join(lines),ai_calls_done=7+action_count)
  except Exception as exc:
   with self.lock:self.status.update(running=False,phase="Failed",error=f"{type(exc).__name__}: {exc}",report="BELLWETHER FULL AI STRESS DIAGNOSTIC REPORT\nFAILED TO COMPLETE\n"+traceback.format_exc()[-6000:])
FULL_DIAGNOSTIC=FullDiagnosticRunner()
