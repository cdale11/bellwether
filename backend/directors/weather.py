
from .base import Director

ALLOWED = {"clear", "soft_overcast", "light_rain", "heavy_rain", "mist"}

class WeatherDirector(Director):
    name = "weather"

    def build_context(self, world_state):
        return {
            "day": world_state["day"],
            "minute": world_state["minute"],
            "current_weather": world_state["weather"],
            "village_brain": world_state["village_brain"],
        }

    def fallback_proposal(self, context):
        return {
            "state": "soft_overcast",
            "label": "Soft overcast",
            "temperature_c": 14,
            "wind": "light",
        }

    def validate(self, proposal):
        if proposal.get("state") not in ALLOWED:
            return self.fallback_proposal({})
        return {
            "state": proposal["state"],
            "label": str(proposal.get("label", proposal["state"].replace("_", " ").title())),
            "temperature_c": max(-10, min(35, int(proposal.get("temperature_c", 14)))),
            "wind": str(proposal.get("wind", "light")),
        }
