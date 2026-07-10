
from pathlib import Path
import json
import threading
import os
import subprocess
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from backend.core.game import game
from backend.core.horror_model import HORROR_MODEL
from backend.core.horror_aftermath_model import HORROR_AFTERMATH_MODEL
from backend.core.interface_horror_model import INTERFACE_HORROR_MODEL
from backend.ai.provider import provider
from backend.ai.async_runtime import ASYNC_AI_RUNTIME
from backend.core.failure_recovery_model import FAILURE_RECOVERY_MODEL
from backend.core.story_model import STORY_MODEL
from backend.core.ending_model import ENDING_MODEL
from backend.core.postgame_model import POSTGAME_MODEL
from backend.core.quest_model import QUEST_MODEL
from backend.core.town_mind_model import TOWN_MIND_MODEL
from backend.core.interpretation_model import INTERPRETATION_MODEL
from backend.core.presentation_ledger_model import PRESENTATION_LEDGER_MODEL

ROOT = Path(__file__).resolve().parent.parent
app = FastAPI(title="Bellwether")
game_lock = threading.RLock()
_harvest_stop = threading.Event()
def _ai_result_harvester():
    # Results are applied under the same lock as player actions; the worker itself never mutates game state.
    while not _harvest_stop.wait(0.5):
        status=ASYNC_AI_RUNTIME.status()
        if status.get("completed_waiting"):
            with game_lock:
                game.harvest_async_ai_results()
@app.on_event("startup")
def _start_ai_harvester():
    if not any(t.name=="bellwether-ai-harvest" and t.is_alive() for t in threading.enumerate()):
        threading.Thread(target=_ai_result_harvester,name="bellwether-ai-harvest",daemon=True).start()
@app.on_event("shutdown")
def _stop_ai_harvester(): _harvest_stop.set()
app.mount("/static", StaticFiles(directory=ROOT / "frontend" / "static"), name="static")

class ActionRequest(BaseModel):
    action: str

class TalkRequest(BaseModel):
    npc_id: str
    text: str

class PortableSaveRequest(BaseModel):
    state: dict

@app.get("/", response_class=HTMLResponse)
def home():
    return (ROOT / "frontend" / "templates" / "index.html").read_text(encoding="utf-8")

@app.get("/api/state")
def state():
    with game_lock:
        return game.view()



def _rss_mb(pid):
    try:
        with open(f"/proc/{pid}/status",encoding="utf-8") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    return round(int(line.split()[1])/1024,1)
    except Exception: pass
    return None

def _ollama_rss_mb():
    try:
        out=subprocess.check_output(["ps","-C","ollama","-o","rss="],text=True,timeout=1)
        return round(sum(int(x) for x in out.split() if x.isdigit())/1024,1)
    except Exception: return None

@app.get("/api/backlog")
def backlog(offset:int=0, limit:int=100, q:str="", kind:str="all"):
    with game_lock:
        return PRESENTATION_LEDGER_MODEL.page(game.state,offset,limit,q,kind)

@app.get("/api/memory-status")
def memory_status():
    with game_lock:
        raw=json.dumps(game.state,separators=(",",":"),ensure_ascii=False).encode("utf-8")
        ledger=PRESENTATION_LEDGER_MODEL.migrate(game.state)
        ai=ASYNC_AI_RUNTIME.status()
        return {"game_rss_mb":_rss_mb(os.getpid()),"ollama_rss_mb":_ollama_rss_mb(),"state_json_mb":round(len(raw)/(1024*1024),2),"backlog_entries":len(ledger.get("entries",[])),"ai_jobs":{"queued":ai.get("queued",0),"running":ai.get("running",0),"completed_waiting":ai.get("completed_waiting",0)},"models":{"fast":provider.fast_model,"deep":provider.deep_model,"num_ctx":provider.num_ctx,"keep_alive":provider.keep_alive,"single_model_mode":provider.fast_model==provider.deep_model,"residency_warning":None if provider.fast_model==provider.deep_model else "Fast and deep roles use different models; on low-memory hosts this can cause overlapping Ollama residency."}}

@app.get("/api/pacing-status")
def pacing_status():
    """Read-only adaptive pacing state for the UI settling interval."""
    with game_lock:
        return game.simulation_pacing_status()


