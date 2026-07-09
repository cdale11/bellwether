"""Spoiler-minimised automated integration playtest for Bellwether v1.0.8."""
from copy import deepcopy
from threading import RLock, Thread
import json, time, traceback
from backend.core.game import Game, INITIAL_STATE, SEASONS
from backend.core.activity_model import ACTIVITY_MODEL
from backend.core.story_model import STORY_MODEL
from backend.core.procedural_arc_model import PROCEDURAL_ARC_MODEL

class FullDiagnosticRunner:
    def __init__(self):
        self.lock=RLock(); self.status={"running":False,"progress":0,"phase":"Idle","report":"No diagnostic has been run yet.","error":None}
    def snapshot(self):
        with self.lock:return deepcopy(self.status)
    def start(self):
        with self.lock:
            if self.status["running"]: return False
            self.status={"running":True,"progress":0,"phase":"Preparing isolated test world","report":"","error":None}
        Thread(target=self._run,daemon=True,name='bellwether-full-diagnostic').start(); return True
    def _set(self,pct,phase):
        with self.lock:self.status.update(progress=int(pct),phase=phase)
    def _run(self):
        checks=[]; warnings=[]; traces=[]
        def check(name,ok,detail): checks.append((name,bool(ok),detail))
        try:
            g=Game.__new__(Game); g.state=deepcopy(INITIAL_STATE); g._overview_cache_key=None; g._overview_cache=None
            g.state['season']=deepcopy(SEASONS[1]); g.state['weather']['temperature_c']=12; g.state['diagnostic_mode']=True
            self._set(5,'Baseline state and public view')
            v=g.view(); check('public_view',bool(v.get('actions')) and bool(v.get('location')),'Public view exposes location and legal actions')
            # Exercise legal action pathways for seven simulated days. Avoid free talk because it is intentionally synchronous.
            profiles=['mixed','home','explore','social','economy','investigation','mixed']
            action_count=0
            for day_i,profile in enumerate(profiles,1):
                self._set(8+day_i*8,f'Simulating day {day_i}/7 · {profile} behaviour')
                for turn in range(14):
                    actions=g.actions(); ids=[a['id'] for a in actions]
                    preferred=[]
                    if profile=='home': preferred=['garden:water','garden:tend','life:read','look']
                    elif profile=='explore': preferred=[x for x in ids if x.startswith('move:')]+['look','ask_village']
                    elif profile=='social': preferred=[x for x in ids if x.startswith('talk:')]+['ask_village','look']
                    elif profile=='economy': preferred=[x for x in ids if x.startswith('job:') or x.startswith('economy:')]+['look']
                    elif profile=='investigation': preferred=[x for x in ids if x.startswith('investigate:')]+['look','ask_village']
                    else: preferred=['look','ask_village']+[x for x in ids if x.startswith('move:')]
                    choice=next((x for x in preferred if x in ids), ids[turn%len(ids)] if ids else None)
                    if choice:
                        g.perform(choice); action_count+=1
                # ensure biological time crosses full days through normal advance path
                g.advance(max(0,1440-g.state['minute']+540))
            self._set(68,'Crop lifecycle audit')
            # Controlled crop audit on isolated state, exercising authoritative advance model.
            cg=g.state['player_activities']['garden']; cg['soil_prepared']=True; cg['moisture']=80; cg['weeds']=0
            cg['plots'][0]={"crop_id":"radish","growth":0.0,"growth_required":1440,"health":100,"sown_day":g.state['day']}
            before=cg['plots'][0]['growth']; ACTIVITY_MODEL.advance(g.state,720); mid=cg['plots'][0]['growth']; ACTIVITY_MODEL.advance(g.state,900); stage=ACTIVITY_MODEL.stage(cg['plots'][0])
            check('crop_growth',mid>before and stage in {'growing','maturing','ready'},f'Radish growth {before:.1f} → {mid:.1f}; final stage {stage}')
            self._set(74,'Story and opportunity reachability')
            story=STORY_MODEL.public(g.state); check('story_public',bool(story.get('title')) and bool(story.get('objective')),'Authored story exposes a current title and objective')
            arcs=PROCEDURAL_ARC_MODEL.migrate(g.state); candidates=PROCEDURAL_ARC_MODEL.candidates(g.state); arc=PROCEDURAL_ARC_MODEL.start(g.state,candidates[0]['id'],'diagnostic_template') if candidates else None; public=g.view().get('state',{}).get('quests',{}).get('side',[]); check('procedural_arc_visibility',bool(arc) and any(q.get('procedural') for q in public),'A legal procedural arc becomes a visible side-story opportunity')
            self._set(80,'Save/load round trip')
            blob=json.dumps(g.state,sort_keys=True,default=list); restored=json.loads(blob); check('save_roundtrip',restored['day']==g.state['day'] and restored['money']==g.state['money'],'JSON state round trip preserves clock and money')
            self._set(86,'World, ecology, economy and horror invariants')
            wr=g.state.get('world_runtime',{}); check('world_runtime',int(wr.get('ticks',0))>0,f"World ticks: {wr.get('ticks',0)}")
            check('npc_simulation',bool(g.state.get('npcs')) and bool(g.state.get('npc_action_history',{})),'NPC state and action history exist after simulated play')
            check('event_stream',len(g.state.get('world_events',[]))>0,f"World events retained: {len(g.state.get('world_events',[]))}")
            check('relationship_structure',isinstance(g.state.get('relationships',{}),dict),'Relationship state remains structurally valid')
            check('investigation_structure',isinstance(g.state.get('investigation',{}),dict),'Investigation notebook remains structurally valid')
            check('recurrence_structure',isinstance(g.state.get('recurrence',{}),dict),'Recurrence state remains structurally valid')
            eco=wr.get('tendencies',{}); check('ecology',all(k in eco for k in ('soil_saturation','bird_activity','pollinator_activity')),'Ecology tendencies populated')
            econ=g.state.get('economy',{}); check('economy',int(g.state.get('money',0))>=0 and isinstance(econ.get('ledger',[]),list),'Money non-negative and ledger structurally valid')
            horror=g.state.get('horror',{}); check('horror_structure',isinstance(horror,dict),'Horror state structurally valid')
            self._set(92,'Scheduler efficiency audit')
            from backend.ai.async_runtime import ASYNC_AI_RUNTIME
            ai=ASYNC_AI_RUNTIME.status(); counts=ai.get('event_counts',{})
            wasted=int(ai.get('wasted_after_inference',0)); check('no_wasted_inference',wasted==0,f'Wasted-after-inference counter: {wasted}')
            check('ai_runtime_structure',ai.get('policy')=='single_worker_priority_queue_lossless_running_results' and ai.get('worker_threads')==1,'Single-worker lossless-running-results policy active')
            merged=int(counts.get('job_merged_before_inference',0)); deferred=int(counts.get('job_request_deferred_running',0)); traces.append(f'AI scheduler: merged-before-inference={merged}; deferred-while-running={deferred}; wasted-after-inference={wasted}')
            self._set(97,'Building compact diagnostic report')
            passed=sum(x[1] for x in checks); total=len(checks); score=round(100*passed/max(1,total))
            failed=[x for x in checks if not x[1]]
            lines=['BELLWETHER FULL DIAGNOSTIC REPORT','Version: 1.0.8','Scope: isolated 7-day goal-directed integration simulation','Overall: %d%% (%d/%d checks passed)'%(score,passed,total),f'Actions exercised: {action_count}','', 'FAILED CHECKS:']
            lines += [f'- {n}: {d}' for n,ok,d in failed] or ['- None']
            lines += ['', 'WARNINGS:'] + ([f'- {x}' for x in warnings] or ['- None'])
            lines += ['', 'CHECKS:']+[f"- {'PASS' if ok else 'FAIL'} | {n} | {d}" for n,ok,d in checks]
            lines += ['', 'RUNTIME TRACE:']+[f'- {x}' for x in traces]
            lines += ['', 'STATE SUMMARY:',f"- Final simulated clock: Day {g.state.get('day')} at {g.time_label()}",f"- World ticks: {wr.get('ticks',0)}",f"- Procedural arcs: active={len(arcs.get('active',[]))}, history={len(arcs.get('history',[]))}, proposals={arcs.get('proposal_count',0)}",f"- Economy ledger entries: {len(econ.get('ledger',[]))}",f"- World events retained: {len(g.state.get('world_events',[]))}"]
            with self.lock:self.status.update(running=False,progress=100,phase='Complete',report='\n'.join(lines))
        except Exception as exc:
            with self.lock:self.status.update(running=False,phase='Failed',error=f'{type(exc).__name__}: {exc}',report='BELLWETHER FULL DIAGNOSTIC REPORT\nFAILED TO COMPLETE\n'+traceback.format_exc()[-4000:])

FULL_DIAGNOSTIC=FullDiagnosticRunner()
