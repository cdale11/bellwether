"""Journey-depth model for Bellwether v0.6.1.

Travel remains deterministic-authoritative: route state, timing, familiarity and
encounter eligibility are computed by the engine. Future AI may choose among
validated encounter candidates but may not invent routes or movement.
"""
from copy import deepcopy
import random

class TravelModel:
    SCHEMA_VERSION = 1
    BAD_WEATHER = {"heavy_rain", "storm", "snow", "heavy_snow", "fog"}

    def runtime_defaults(self):
        return {
            "schema_version": self.SCHEMA_VERSION,
            "routes": {},
            "journey_log": [],
            "total_journeys": 0,
            "total_minutes_travelling": 0,
            "shortcuts": [],
        }

    def migrate(self, state):
        travel = state.setdefault("travel", self.runtime_defaults())
        defaults = self.runtime_defaults()
        for key, value in defaults.items():
            travel.setdefault(key, deepcopy(value))
        return travel

    @staticmethod
    def route_key(origin, target):
        return "::".join(sorted((origin, target)))

    def route_state(self, state, origin, target):
        travel = self.migrate(state)
        key = self.route_key(origin, target)
        return travel["routes"].setdefault(key, {
            "journeys": 0,
            "familiarity": 0,
            "condition": "normal",
            "last_travelled_day": None,
            "first_observation_seen": False,
        })

    def weather_multiplier(self, state, origin, target, world):
        weather = state.get("weather", {}).get("state", "clear")
        exposure = {world[origin].get("weather_exposure"), world[target].get("weather_exposure")}
        if weather in {"storm", "heavy_snow"}: return 1.50
        if weather in {"heavy_rain", "snow"}: return 1.30 if "exposed" in exposure else 1.18
        if weather == "fog": return 1.22
        if weather in {"rain", "showers"}: return 1.12 if "exposed" in exposure else 1.06
        return 1.0

    def condition_multiplier(self, route):
        return {"good": .95, "normal": 1.0, "muddy": 1.18, "flooded": 1.45, "icy": 1.35}.get(route.get("condition"), 1.0)

    def plan(self, state, origin, target, world):
        route = self.route_state(state, origin, target)
        base = int(world[origin]["travel_minutes"])
        familiarity = int(route.get("familiarity", 0))
        familiar_discount = min(.18, familiarity * .02)
        minutes = max(5, round(base * self.weather_multiplier(state, origin, target, world) * self.condition_multiplier(route) * (1 - familiar_discount)))
        return {"route_key": self.route_key(origin, target), "minutes": minutes, "base_minutes": base, "familiarity": familiarity, "condition": route.get("condition", "normal")}

    def first_observation(self, origin, target):
        key = frozenset((origin, target))
        observations = {
            frozenset(("village_green", "field_lane")): "Beyond the last houses, the hedges close around the lane and the village disappears faster than expected.",
            frozenset(("field_lane", "calder_farm")): "The farm announces itself first by sound: machinery, rooks, and the irregular complaints of livestock.",
            frozenset(("field_lane", "north_woods")): "The temperature drops beneath the first trees, and the lane's open sky narrows to a green corridor.",
            frozenset(("north_woods", "old_quarry")): "Pale stone begins appearing between roots before the woodland opens abruptly onto the old workings.",
            frozenset(("calder_farm", "old_quarry")): "The rough track climbs past neglected fencing until farm mud gives way to pale limestone dust.",
            frozenset(("old_quarry", "quarry_caves")): "The air cools sharply near the cave mouth; sounds from the quarry seem to stop at the threshold.",
            frozenset(("village_green", "riverside_path")): "The village noise thins downhill until moving water becomes the clearest sound.",
            frozenset(("riverside_path", "railway_halt")): "The meadow path runs beside the railway embankment before the small platform comes into view.",
        }
        return observations.get(key, "The journey gives you a clearer sense of how this part of Bellwether fits together.")

    def encounter(self, state, origin, target):
        # Seeded from authoritative state so tests and saved histories are reproducible.
        day = int(state.get("day", 1)); minute = int(state.get("minute", 0))
        seed = f"{day}:{minute}:{origin}:{target}:{self.route_state(state, origin, target).get('journeys',0)}"
        rng = random.Random(seed)
        candidates=[]
        for npc_id, npc in state.get("npcs", {}).items():
            if npc.get("visible") and npc.get("location") in {origin, target}:
                candidates.append({"type":"npc_glimpse", "npc_id":npc_id, "text":f"On the way, you catch sight of {npc.get('name', npc_id)} moving through the same part of the village."})
        weather=state.get("weather",{}).get("state","clear")
        if weather in {"rain","showers","heavy_rain"}:
            candidates.append({"type":"weather", "text":"Rain changes the journey: gutters run, leaves shine, and the ground asks for more attention."})
        ecology={"north_woods":"A sudden movement between the trees resolves into an ordinary animal before it disappears into cover.", "field_lane":"Small birds lift from the hedge ahead of you and settle again farther along.", "riverside_path":"Something breaks the river surface once, leaving widening rings behind."}
        if target in ecology: candidates.append({"type":"ecology", "text":ecology[target]})
        # Encounters are occasional and bounded; first observations are handled separately.
        if candidates and rng.random() < .38:
            return rng.choice(candidates)
        return None

    def complete(self, state, origin, target, plan):
        travel=self.migrate(state); route=self.route_state(state, origin, target)
        first = not route.get("first_observation_seen", False)
        route["journeys"] = int(route.get("journeys",0)) + 1
        route["familiarity"] = min(10, int(route.get("familiarity",0)) + 1)
        route["last_travelled_day"] = int(state.get("day",1))
        route["first_observation_seen"] = True
        travel["total_journeys"] += 1
        travel["total_minutes_travelling"] += int(plan["minutes"])
        entry={"day":state.get("day"), "minute":state.get("minute"), "origin":origin, "target":target, "minutes":plan["minutes"], "route_key":plan["route_key"]}
        travel["journey_log"].append(entry); travel["journey_log"] = travel["journey_log"][-80:]
        return first

TRAVEL_MODEL = TravelModel()
