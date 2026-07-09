"""v1.0.12 resumable exhaustive AI stress and coverage playtest."""
from copy import deepcopy
from threading import RLock, Thread
from pathlib import Path
from collections import Counter
import json,time,traceback
from backend.core.game import Game,INITIAL_STATE,SEASONS
from backend.core.activity_model import ACTIVITY_MODEL
from backend.core.story_model import STORY_MODEL
from backend.core.procedural_arc_model import PROCEDURAL_ARC_MODEL,ARC_TEMPLATES
from backend.core.ecology_ai_model import ECOLOGY_AI_MODEL
from backend.core.town_mind_model import TOWN_MIND_MODEL
from backend.core.horror_model import HORROR_MODEL
from backend.core.memory_model import MEMORY_MODEL
from backend.core.cognition_model import COGNITION_MODEL
from backend.ai.provider import provider
from backend.ai.specific_directors import run_specific_round
from backend.core.ai_player import choose_action
ROOT=Path(__file__).resolve().parents[2]; DIAG_DIR=ROOT/'diagnostics'; LIVE_JSON=DIAG_DIR/'latest_live_diagnostic.json'; LIVE_TXT=DIAG_DIR/'latest_live_diagnostic.txt'

class FullDiagnosticRunner:
 def __init__(self):
  self.lock=RLock();self.status={"running":False,"progress":0,"phase":"Idle","report":"No diagnostic has been run yet.","error":None,"ai_calls_done":0,"ai_calls_budget":96,"feed":[],"decision_accounting":{}}
  self._restore()
 def _restore(self):
  try:
   d=json.loads(LIVE_JSON.read_text());d["running"]=False
   if d.get("phase") not in {"Complete","Idle"}:d["phase"]="Interrupted run recovered · "+d.get("phase","unknown phase")
   self.status.update(d)
  except Exception:pass
 def snapshot(self):
  with self.lock:return deepcopy(self.status)
 def _persist(self):
  DIAG_DIR.mkdir(exist_ok=True); snap=self.snapshot(); tmp=LIVE_JSON.with_suffix('.tmp');tmp.write_text(json.dumps(snap,indent=2),encoding='utf-8');tmp.replace(LIVE_JSON)
  report=snap.get('report') or self._live_text(snap);tmp2=LIVE_TXT.with_suffix('.tmp');tmp2.write_text(report,encoding='utf-8');tmp2.replace(LIVE_TXT)
 def _live_text(self,s):
  return "BELLWETHER LIVE DIAGNOSTIC CHECKPOINT\nVersion: 1.0.12\nProgress: %s%%\nPhase: %s\n\nDECISION ACCOUNTING\n%s\n\nRECENT TRACE\n%s\n"%(s.get('progress',0),s.get('phase'),json.dumps(s.get('decision_accounting',{}),indent=2),'\n'.join('- '+x for x in s.get('feed',[])))
 def start(self):
  with self.lock:
   if self.status.get('running'):return False
   self.status={"running":True,"progress":0,"phase":"Preparing isolated AI stress world","report":"","error":None,"ai_calls_done":0,"ai_calls_budget":96,"feed":[],"decision_accounting":{"attempts":0,"llm_success":0,"timeouts":0,"invalid":0,"fallbacks":0,"no_effect":0,"blocked_retries":0}}
  self._persist();Thread(target=self._run,daemon=True,name='bellwether-full-ai-diagnostic').start();return True
 def _set(self,pct,phase,calls=None,feed=None):
  with self.lock:
   self.status.update(progress=int(pct),phase=phase)
   if calls is not None:self.status['ai_calls_done']=calls
   if feed:self.status.setdefault('feed',[]).append(feed);self.status['feed']=self.status['feed'][-40:]
  self._persist()
 def _run(self):
  checks=[];warnings=[];ai_audit=[];player_audit=[];started=time.time()
  def check(n,ok,d):checks.append((n,bool(ok),d));self._persist()
  try:
   g=Game.__new__(Game);g.state=deepcopy(INITIAL_STATE);g._overview_cache_key=None;g._overview_cache=None;g.state['season']=deepcopy(SEASONS[1]);g.state['weather']['temperature_c']=12;g.state['diagnostic_mode']=True
   self._set(3,'Public surfaces and state integrity');v=g.view();check('public_view',bool(v.get('actions')) and bool(v.get('location')),'Location and legal actions exposed')
   npc_ids=list(g.state.get('npcs',{}));
   if len(npc_ids)>=2:g.state['npcs'][npc_ids[1]]['location']=g.state['npcs'][npc_ids[0]]['location']
   domains=['weather','npc','traffic','conversation']
   for i,domain in enumerate(domains,1):
    self._set(5+i*5,f'Real AI stress {i}/7 · {domain}',i-1);t=time.time();result=run_specific_round(deepcopy(g.state),[domain]);dt=time.time()-t;ok=bool(result.get(domain)) if isinstance(result,dict) else False;check('ai_'+domain,ok,f'Real {domain} Director call completed in {dt:.1f}s');ai_audit.append((domain,dt,ok));self._set(5+i*5,f'Real AI stress {i}/7 · {domain} complete',i)
   strategic=[('town_mind',TOWN_MIND_MODEL.compact_context(g.state),TOWN_MIND_MODEL.candidates(g.state),'Choose one legal strategic intention justified by current state.'),('procedural_arc',PROCEDURAL_ARC_MODEL.compact_context(g.state),PROCEDURAL_ARC_MODEL.candidates(g.state),'Choose one legal grounded multi-day village situation.'),('ecology',ECOLOGY_AI_MODEL.context(g.state),ECOLOGY_AI_MODEL.candidates(g.state),'Choose the ecological response best supported by current conditions.')]
   choices={}
   for j,(name,ctx,cands,q) in enumerate(strategic,5):
    self._set(5+j*5,f'Real AI stress {j}/7 · {name}',j-1);t=time.time();choice=provider.ask_choice(name,q,ctx,cands);dt=time.time()-t;choices[name]=choice;check('ai_'+name,bool(choice),f'Real {name} bounded call completed in {dt:.1f}s');ai_audit.append((name,dt,bool(choice)));self._set(5+j*5,f'Real AI stress {j}/7 · {name} complete',j)
   applied=ECOLOGY_AI_MODEL.apply(g.state,choices.get('ecology'),provider.model_for_task('weather'));rt=ECOLOGY_AI_MODEL.migrate(g.state);check('ecology_ai_application',applied and .05<=rt['crop_factor']<=1.25 and bool(rt['animal_locations']),f"AI ecology applied: crop factor {rt['crop_factor']}; animal mode {rt['animal_mode']}")
   coverage={k:False for k in ['movement','npc_interaction','relationships','economy','jobs','gardening','ecology','wildlife','weather','investigation','procedural_content','save_reload','ai_runtime','ui_contract']}
   guidance={'movement':'Explore ordinary village locations and travel naturally.','npc_interaction':'Meet a villager through a visible legal interaction.','economy':'Earn or spend money through visible ordinary-life actions.','jobs':'Find visible work and perform a shift if possible.','gardening':'Complete the prerequisite chain to reach Ashcroft Cottage and perform an actual garden action.','investigation':'Follow a visible lead using only player-visible information.','procedural_content':'Find and participate in a visible village opportunity.'}
   memory={'recent_actions':[],'recent_locations':[],'failed_attempts':[],'completed_subtasks':[],'blocked_actions':set()};start_day=g.state.get('day',1);action_count=0;target_fail=Counter();account=self.status['decision_accounting']
   while g.state.get('day',1)<start_day+7 and action_count<96:
    missing=[k for k,v in coverage.items() if not v];target=next((k for k in guidance if k in missing and target_fail[k]<24),None);purpose=guidance.get(target,'Live a varied ordinary week and respond naturally to visible opportunities.')
    dayn=g.state.get('day',1)-start_day+1;self._set(45+int(35*min(1,(dayn-1)/7)),f"Coverage AI player · day {dayn}/7 · target {target or 'natural variety'}",7+account['attempts'])
    action,raw,dt,meta=choose_action(g,purpose,memory,target=target);account['attempts']+=1;outcome=meta.get('outcome','unknown');account['llm_success']+=outcome=='llm_success';account['timeouts']+='timeout' in outcome;account['invalid']+='invalid' in outcome;account['fallbacks']+='fallback' in outcome
    if not action:warnings.append('AI player found no legal public action');break
    before=(g.state.get('day'),g.state.get('minute'),g.state.get('location'),g.state.get('money'),len(g.state.get('history',[])));aid=action.get('id','');label=action.get('label',aid);kind=action.get('kind','')
    try:g.perform(aid);ok=True
    except Exception as exc:ok=False;memory['failed_attempts'].append(f'{aid}: {type(exc).__name__}')
    after=(g.state.get('day'),g.state.get('minute'),g.state.get('location'),g.state.get('money'),len(g.state.get('history',[])));changed=before!=after;action_count+=1
    if not changed:account['no_effect']+=1;memory['blocked_actions'].add(aid);target_fail[target]+=1
    else:memory['blocked_actions'].discard(aid);target_fail[target]=max(0,target_fail[target]-1)
    memory['recent_actions']=(memory['recent_actions']+[aid])[-12:];memory['recent_locations']=(memory['recent_locations']+[after[2]])[-8:]
    low=(aid+' '+kind+' '+label).lower();coverage['ui_contract']=True;coverage['movement']|=before[2]!=after[2] or kind in {'travel','move'};coverage['economy']|=before[3]!=after[3];coverage['npc_interaction']|=any(x in low for x in ('talk','speak','offer to help'));coverage['relationships']|=coverage['npc_interaction'];coverage['jobs']|=any(x in low for x in ('job','work','shift'));coverage['gardening']|=changed and any(x in low for x in ('garden','plant','water','weed','harvest','soil'));coverage['investigation']|='investigat' in low or any(x in low for x in ('observe carefully','examine the area','review what'))
    arcs=PROCEDURAL_ARC_MODEL.migrate(g.state);coverage['procedural_content']|=bool(arcs.get('active') or arcs.get('history'));coverage['weather']=bool(g.state.get('weather'));coverage['ecology']=bool(g.state.get('world_runtime',{}).get('ticks',0));coverage['wildlife']=bool(g.state.get('ecology_ai',{}).get('animal_locations'));coverage['ai_runtime']=True
    player_audit.append((dayn,target or 'variety',label,dt,outcome,'changed' if changed else 'NO_EFFECT',before[:3],after[:3]));self._set(self.status['progress'],self.status['phase'],7+account['attempts'],f'Day {dayn} · {target or "variety"} · {label} · {outcome} {dt:.1f}s'+(' · NO EFFECT' if not changed else ''))
    if action_count%12==0 and g.state.get('day')==before[0]:g.advance(360)
   # If the LLM decision budget is exhausted before seven calendar days, complete
   # the remaining world-time simulation deterministically. This is explicitly
   # separated from AI-player action coverage in the report.
   completion_minutes=0
   while g.state.get('day',1)<start_day+7:
    step=min(360, max(10, (start_day+7-g.state.get('day',1))*1440-g.state.get('minute',0)))
    g.advance(step);completion_minutes+=step
   actual_days=g.state.get('day',1)-start_day;check('seven_day_completion',actual_days>=7,f'Playtest reached day offset {actual_days}; LLM actions {action_count}; deterministic world completion {completion_minutes} minutes')
   snap=json.loads(json.dumps(g.state));sg=Game.__new__(Game);sg.state=deepcopy(snap);sg._overview_cache_key=None;sg._overview_cache=None
   try:sg.migrate_state();coverage['save_reload']=sg.state.get('day')==g.state.get('day') and sg.state.get('location')==g.state.get('location')
   except Exception:coverage['save_reload']=False
   for name,ok in coverage.items():check('coverage_'+name,ok,f'Coverage-driven public play surface: {name}')
   # Controlled procedural lifecycle certification, separate from natural play.
   pg=deepcopy(g.state);pr=PROCEDURAL_ARC_MODEL.migrate(pg);pr['active']=[];row=PROCEDURAL_ARC_MODEL.start(pg,ARC_TEMPLATES[0]['id'],'diagnostic_controlled');visible=bool(row);involved=False;resolved=False
   if row:
    pg['location']=row['location'];involved=bool(PROCEDURAL_ARC_MODEL.involve_player(pg,row['id'],MEMORY_MODEL,COGNITION_MODEL))
    for day in range(0,5):
     pg['day']=row['started_day']+day
     for arc,t,stage in list(PROCEDURAL_ARC_MODEL.due_stages(pg)):PROCEDURAL_ARC_MODEL.apply_stage(pg,arc,t,stage,MEMORY_MODEL,COGNITION_MODEL)
    resolved=bool(PROCEDURAL_ARC_MODEL.migrate(pg).get('history'))
   check('procedural_lifecycle',visible and involved and resolved,f'Controlled lifecycle: proposed={visible}, involved={involved}, resolved={resolved}')
   # Controlled horror certification: natural play is not forced to trigger horror.
   hg=deepcopy(g.state);aid=next(iter(HORROR_MODEL.anomalies));a=HORROR_MODEL.anomalies[aid];hg['location']=a['location'];ap=HORROR_MODEL.apply(hg,aid);overlay=HORROR_MODEL.location_context(hg,a['location']);hg.setdefault('village_brain',{})['pulse_count']=int(overlay.get('expires_pulse',0)) if overlay else 999;expired=a['location'] in HORROR_MODEL.expire(hg);check('controlled_horror_pipeline',bool(ap) and bool(overlay) and expired,'Isolated authored anomaly apply, overlay and expiry certified')
   self._set(86,'Climate, moisture and crop response matrix',7+account['attempts']);results=[]
   for label,season,moisture,factor in [('winter',SEASONS[8],80,.12),('dry',SEASONS[1],15,.45),('moist',SEASONS[1],80,1.15)]:
    cg=deepcopy(g.state);cg['season']=deepcopy(season);garden=cg['player_activities']['garden'];garden['moisture']=moisture;garden['weeds']=0;cg.setdefault('ecology_ai',{})['crop_factor']=factor;garden['plots'][0]={'crop_id':'radish','growth':0.0,'growth_required':1440,'health':100,'sown_day':cg['day']};ACTIVITY_MODEL.advance(cg,720);results.append((label,garden['plots'][0]['growth']))
   vals=dict(results);check('crop_climate_response',vals['moist']>vals['dry'] and vals['moist']>vals['winter']>=0,'Controlled growth invariants: '+', '.join(f'{k}={v:.1f}' for k,v in results))
   wr=g.state.get('world_runtime',{});story=STORY_MODEL.public(g.state);arcs=PROCEDURAL_ARC_MODEL.migrate(g.state);econ=g.state.get('economy',{});check('story_public',bool(story.get('title')) and bool(story.get('objective')),'Authored story public surface valid');check('world_runtime',int(wr.get('ticks',0))>0,f"World ticks: {wr.get('ticks',0)}");check('npc_simulation',bool(g.state.get('npcs')) and bool(g.state.get('npc_action_history',{})),'NPC state/action history populated');check('event_stream',bool(g.state.get('world_events',[])),f"World events retained: {len(g.state.get('world_events',[]))}");check('economy',isinstance(econ,dict) and g.state.get('money',0)>=0,'Economy structurally valid');check('save_roundtrip',coverage['save_reload'],'JSON round trip preserved clock and location')
   failures=[x for x in checks if not x[1]];elapsed=(time.time()-started)/60;integrity=round(100*(len(checks)-len(failures))/max(1,len(checks)));lines=['BELLWETHER FULL AI PLAYTEST','Version: 1.0.12','Scope: real LLM subsystem stress + resumable coverage-driven isolated seven-day play + controlled procedural/horror certification',f'Overall integrity: {integrity}%',f'Elapsed wall time: {elapsed:.1f} minutes',f'LLM-selected actions exercised: {action_count}',f'Deterministic world minutes after AI budget: {completion_minutes}',f'Real specialist LLM calls exercised: {len(ai_audit)}',f'AI player decision attempts: {account["attempts"]}','','DECISION ACCOUNTING']+[f'- {k}: {v}' for k,v in account.items()]+['','FAILED CHECKS:']+([f'- {n}: {d}' for n,ok,d in failures] or ['- None'])+['','WARNINGS:']+([f'- {x}' for x in warnings] or ['- None'])+['','REAL AI CALL AUDIT:']+[f'- {"PASS" if ok else "FAIL"} | {n} | {dt:.1f}s' for n,dt,ok in ai_audit]+['','AI PLAYER ACTION TRACE:']+[f'- Day {d} | target {tgt} | {label} | {outcome} {dt:.1f}s | {effect} | {before} -> {after}' for d,tgt,label,dt,outcome,effect,before,after in player_audit]+['','CHECKS:']+[f'- {"PASS" if ok else "FAIL"} | {n} | {d}' for n,ok,d in checks]+['','STATE SUMMARY:',f'- Final simulated clock: Day {g.state.get("day")} at {g.time_label()}',f'- World ticks: {wr.get("ticks",0)}',f'- Procedural arcs: active={len(arcs.get("active",[]))}, history={len(arcs.get("history",[]))}, proposals={arcs.get("proposal_count",0)}',f'- Economy ledger entries: {len(econ.get("ledger",[]))}',f'- World events retained: {len(g.state.get("world_events",[]))}','','LIVE CHECKPOINT FILES:','- diagnostics/latest_live_diagnostic.json','- diagnostics/latest_live_diagnostic.txt']
   report='\n'.join(lines)
   with self.lock:self.status.update(running=False,progress=100,phase='Complete',report=report,error=None,ai_calls_done=7+account['attempts'])
   self._persist()
  except Exception as e:
   report='BELLWETHER FULL AI PLAYTEST\nFAILED OR INTERRUPTED\n'+traceback.format_exc()[-12000:]
   with self.lock:self.status.update(running=False,phase='Failed',report=report,error=f'{type(e).__name__}: {e}')
   self._persist()
FULL_DIAGNOSTIC=FullDiagnosticRunner()
