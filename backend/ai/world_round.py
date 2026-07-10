
from backend.ai.provider import provider
from backend.ai.repair import repair_world_round
SHAPE={"weather":{"state":"weather"},"npc":{"changes":[{"npc":"id","activity":"intent","destination":"place"}]},"traffic":{"changes":[{"vehicle":"id","activity":"intent","destination":"place"}]},"conversation":{"interactions":[{"participants":["id","id"],"topic":"topic","summary":"summary"}]}}
def compact_context(s):
    return {"day":s["day"],"minute":s["minute"],"weather":s["weather"],"village_brain":s["village_brain"],"npcs":s["npcs"],"traffic":s["traffic"],"recent_events":s.get("overheard",[])[-3:]}
def run_world_round(s):
    raw = provider.propose("world", compact_context(s), SHAPE)
    if raw is None:
        return None
    return {"raw": raw, "repaired": repair_world_round(raw, s)}
