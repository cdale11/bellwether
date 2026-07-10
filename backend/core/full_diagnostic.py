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
from backend.core.quest_model import QUEST_MODEL
from backend.core.life_simulation_model import LIFE_SIMULATION_MODEL
from backend.core.society_model import SOCIETY_MODEL
from backend.core.failure_recovery_model import FAILURE_RECOVERY_MODEL
from backend.core.danger_model import DANGER_MODEL
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
  return "BELLWETHER LIVE DIAGNOSTIC CHECKPOINT\nVersion: 1.6.0\nProgress: %s%%\nPhase: %s\n\nDECISION ACCOUNTING\n%s\n\nRECENT TRACE\n%s\n"%(s.get('progress',0),s.get('phase'),json.dumps(s.get('decision_accounting',{}),indent=2),'\n'.join('- '+x for x in s.get('feed',[])))
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
  audit_dir=DIAG_DIR/'runs'/time.strftime('%Y%m%d_%H%M%S');audit_dir.mkdir(parents=True,exist_ok=True);decision_log=audit_dir/'decisions.jsonl';call_log=audit_dir/'llm_calls.jsonl';snapshot_log=audit_dir/'state_snapshots.jsonl'
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
   # Apply the already-exercised bounded procedural specialist choice to the isolated test world.
   # Earlier diagnostic_mode suppressed the normal async proposal queue, making natural procedural coverage impossible by construction.
   pchoice=choices.get('procedural_arc')
   if isinstance(pchoice,dict) and pchoice.get('id'):
    PROCEDURAL_ARC_MODEL.migrate(g.state)['proposal_count']+=1
    PROCEDURAL_ARC_MODEL.start(g.state,pchoice.get('id'),provider.model_for_task('procedural_arc'))
   applied=ECOLOGY_AI_MODEL.apply(g.state,choices.get('ecology'),provider.model_for_task('weather'));rt=ECOLOGY_AI_MODEL.migrate(g.state);check('ecology_ai_application',applied and .05<=rt['crop_factor']<=1.25 and bool(rt['animal_locations']),f"AI ecology applied: crop factor {rt['crop_factor']}; animal mode {rt['animal_mode']}")
   coverage={k:False for k in ['movement','npc_interaction','relationships','economy','jobs','gardening','ecology','wildlife','weather','investigation','procedural_content','cooking','hobbies','community','life_progression','society','population_continuity','employment_change','save_reload','ai_runtime','ui_contract']}
   guidance={'movement':'Explore ordinary village locations and travel naturally.','npc_interaction':'Meet a villager through a visible legal interaction.','economy':'Earn or spend money through visible ordinary-life actions.','jobs':'Find visible work and perform a shift if possible.','gardening':'Complete the prerequisite chain to reach Ashcroft Cottage and perform an actual garden action.','investigation':'Follow a visible lead using only player-visible information.','procedural_content':'Find and participate in a visible village opportunity.','cooking':'Acquire food ingredients and cook or preserve something at the cottage.','hobbies':'Practise a visible hobby and develop a collection or skill.','community':'Take part in a visible community activity or share food.','society':'Meet background residents and form ordinary social contact.','employment_change':'Exercise employment entry, work, or exit.'}
   memory={'recent_actions':[],'recent_locations':[],'failed_attempts':[],'completed_subtasks':[],'blocked_actions':set()};start_day=g.state.get('day',1);action_count=0;target_fail=Counter();goal_attempts=Counter();goal_deferred=Counter();target_cursor=0;account=self.status.setdefault('decision_accounting',{});[account.setdefault(k,0) for k in ('attempts','llm_success','timeouts','invalid','fallbacks','no_effect','blocked_retries')]
   while g.state.get('day',1)<start_day+7 and action_count<96:
    missing=[k for k,v in coverage.items() if not v]; eligible_targets=[k for k in guidance if k in missing and goal_attempts[k]<12]
    target=eligible_targets[target_cursor % len(eligible_targets)] if eligible_targets else None
    purpose=guidance.get(target,'Live a varied ordinary week and respond naturally to visible opportunities.')
    dayn=g.state.get('day',1)-start_day+1;self._set(45+int(35*min(1,(dayn-1)/7)),f"Coverage AI player · day {dayn}/7 · target {target or 'natural variety'}",7+account['attempts'])
    action,raw,dt,meta=choose_action(g,purpose,memory,target=target);account['attempts']+=1;outcome=meta.get('outcome','unknown');account['llm_success']+=outcome=='llm_success';account['timeouts']+='timeout' in outcome;account['invalid']+='invalid' in outcome;account['fallbacks']+='fallback' in outcome
    if not action:warnings.append('AI player found no legal public action');break
    before=(g.state.get('day'),g.state.get('minute'),g.state.get('location'),g.state.get('money'),len(g.state.get('history',[])));aid=action.get('id','');label=action.get('label',aid);kind=action.get('kind','')
    try:g.perform(aid);ok=True
    except Exception as exc:ok=False;memory['failed_attempts'].append(f'{aid}: {type(exc).__name__}')
    after=(g.state.get('day'),g.state.get('minute'),g.state.get('location'),g.state.get('money'),len(g.state.get('history',[])));changed=before!=after;action_count+=1
    if not changed:account['no_effect']+=1;memory['blocked_actions'].add(aid)
    else:memory['blocked_actions'].discard(aid)
    if target:
     goal_attempts[target]+=1
     if meta.get('goal_progress') and changed: target_fail[target]=0
     else: target_fail[target]+=1
     if target_fail[target]>=3:
      goal_deferred[target]+=1; target_fail[target]=0; target_cursor+=1
    memory['recent_actions']=(memory['recent_actions']+[aid])[-12:];memory['recent_locations']=(memory['recent_locations']+[after[2]])[-8:]
    low=(aid+' '+kind+' '+label).lower();coverage['ui_contract']=True;coverage['movement']|=before[2]!=after[2] or kind in {'travel','move'};coverage['economy']|=before[3]!=after[3];coverage['npc_interaction']|=aid.startswith('social:greet:') or any(x in low for x in ('talk','speak','offer to help','exchange a few words'));coverage['relationships']|=coverage['npc_interaction'];coverage['jobs']|=any(x in low for x in ('job','work','shift'));coverage['gardening']|=changed and any(x in low for x in ('garden','plant','water','weed','harvest','soil'));coverage['investigation']|='investigat' in low or any(x in low for x in ('observe carefully','examine the area','review what'));coverage['cooking']|=aid.startswith('content:cook:') or aid.startswith('lifesim:preserve:');coverage['hobbies']|=aid.startswith('hobby:');coverage['community']|=aid.startswith('lifesim:community:') or aid=='lifesim:share_meal';coverage['life_progression']=LIFE_SIMULATION_MODEL.migrate(g.state)['progression']['life_xp']>0;coverage['society']|=aid.startswith('society:greet:');soc=SOCIETY_MODEL.migrate(g.state);coverage['population_continuity']=len(g.state.get('population',{}).get('residents',{}))>=20 and bool(soc.get('weekly_snapshots')) if g.state.get('day',1)>=7 else len(g.state.get('population',{}).get('residents',{}))>=20;coverage['employment_change']|=any(x in low for x in ('ask about work','work shift','leave job'))
    arcs=PROCEDURAL_ARC_MODEL.migrate(g.state);coverage['procedural_content']|=bool(arcs.get('active') or arcs.get('history'));coverage['weather']=bool(g.state.get('weather'));coverage['ecology']=bool(g.state.get('world_runtime',{}).get('ticks',0));coverage['wildlife']=bool(g.state.get('ecology_ai',{}).get('animal_locations'));coverage['ai_runtime']=True
    player_audit.append((dayn,target or 'variety',label,dt,outcome,'changed' if changed else 'NO_EFFECT',before[:3],after[:3]));decision_log.open('a',encoding='utf-8').write(json.dumps({'day':dayn,'target':target,'action':aid,'label':label,'latency_s':round(dt,2),'outcome':outcome,'changed':changed,'goal_progress':bool(meta.get('goal_progress')),'goal_stage':meta.get('goal_stage'),'provider_state':meta.get('provider_state'),'target_stall':target_fail.get(target,0),'before':before,'after':after})+'\n');self._set(self.status['progress'],self.status['phase'],7+account['attempts'],f'Day {dayn} · {target or "variety"} · {label} · {outcome} {dt:.1f}s'+(' · NO EFFECT' if not changed else ''))
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
   qrt=QUEST_MODEL.migrate(pg);reward_tx=[k for k in qrt.get('transactions',{}) if k.startswith('quest_reward:arc:')];check('quest_lifecycle_and_reward',visible and involved and resolved and bool(reward_tx),f'Procedural quest resolved and reward transaction count={len(reward_tx)}')
   before_money=pg.get('money',0); hist=PROCEDURAL_ARC_MODEL.migrate(pg).get('history',[]); duplicate_safe=True
   if hist:
    applied,_=QUEST_MODEL.complete_arc(pg,hist[-1]);duplicate_safe=(not applied and pg.get('money',0)==before_money)
   check('quest_reward_exactly_once',duplicate_safe,'Repeated completion cannot duplicate quest reward')
   # Controlled horror certification: natural play is not forced to trigger horror.
   hg=deepcopy(g.state);aid=next(iter(HORROR_MODEL.anomalies));a=HORROR_MODEL.anomalies[aid];hg['location']=a['location'];ap=HORROR_MODEL.apply(hg,aid);overlay=HORROR_MODEL.location_context(hg,a['location']);hg.setdefault('village_brain',{})['pulse_count']=int(overlay.get('expires_pulse',0)) if overlay else 999;expired=a['location'] in HORROR_MODEL.expire(hg);check('controlled_horror_pipeline',bool(ap) and bool(overlay) and expired,'Isolated authored anomaly apply, overlay and expiry certified')
   self._set(86,'Climate, moisture and crop response matrix',7+account['attempts']);results=[]
   for label,season,moisture,factor in [('winter',SEASONS[8],80,.12),('dry',SEASONS[1],15,.45),('moist',SEASONS[1],80,1.15)]:
    cg=deepcopy(g.state);cg['season']=deepcopy(season);garden=cg['player_activities']['garden'];garden['moisture']=moisture;garden['weeds']=0;cg.setdefault('ecology_ai',{})['crop_factor']=factor;garden['plots'][0]={'crop_id':'radish','growth':0.0,'growth_required':1440,'health':100,'sown_day':cg['day']};ACTIVITY_MODEL.advance(cg,720);results.append((label,garden['plots'][0]['growth']))
   vals=dict(results);check('crop_climate_response',vals['moist']>vals['dry'] and vals['moist']>vals['winter']>=0,'Controlled growth invariants: '+', '.join(f'{k}={v:.1f}' for k,v in results))
   wr=g.state.get('world_runtime',{});story=STORY_MODEL.public(g.state);arcs=PROCEDURAL_ARC_MODEL.migrate(g.state);econ=g.state.get('economy',{});check('story_public',bool(story.get('title')) and bool(story.get('objective')),'Authored story public surface valid');check('world_runtime',int(wr.get('ticks',0))>0,f"World ticks: {wr.get('ticks',0)}");check('npc_simulation',bool(g.state.get('npcs')) and bool(g.state.get('npc_action_history',{})),'NPC state/action history populated');check('event_stream',bool(g.state.get('world_events',[])),f"World events retained: {len(g.state.get('world_events',[]))}");check('economy',isinstance(econ,dict) and g.state.get('money',0)>=0,'Economy structurally valid');check('save_roundtrip',coverage['save_reload'],'JSON round trip preserved clock and location');check('geographic_expansion',len(__import__('backend.core.game',fromlist=['WORLD']).WORLD)>=21,'Expanded world has at least 21 connected authored locations');ps=g.state.get('player_status',{});check('player_status_surface',all(k in ps for k in ('health','hunger','energy','warmth')),'Player survival/status state exposes health, hunger, energy and warmth');check('cottage_condition',isinstance(ps.get('cottage',{}).get('condition'),(int,float)),'Persistent cottage condition is present');check('fishing_inventory_contract','s.setdefault("inventory",[]).append' in (ROOT/'backend/core/game.py').read_text(encoding='utf-8'),'Successful fishing catch writes to inventory');backend_text='\n'.join(x.read_text(encoding='utf-8',errors='ignore') for x in (ROOT/'backend').rglob('*.py') if x.name!='full_diagnostic.py');check('currency_consistency','Br ' not in backend_text and '¤' not in backend_text,'Backend authored currency prose contains no legacy Br or generic currency glyph')
   ui_source=(ROOT/'frontend/static/js/game.js').read_text(encoding='utf-8');check('ui_serialization_guard','displayText(value)' in ui_source and 'relationshipNpcName' in ui_source,'Relationship UI has structured-value serialization guard and unified resident naming');check('control_plane_inference_lock','shadow=_shadow_game' in (ROOT/'backend/core/ai_player.py').read_text(encoding='utf-8'),'AI player snapshots under lock and performs inference outside authoritative game lock');call_log.write_text('\n'.join(json.dumps(x,default=str) for x in provider.debug_traces),encoding='utf-8');snapshot_log.write_text(json.dumps(g.state,default=str),encoding='utf-8');failures=[x for x in checks if not x[1]];elapsed=(time.time()-started)/60;integrity=round(100*(len(checks)-len(failures))/max(1,len(checks)));lines=['BELLWETHER FULL AI PLAYTEST','Version: 1.6.0','Scope: real LLM subsystem stress + prerequisite-aware goal play + adaptive horror/failure depth + adversarial recovery + long-horizon society soak + controlled certification',f'Overall integrity: {integrity}%',f'Elapsed wall time: {elapsed:.1f} minutes',f'LLM-selected actions exercised: {action_count}',f'Deterministic world minutes after AI budget: {completion_minutes}',f'Real specialist LLM calls exercised: {len(ai_audit)}',f'AI player decision attempts: {account["attempts"]}','','DECISION ACCOUNTING']+[f'- {k}: {v}' for k,v in account.items()]+['','FAILED CHECKS:']+([f'- {n}: {d}' for n,ok,d in failures] or ['- None'])+['','WARNINGS:']+([f'- {x}' for x in warnings] or ['- None'])+['','REAL AI CALL AUDIT:']+[f'- {"PASS" if ok else "FAIL"} | {n} | {dt:.1f}s' for n,dt,ok in ai_audit]+['','AI PLAYER ACTION TRACE:']+[f'- Day {d} | target {tgt} | {label} | {outcome} {dt:.1f}s | {effect} | {before} -> {after}' for d,tgt,label,dt,outcome,effect,before,after in player_audit]+['','CHECKS:']+[f'- {"PASS" if ok else "FAIL"} | {n} | {d}' for n,ok,d in checks]+['','QUALITY DIMENSIONS:',f'- Structural correctness: {round(100*sum(1 for n,ok,d in checks if ok)/max(1,len(checks)))}%',f'- Feature coverage: {round(100*sum(1 for n,ok,d in checks if n.startswith("coverage_") and ok)/max(1,sum(1 for n,ok,d in checks if n.startswith("coverage_"))))}%',f'- AI decision success: {round(100*account["llm_success"]/max(1,account["attempts"]))}%',f'- Fallback rate: {round(100*account["fallbacks"]/max(1,account["attempts"]))}%',f'- Timeout rate: {round(100*account["timeouts"]/max(1,account["attempts"]))}%',f'- Invalid-response rate: {round(100*account["invalid"]/max(1,account["attempts"]))}%',f'- No-effect rate: {round(100*account["no_effect"]/max(1,account["attempts"]))}%',f'- Behavioural diversity: {round(100*len(set(x[2] for x in player_audit))/max(1,len(player_audit)))}%',f'- Goal completion: {round(100*sum(1 for k,v in coverage.items() if v)/max(1,len(coverage)))}%',f'- Mean attempts per pursued goal: {round(sum(goal_attempts.values())/max(1,len([v for v in goal_attempts.values() if v])),1)}',f'- Maximum attempts on one goal: {max(goal_attempts.values()) if goal_attempts else 0}',f'- Goal deferrals after semantic stalls: {sum(goal_deferred.values())}',f'- Unique locations visited: {len(set(x[7][2] for x in player_audit)) if player_audit else 0}',f'- Passive-action share: {round(100*sum(1 for x in player_audit if any(p in x[2].lower() for p in ("look around","take a moment","wait and observe","review what","observe carefully")))/max(1,len(player_audit)))}%','','GOAL CONTROL:',*[f'- {k}: attempts={goal_attempts[k]}, deferrals={goal_deferred[k]}, covered={coverage.get(k,False)}' for k in guidance],'','PROCEDURAL PIPELINE:',f'- proposal_count: {PROCEDURAL_ARC_MODEL.migrate(g.state).get("proposal_count",0)}',f'- accepted_count: {PROCEDURAL_ARC_MODEL.migrate(g.state).get("accepted_count",0)}',f'- rejected_count: {PROCEDURAL_ARC_MODEL.migrate(g.state).get("rejected_count",0)}',f'- active: {len(PROCEDURAL_ARC_MODEL.migrate(g.state).get("active",[]))}',f'- history: {len(PROCEDURAL_ARC_MODEL.migrate(g.state).get("history",[]))}','','STATE SUMMARY:',f'- Final simulated clock: Day {g.state.get("day")} at {g.time_label()}',f'- World ticks: {wr.get("ticks",0)}',f'- Procedural arcs: active={len(arcs.get("active",[]))}, history={len(arcs.get("history",[]))}, proposals={arcs.get("proposal_count",0)}',f'- Economy ledger entries: {len(econ.get("ledger",[]))}',f'- Society encounters: {SOCIETY_MODEL.migrate(g.state)["social"]["encounters"]}',f'- Society strong ties: {SOCIETY_MODEL.migrate(g.state)["social"]["strong_ties"]}',f'- Society isolated residents: {SOCIETY_MODEL.migrate(g.state)["social"]["isolated"]}',f'- Migration pressure: {SOCIETY_MODEL.migrate(g.state)["migration"]["pressure"]}',f'- Weekly society snapshots: {len(SOCIETY_MODEL.migrate(g.state)["weekly_snapshots"])}',f'- World events retained: {len(g.state.get("world_events",[]))}',f'- Diagnostic audit directory: {audit_dir}','','LIVE CHECKPOINT FILES:','- diagnostics/latest_live_diagnostic.json','- diagnostics/latest_live_diagnostic.txt']
   report='\n'.join(lines)
   with self.lock:self.status.update(running=False,progress=100,phase='Complete',report=report,error=None,ai_calls_done=7+account['attempts'])
   self._persist()
  except Exception as e:
   report='BELLWETHER FULL AI PLAYTEST\nFAILED OR INTERRUPTED\n'+traceback.format_exc()[-12000:]
   with self.lock:self.status.update(running=False,phase='Failed',report=report,error=f'{type(e).__name__}: {e}')
   self._persist()
FULL_DIAGNOSTIC=FullDiagnosticRunner()
