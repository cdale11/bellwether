
from .base import Director

class NPCDirector(Director):
    name = "npc"

    def build_context(self, world_state):
        return {
            "minute": world_state["minute"],
            "weather": world_state["weather"],
            "village_brain": world_state["village_brain"],
            "npcs": world_state.get("npcs", {}),
        }

    def fallback_proposal(self, context):
        return {"changes": []}

    def validate(self, proposal):
        changes = proposal.get("changes", [])
        if not isinstance(changes, list):
            return self.fallback_proposal({})
        clean = []
        for change in changes[:8]:
            if isinstance(change, dict) and {"npc", "activity"} <= set(change):
                clean.append({
                    "npc": str(change["npc"]),
                    "activity": str(change["activity"])[:160],
                    "destination": str(change.get("destination", ""))[:80],
                })
        return {"changes": clean}
