
from backend.ai.provider import provider

SCHEMAS = {
    "weather": {
        "state": "one of: clear, soft_overcast, light_rain, heavy_rain, mist, snow, storm",
        "label": "short display label",
        "temperature_c": "integer -10 to 35",
        "wind": "short wind description"
    },
    "npc": {
        "changes": [
            {"npc": "existing npc id", "activity": "short activity", "destination": "existing location id or empty"}
        ]
    },
    "traffic": {
        "changes": [
            {"vehicle": "existing vehicle id", "activity": "short activity", "destination": "existing location id or away"}
        ]
    },
    "conversation": {
        "interactions": [
            {"participants": ["npc id", "npc id"], "topic": "short topic", "summary": "short summary"}
        ]
    }
}

def run_director(director, world_state):
    context = director.build_context(world_state)
    proposal = provider.propose(director.name, context, SCHEMAS.get(director.name, {}))
    if proposal is None:
        return None
    validated = director.validate(proposal)
    validated["_ai_trace"] = {
        "director": director.name,
        "proposal": proposal
    }
    return validated