@app.get("/api/developer-status")
def developer_status():
    """Read-only development inspector. Never mutates authoritative state."""
    provider.health()
    s = game.state
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    npcs = {nid: {
        "name": n.get("name", nid), "location": n.get("location"),
        "activity": n.get("activity"), "visible": n.get("visible", True)
    } for nid, n in s.get("npcs", {}).items()}
    return {
        "version": version,
        "clock": {"day": s.get("day"), "time": game.time_label(), "season": s.get("season"), "weather": s.get("weather"), "daypart": s.get("daypart")},
        "player": {"location": s.get("location"), "money": s.get("money"), "inventory": s.get("inventory", []), "identity": s.get("player_identity", {}), "danger": s.get("danger", {})},
        "run": {"index": s.get("recurrence", {}).get("run_index", 1), "recurrence": s.get("recurrence", {}), "expanded": __import__("backend.core.recurrence_model", fromlist=["RECURRENCE_MODEL"]).RECURRENCE_MODEL.developer_context(game.state)},
        "simulation": {"director_status": s.get("director_status", {}), "traffic": s.get("traffic", {}), "world_runtime": s.get("world_runtime", {}), "ecology": s.get("world_runtime", {}).get("tendencies", {})},
        "npcs": npcs,
        "events": {"dynamic_events": s.get("dynamic_events", {}), "recent_world_events": s.get("world_events", [])[-20:]},
        "horror": {"pressure": s.get("supernatural_pressure", 0), "state": s.get("horror", {}), "psychology": s.get("psychology", {}), "anomaly_history": s.get("anomaly_history", [])[-20:], "adaptive": HORROR_MODEL.developer_context(game.state), "aftermath": HORROR_AFTERMATH_MODEL.developer_context(game.state), "interface": INTERFACE_HORROR_MODEL.developer_context(game.state)},
        "investigation": {"notebook": s.get("investigation", {}), "mysteries": game.investigation_overview()},
        "authored_story": STORY_MODEL.public(game.state), "procedural_arcs": s.get("procedural_arcs", {}), "quest_lifecycle": QUEST_MODEL.developer_context(game.state), "ending_families": ENDING_MODEL.public(game.state), "postgame": POSTGAME_MODEL.public(game.state),
        "economy": {"money": s.get("money"), "economy": s.get("economy", {}), "employment": s.get("employment", {}), "activities": s.get("activities", {})},
        # v3.0-RC: expose the v2.x simulation layers explicitly. These are read-only
        # diagnostic surfaces; authoritative mutation remains inside each model.
        "v2_systems": {
            "property": s.get("property", {}),
            "businesses": s.get("player_businesses", {}),
            "transport": s.get("transport", {}),
            "npc_lives": s.get("npc_lives", {}),
            "relationship_life": s.get("relationship_life", {}),
            "town_consciousness": TOWN_MIND_MODEL.developer_context(game.state),
            "social_obligations_and_goals": __import__("backend.core.social_obligation_model",fromlist=["SOCIAL_OBLIGATION_MODEL"]).SOCIAL_OBLIGATION_MODEL.public(game.state),
            "interpretations": {o: INTERPRETATION_MODEL.public_summary(game.state,o) for o in INTERPRETATION_MODEL.OBSERVERS},
            "resistance": s.get("resistance", {}),
            "village_evolution": s.get("village_evolution", {}),
            "narrative_expansion": s.get("narrative_expansion", {}),
            "story_consciousness": s.get("story_consciousness_integration", {}),
            "systemic_horror": s.get("systemic_horror_integration", {}),
        },
        "provider": {**provider.last_status, "telemetry": provider.telemetry()}, "ai_runtime": {**s.get("ai_runtime", {}), "background": ASYNC_AI_RUNTIME.status(), "pacing": game.simulation_pacing_status()}, "ai_player": __import__("backend.core.ai_player", fromlist=["AI_PLAYER"]).AI_PLAYER.snapshot(), "failure_recovery": FAILURE_RECOVERY_MODEL.developer_context(game.state),
        "ai_events": s.get("ai_events", [])[-20:], "traces": provider.debug_traces[-40:]
    }

@app.get("/api/director-status")
def director_status():
    provider.health()
    return {
        "simulation": game.state.get("director_status", {}),
        "provider": provider.last_status,
        "events": game.state.get("ai_events", [])[-10:],
        "runtime": {**game.state.get("ai_runtime", {}), "background": ASYNC_AI_RUNTIME.status()},
        "traces": provider.debug_traces[-40:]
    }


@app.post("/api/ai/self-test")
def ai_self_test():
    health=provider.health()
    if not health.get("connected"):
        return {"ok":False,"stage":"connection","status":health}
    started=__import__("time").time()
    value=provider.ask_value("health_check","Return the exact word BELLWETHER_READY.",{"purpose":"developer runtime self-test"},allowed=["BELLWETHER_READY"])
    return {"ok":value=="BELLWETHER_READY","stage":"inference","value":value,"latency_s":round(__import__("time").time()-started,2),"status":dict(provider.last_status)}

