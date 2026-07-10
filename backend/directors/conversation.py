
from .base import Director

class ConversationDirector(Director):
    name = "conversation"

    def build_context(self, world_state):
        return {
            "minute": world_state["minute"],
            "weather": world_state["weather"],
            "village_brain": world_state["village_brain"],
            "npcs": world_state.get("npcs", {}),
            "recent_social_events": world_state.get("overheard", [])[-6:],
        }

    def fallback_proposal(self, context):
        return {"interactions": []}

    def validate(self, proposal):
        interactions = proposal.get("interactions", [])
        if not isinstance(interactions, list):
            return self.fallback_proposal({})
        clean = []
        for item in interactions[:5]:
            if isinstance(item, dict) and "participants" in item and "topic" in item:
                clean.append({
                    "participants": list(item["participants"])[:3],
                    "topic": str(item["topic"])[:100],
                    "summary": str(item.get("summary", ""))[:220],
                })
        return {"interactions": clean}
