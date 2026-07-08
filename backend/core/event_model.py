"""Part 7 dynamic village events and consequence substrate.

Authored event definitions describe bounded triggers and consequences. Runtime state
tracks schedules, active/completed events and reversible overlays. Events are applied
through existing world, economy, job and NPC state rather than a parallel minigame.
"""
from copy import deepcopy

EVENTS = {
    "late_delivery": {
        "name": "Late Village Delivery",
        "duration_minutes": 240,
        "locations": ["village_shop", "village_road"],
        "description": "The shop delivery is running late, leaving several ordinary shelves thin until the van arrives.",
        "world_modifiers": {"village_shop": "thin_stock", "village_road": "delivery_delayed"},
    },
    "green_workday": {
        "name": "Village Green Workday",
        "duration_minutes": 300,
        "locations": ["village_green"],
        "description": "A loose village work party has gathered on the green for pruning, sweeping and small repairs.",
        "world_modifiers": {"village_green": "community_workday"},
    },
    "bakery_oven_repair": {
        "name": "Bakery Oven Repair",
        "duration_minutes": 180,
        "locations": ["bakery"],
        "description": "One of the bakery ovens needs attention. Production is reduced and the morning helper shift is suspended for repairs.",
        "world_modifiers": {"bakery": "reduced_production"},
        "blocked_jobs": ["bakery_helper"],
    },
}

class EventModel:
    def runtime_defaults(self):
        return {
            "schema_version": 1,
            "active": {},
            "completed": [],
            "event_history": [],
            "last_schedule_day": 0,
            "scheduled": [],
            "counter": 0,
        }

    def _absolute_minute(self, state):
        return (int(state.get("day", 1)) - 1) * 1440 + int(state.get("minute", 0))

    def schedule_day(self, state):
        """Create bounded ordinary events from current shared state.

        Scheduling is deterministic from day/season/weather state so save/load remains
        stable. Natural variation still comes from changing weather and seasonal state.
        """
        rt = state.setdefault("dynamic_events", self.runtime_defaults())
        day = int(state.get("day", 1))
        if rt.get("last_schedule_day", 0) >= day:
            return
        rt["last_schedule_day"] = day
        weather = state.get("weather", {}).get("state", "")
        season = state.get("season", {}).get("id", "")
        candidates = []
        if day >= 2 and ("rain" in weather or day % 4 == 0):
            candidates.append(("late_delivery", 600))
        if day >= 2 and day % 3 == 0 and "winter" not in season:
            candidates.append(("green_workday", 660))
        if day >= 3 and day % 5 == 0:
            candidates.append(("bakery_oven_repair", 450))
        known={(x["event_id"],x["day"]) for x in rt.get("scheduled",[])}
        for event_id, minute in candidates:
            if (event_id, day) not in known:
                rt["scheduled"].append({"event_id":event_id,"day":day,"minute":minute})

    def start(self, state, event_id, *, duration_minutes=None):
        if event_id not in EVENTS:
            return False, "Unknown event."
        rt = state.setdefault("dynamic_events", self.runtime_defaults())
        if event_id in rt["active"]:
            return False, "Event already active."
        spec = EVENTS[event_id]
        now = self._absolute_minute(state)
        duration = int(duration_minutes or spec["duration_minutes"])
        rt["counter"] += 1
        inst = {
            "instance_id": f"{event_id}:{rt['counter']}", "event_id": event_id,
            "start_day": state.get("day",1), "start_minute": state.get("minute",0),
            "start_absolute": now, "end_absolute": now + duration,
        }
        rt["active"][event_id] = inst
        for loc, modifier in spec.get("world_modifiers", {}).items():
            mods=state.setdefault("world_model",{}).setdefault("location_modifiers",{}).setdefault(loc,[])
            token=f"event:{event_id}:{modifier}"
            if token not in mods: mods.append(token)
        # Concrete economy consequence: a delayed delivery makes selected stock scarce.
        if event_id == "late_delivery":
            stock=state.setdefault("economy",{}).setdefault("shop_stock",{}).setdefault("village_shop",{})
            for iid in ("radish_seed","carrot_seed","groceries","repair_supplies"):
                stock[iid]=min(int(stock.get(iid,0)), 1)
        # NPCs respond through existing authoritative activity state.
        if event_id == "green_workday":
            for npc_id in ("mara","mrs_ellis"):
                npc=state.get("npcs",{}).get(npc_id)
                if npc:
                    npc["activity"]="helping with the village green workday"
        rt["event_history"].append({"kind":"started","event_id":event_id,"day":state.get("day"),"minute":state.get("minute")})
        rt["event_history"]=rt["event_history"][-80:]
        return True, spec["description"]

    def end(self, state, event_id):
        rt=state.setdefault("dynamic_events",self.runtime_defaults())
        inst=rt.get("active",{}).pop(event_id,None)
        if not inst:return False
        spec=EVENTS[event_id]
        for loc in spec.get("world_modifiers",{}):
            mods=state.setdefault("world_model",{}).setdefault("location_modifiers",{}).setdefault(loc,[])
            mods[:]=[m for m in mods if not m.startswith(f"event:{event_id}:")]
        if event_id == "late_delivery":
            stock=state.setdefault("economy",{}).setdefault("shop_stock",{}).setdefault("village_shop",{})
            for iid in ("radish_seed","carrot_seed","groceries","repair_supplies"):
                stock[iid]=max(int(stock.get(iid,0)), 8)
        rt["completed"].append(inst);rt["completed"]=rt["completed"][-40:]
        rt["event_history"].append({"kind":"ended","event_id":event_id,"day":state.get("day"),"minute":state.get("minute")})
        return True

    def advance(self, state):
        self.schedule_day(state)
        rt=state.setdefault("dynamic_events",self.runtime_defaults())
        now=self._absolute_minute(state)
        messages=[]
        pending=[]
        for item in rt.get("scheduled",[]):
            when=(int(item["day"])-1)*1440+int(item["minute"])
            if when <= now and item["event_id"] not in rt["active"]:
                ok,msg=self.start(state,item["event_id"])
                if ok: messages.append(("start",item["event_id"],msg))
            else: pending.append(item)
        rt["scheduled"]=pending
        for event_id,inst in list(rt.get("active",{}).items()):
            if now >= int(inst["end_absolute"]):
                self.end(state,event_id);messages.append(("end",event_id,f"{EVENTS[event_id]['name']} has ended; ordinary routines begin to settle back into place."))
        return messages

    def job_available(self,state,job_id):
        rt=state.get("dynamic_events",{})
        for event_id in rt.get("active",{}):
            if job_id in EVENTS[event_id].get("blocked_jobs",[]): return False
        return True

    def location_context(self,state,location_id):
        out=[]
        for event_id in state.get("dynamic_events",{}).get("active",{}):
            spec=EVENTS[event_id]
            if location_id in spec.get("locations",[]): out.append({"id":event_id,"name":spec["name"],"description":spec["description"]})
        return out

EVENT_MODEL=EventModel()
