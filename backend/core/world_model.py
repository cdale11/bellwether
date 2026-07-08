"""Part 1 world substrate.

Loads authored location data and exposes bounded queries for travel, access,
location suitability, ecology hooks, economy hooks, and future Directors.
The legacy WORLD shape remains available so frozen v0.1.0 callers keep working.
"""
from collections import deque
from copy import deepcopy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORLD_DATA_PATH = ROOT / "content" / "world" / "locations.json"

class WorldModel:
    REQUIRED_LOCATION_FIELDS = {
        "name", "description", "district", "kind", "interior", "ownership",
        "access", "weather_exposure", "seasonal_access", "services",
        "activity_tags", "npc_suitability", "story_tags", "investigation_tags",
        "ecology_tags", "future_job_tags", "future_economy_tags", "exits",
        "travel_minutes",
    }

    def __init__(self, path=WORLD_DATA_PATH):
        self.path = Path(path)
        self.data = json.loads(self.path.read_text(encoding="utf-8"))
        self.schema_version = int(self.data.get("schema_version", 1))
        self.districts = self.data["districts"]
        self.locations = self.data["locations"]
        self.npc_adjacency = {k: set(v) for k, v in self.data.get("npc_adjacency", {}).items()}
        self.validate()

    def validate(self):
        errors = []
        for loc_id, loc in self.locations.items():
            missing = self.REQUIRED_LOCATION_FIELDS - set(loc)
            if missing:
                errors.append(f"{loc_id}: missing {sorted(missing)}")
            if loc.get("district") not in self.districts:
                errors.append(f"{loc_id}: unknown district {loc.get('district')}")
            for target in loc.get("exits", {}).values():
                if target not in self.locations:
                    errors.append(f"{loc_id}: exit targets unknown location {target}")
            if not isinstance(loc.get("travel_minutes"), int) or loc.get("travel_minutes", 0) <= 0:
                errors.append(f"{loc_id}: travel_minutes must be a positive integer")
        for origin, targets in self.npc_adjacency.items():
            if origin not in self.locations:
                errors.append(f"npc adjacency origin unknown: {origin}")
            for target in targets:
                if target not in self.locations:
                    errors.append(f"npc adjacency target unknown: {origin}->{target}")
        if errors:
            raise ValueError("Invalid world data: " + "; ".join(errors))
        return True

    def location(self, location_id):
        return self.locations[location_id]

    def district(self, location_id):
        return self.districts[self.location(location_id)["district"]]

    def player_neighbors(self, location_id):
        return set(self.location(location_id)["exits"].values())

    def npc_neighbors(self, location_id):
        return set(self.npc_adjacency.get(location_id, set()))

    def npc_transition_valid(self, origin, destination):
        return destination == origin or destination in self.npc_neighbors(origin)

    def access_status(self, location_id, minute, *, is_owner=False, invited=False):
        loc = self.location(location_id)
        access = loc["access"]
        if access == "public":
            return True, "public"
        if access == "owner":
            return (is_owner or invited), "owner_or_invited"
        if access == "opening_hours":
            hours = loc.get("opening_hours", {})
            return hours.get("open_minute", 0) <= minute < hours.get("close_minute", 1440), "opening_hours"
        return invited, access

    def suitability(self, location_id, *, purpose=None, role=None):
        loc = self.location(location_id)
        score = 0
        reasons = []
        if purpose and purpose in loc["activity_tags"]:
            score += 3; reasons.append("activity_match")
        if purpose and purpose in loc["services"]:
            score += 4; reasons.append("service_match")
        if role and role in loc["npc_suitability"]:
            score += 2; reasons.append("role_match")
        return {"score": score, "reasons": reasons}

    def shortest_player_route(self, origin, destination):
        if origin == destination:
            return [origin]
        queue = deque([(origin, [origin])]); seen = {origin}
        while queue:
            node, path = queue.popleft()
            for nxt in self.player_neighbors(node):
                if nxt in seen:
                    continue
                if nxt == destination:
                    return path + [nxt]
                seen.add(nxt); queue.append((nxt, path + [nxt]))
        return None

    def runtime_state_defaults(self):
        return {
            "schema_version": self.schema_version,
            "location_modifiers": {loc_id: [] for loc_id in self.locations},
            "access_overrides": {},
            "seasonal_closures": {},
            "supernatural_overlays": {},
        }

    def public_location_context(self, location_id):
        loc = self.location(location_id)
        return {
            "district": {"id": loc["district"], **deepcopy(self.district(location_id))},
            "kind": loc["kind"],
            "interior": loc["interior"],
            "ownership": loc["ownership"],
            "access": loc["access"],
            "weather_exposure": loc["weather_exposure"],
            "seasonal_access": loc["seasonal_access"],
            "services": deepcopy(loc["services"]),
            "activity_tags": deepcopy(loc["activity_tags"]),
            "ecology_tags": deepcopy(loc["ecology_tags"]),
        }

WORLD_MODEL = WorldModel()
WORLD = WORLD_MODEL.locations
