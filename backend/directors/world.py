
class WorldDirector:
    """Coordinates high-level context shared by domain Directors."""

    def context(self, world_state):
        return {
            "day": world_state["day"],
            "minute": world_state["minute"],
            "village_brain": world_state["village_brain"],
            "weather": world_state["weather"],
            "recent_events": world_state.get("day_events", [])[-5:],
        }

    def domain_context(self, world_state, domain):
        base = self.context(world_state)
        if domain == "npc":
            base["npcs"] = world_state.get("npcs", {})
        elif domain == "traffic":
            base["traffic"] = world_state.get("traffic", {})
        return base
