
from .base import Director

class TrafficDirector(Director):
    name = "traffic"

    def build_context(self, world_state):
        return {
            "minute": world_state["minute"],
            "weather": world_state["weather"],
            "village_brain": world_state["village_brain"],
            "traffic": world_state.get("traffic", {}),
        }

    def fallback_proposal(self, context):
        return {"changes": []}

    def validate(self, proposal):
        changes = proposal.get("changes", [])
        if not isinstance(changes, list):
            return self.fallback_proposal({})
        clean = []
        for item in changes[:6]:
            if isinstance(item, dict) and "vehicle" in item and "activity" in item:
                clean.append({
                    "vehicle": str(item["vehicle"]),
                    "activity": str(item["activity"])[:160],
                    "destination": str(item.get("destination", ""))[:80],
                })
        return {"changes": clean}
