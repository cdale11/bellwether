
from pathlib import Path
import json
import threading
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from backend.core.game import game
from backend.ai.provider import provider

ROOT = Path(__file__).resolve().parent.parent
app = FastAPI(title="Bellwether")
game_lock = threading.RLock()
app.mount("/static", StaticFiles(directory=ROOT / "frontend" / "static"), name="static")

class ActionRequest(BaseModel):
    action: str

class TalkRequest(BaseModel):
    npc_id: str
    text: str

@app.get("/", response_class=HTMLResponse)
def home():
    return (ROOT / "frontend" / "templates" / "index.html").read_text(encoding="utf-8")

@app.get("/api/state")
def state():
    return game.view()


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
        "run": {"index": s.get("recurrence", {}).get("run_index", 1), "recurrence": s.get("recurrence", {})},
        "simulation": {"director_status": s.get("director_status", {}), "traffic": s.get("traffic", {}), "world_runtime": s.get("world_runtime", {}), "ecology": s.get("ecology", {})},
        "npcs": npcs,
        "events": {"dynamic_events": s.get("dynamic_events", {}), "recent_world_events": s.get("world_events", [])[-20:]},
        "horror": {"pressure": s.get("supernatural_pressure", 0), "state": s.get("horror", {}), "psychology": s.get("psychology", {}), "anomaly_history": s.get("anomaly_history", [])[-20:]},
        "investigation": {"notebook": s.get("investigation", {}), "mysteries": game.investigation_overview()},
        "economy": {"money": s.get("money"), "economy": s.get("economy", {}), "employment": s.get("employment", {}), "activities": s.get("activities", {})},
        "provider": provider.last_status, "ai_runtime": s.get("ai_runtime", {}),
        "ai_events": s.get("ai_events", [])[-20:], "traces": provider.debug_traces[-40:]
    }

@app.get("/api/director-status")
def director_status():
    provider.health()
    return {
        "simulation": game.state.get("director_status", {}),
        "provider": provider.last_status,
        "events": game.state.get("ai_events", [])[-10:],
        "runtime": game.state.get("ai_runtime", {}),
        "traces": provider.debug_traces[-40:]
    }

@app.post("/api/action")
def action(req: ActionRequest):
    with game_lock:
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

@app.post("/api/new-game")
def new_game():
    with game_lock:
        return game.new_game()


@app.post("/api/director-debug/clear")
def clear_director_debug():
    provider.debug_traces.clear()
    provider._last_trace_index = None
    return {"ok": True}