@app.post("/api/action")
def action(req: ActionRequest):
    with game_lock:
        legal={str(a.get("id")) for a in game.actions()}
        if req.action not in legal:
            return {"ok": False, "message": "That action is no longer available in the current state.", "view": game.view()}
        return game.perform(req.action)

@app.post("/api/talk")
def talk(req: TalkRequest):
    with game_lock:
        return game.free_talk(req.npc_id, req.text)


@app.post("/api/acknowledge")
def acknowledge():
    with game_lock:
        return game.acknowledge_messages()

@app.post("/api/save")
def save():
    with game_lock:
        return game.save()

@app.post("/api/load")
def load():
    with game_lock:
        return game.load()

@app.get("/api/save-file")
def save_file():
    """Export the current authoritative state as a local, copyable JSON file."""
    with game_lock:
        game.compile_llm_overview()
        version=(ROOT / "VERSION").read_text(encoding="utf-8").strip()
        game.state.setdefault("save_meta", {}).update({"schema": 1, "game_version": version, "saved_day": game.state.get("day",1), "saved_minute": game.state.get("minute",0)})
        payload=json.dumps(game.state, indent=2).encode("utf-8")
    return Response(payload, media_type="application/json", headers={"Content-Disposition": 'attachment; filename="bellwether-save.json"'})

@app.post("/api/load-file")
def load_file(req: PortableSaveRequest):
    with game_lock:
        return game.load_payload(req.state)

@app.post("/api/new-game")
def new_game():
    with game_lock:
        return game.new_game()

@app.post("/api/reset-fresh")
def reset_fresh():
    with game_lock:
        return game.reset_fresh()


@app.post("/api/director-debug/clear")
def clear_director_debug():
    provider.debug_traces.clear()
    provider._last_trace_index = None
    return {"ok": True}

@app.post('/api/diagnostic/full/start')
def diagnostic_full_start():
    from backend.core.full_diagnostic import FULL_DIAGNOSTIC
    started=FULL_DIAGNOSTIC.start()
    return {'started':started, **FULL_DIAGNOSTIC.snapshot()}

@app.get('/api/diagnostic/full/status')
def diagnostic_full_status():
    from backend.core.full_diagnostic import FULL_DIAGNOSTIC
    return FULL_DIAGNOSTIC.snapshot()

@app.post('/api/ai-player/start')
def ai_player_start():
    from backend.core.ai_player import AI_PLAYER
    return {'started':AI_PLAYER.start_live(game,game_lock,7), **AI_PLAYER.snapshot()}

@app.post('/api/ai-player/stop')
def ai_player_stop():
    from backend.core.ai_player import AI_PLAYER
    AI_PLAYER.stop(); return AI_PLAYER.snapshot()

@app.get('/api/ai-player/status')
def ai_player_status():
    from backend.core.ai_player import AI_PLAYER
    return AI_PLAYER.snapshot()

@app.get('/api/ai-player/report')
def ai_player_report():
    from backend.core.ai_player import AI_PLAYER
    status=AI_PLAYER.snapshot()
    source=AI_PLAYER.live_report_path if status.get('running') and AI_PLAYER.live_report_path.exists() else AI_PLAYER.report_path
    if not source.exists() and AI_PLAYER.live_report_path.exists(): source=AI_PLAYER.live_report_path
    text=source.read_text(encoding='utf-8') if source.exists() else 'No overnight AI player report has been generated yet.'
    version=(ROOT / "VERSION").read_text(encoding="utf-8").strip()
    return Response(text, media_type='text/plain', headers={'Content-Disposition':f'attachment; filename="Bellwether_v{version}_overnight_AI_soak_report.txt"'})

@app.post('/api/qa/{tier}/start')
def qa_tier_start(tier: str):
    from backend.core.qa_runner import QA_RUNNER
    started=QA_RUNNER.start(tier)
    return {'started':started, **QA_RUNNER.snapshot()}

@app.get('/api/qa/status')
def qa_status():
    from backend.core.qa_runner import QA_RUNNER
    return QA_RUNNER.snapshot()

@app.get('/api/qa/bundle')
def qa_bundle():
    from backend.core.qa_runner import QA_RUNNER
    path=QA_RUNNER.bundle(); version=(ROOT/'VERSION').read_text().strip()
    return Response(path.read_bytes(),media_type='application/zip',headers={'Content-Disposition':f'attachment; filename="Bellwether_v{version}_QA_Bundle.zip"'})
