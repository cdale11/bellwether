
from copy import deepcopy
from datetime import datetime
import json
import os
import random
import time
from pathlib import Path
from backend.directors.hub import hub
from backend.ai.provider import provider
from backend.ai.specific_directors import run_specific_round, npc_transition_is_valid, traffic_transition_is_valid
import re

ROOT = Path(__file__).resolve().parents[2]
SAVE_PATH = ROOT / "saves" / "save.json"

from backend.core.world_model import WORLD, WORLD_MODEL
from backend.core.action_surface import compact as compact_action_surface
from backend.core.npc_model import NPC_MODEL
from backend.core.npc_life_model import NPC_LIFE_MODEL
from backend.core.npc_project_model import NPC_PROJECT_MODEL
from backend.core.emergent_situation_model import EMERGENT_SITUATION_MODEL
from backend.core.social_obligation_model import SOCIAL_OBLIGATION_MODEL
from backend.core.causal_history_model import CAUSAL_HISTORY_MODEL
from backend.core.presentation_ledger_model import PRESENTATION_LEDGER_MODEL
from backend.core.social_model import SOCIAL_MODEL
from backend.core.activity_model import ACTIVITY_MODEL, CROPS
from backend.core.economy_model import ECONOMY_MODEL, ITEMS, SHOPS
from backend.core.job_model import JOB_MODEL, JOBS
from backend.core.event_model import EVENT_MODEL, EVENTS
from backend.core.seasonal_model import SEASONAL_MODEL, SEASONAL_PROFILES
from backend.core.ecology_ai_model import ECOLOGY_AI_MODEL
from backend.core.world_runtime_model import WORLD_RUNTIME_MODEL
from backend.core.knowledge_model import KNOWLEDGE_MODEL
from backend.core.investigation_model import INVESTIGATION_MODEL
from backend.core.horror_model import HORROR_MODEL
from backend.core.horror_aftermath_model import HORROR_AFTERMATH_MODEL
from backend.core.interface_horror_model import INTERFACE_HORROR_MODEL
from backend.core.property_model import PROPERTY_MODEL
from backend.core.player_business_model import PLAYER_BUSINESS_MODEL
from backend.core.player_identity_model import PLAYER_IDENTITY_MODEL
from backend.core.playstyle_pacing_model import PLAYSTYLE_PACING_MODEL
from backend.core.danger_model import DANGER_MODEL
from backend.core.failure_recovery_model import FAILURE_RECOVERY_MODEL
from backend.ai.async_runtime import ASYNC_AI_RUNTIME
from backend.core.recurrence_model import RECURRENCE_MODEL
from backend.core.content_model import CONTENT_MODEL
from backend.core.memory_model import MEMORY_MODEL
from backend.core.dialogue_expression_model import DIALOGUE_EXPRESSION_MODEL
from backend.core.population_model import POPULATION_MODEL
from backend.core.social_consequence_model import SOCIAL_CONSEQUENCE_MODEL
from backend.core.relationship_life_model import RELATIONSHIP_LIFE_MODEL
from backend.core.travel_model import TRAVEL_MODEL
from backend.core.transport_model import TRANSPORT_MODEL
from backend.core.town_mind_model import TOWN_MIND_MODEL
from backend.core.interpretation_model import INTERPRETATION_MODEL
from backend.core.resistance_model import RESISTANCE_MODEL
from backend.core.cognition_model import COGNITION_MODEL
from backend.core.procedural_arc_model import PROCEDURAL_ARC_MODEL, ARC_TEMPLATES
from backend.core.quest_model import QUEST_MODEL
from backend.core.player_status_model import PLAYER_STATUS_MODEL
from backend.core.story_model import STORY_MODEL
from backend.core.narrative_expansion_model import NARRATIVE_EXPANSION_MODEL
from backend.core.story_consciousness_integration_model import STORY_CONSCIOUSNESS_INTEGRATION_MODEL
from backend.core.systemic_horror_integration_model import SYSTEMIC_HORROR_INTEGRATION_MODEL
from backend.core.ending_model import ENDING_MODEL, FAMILIES
from backend.core.postgame_model import POSTGAME_MODEL
from backend.core.life_simulation_model import LIFE_SIMULATION_MODEL
from backend.core.society_model import SOCIETY_MODEL
from backend.core.village_evolution_model import VILLAGE_EVOLUTION_MODEL
from backend.core.animal_model import ANIMAL_MODEL, SPECIES
INITIAL_STATE = {
    "location": "bus_stop",
    "day": 1,
    "minute": 550,
    "weather": {
        "state": "soft_overcast",
        "label": "Soft overcast",
        "temperature_c": 14,
        "wind": "light",
    },
    "season": {
        "id": "late_spring",
        "label": "Late spring",
        "temperature_range_c": [7, 18],
        "daylight": "longening days",
        "character": "mild, changeable, with cool mornings and occasional showers",
    },
    "village_brain": {
        "mood": "quietly_busy",
        "focus": "ordinary_routines",
        "supernatural_pressure": 0,
        "pulse_count": 0,
    },
    "simulation_scheduler": {
        "advance_active": False,
        "pending_domains": [],
        "last_director_pulse": {},
        "round_in_progress": False,
        "rounds_skipped_busy": 0
    },
    "psychological_state": {
        "unease": 0,
        "certainty": 100,
        "familiarity_disruptions": 0,
        "recent_anomalies": [],
        "last_anomaly_pulse": -999,
        "stage": "ordinary"
    },
    "branch_state": {
        "care": 0,
        "community": 0,
        "inquiry": 0,
        "avoidance": 0,
        "setbacks": [],
        "recoveries": [],
        "endgame_unlocked": False,
        "ending": None,
        "run_complete": False
    },
    "money": 24,
    "player_status": PLAYER_STATUS_MODEL.defaults(),
    "inventory": ["Eleanor's key", "Suitcase"],
    "relationships": {"jonah": 0, "mara": 0},
    "history": [
        {"speaker": "Narrator", "text": "The bus leaves you at Bellwether just after nine. Its engine noise thins along the road until the village is quiet again."},
        {"speaker": "Narrator", "text": "For now, there is the road ahead, your suitcase at your feet, and Eleanor's key in your pocket."},
    ],
    "quests": {
        "main": [
            {"id": "arrival", "title": "A House Left Waiting", "objective": "Reach Ashcroft Cottage", "done": False},
            {"id": "eleanor_letter", "title": "In Eleanor's Hand", "objective": "Read the letter waiting in the cottage", "done": False, "hidden": True},
        ],
        "side": [
            {"id": "jonah", "title": "A Warm Welcome", "objective": "Introduce yourself at the bakery", "done": False},
            {"id": "mara", "title": "The Cottage Garden", "objective": "Speak with Mara about Eleanor's garden", "done": False, "hidden": True},
        ],
    },
    "flags": {
        "met_jonah": False,
        "met_mara": False,
        "reached_cottage": False,
        "read_letter": False,
        "mara_intro_available": False,
    },
    "ambient": {
        "traffic": "The morning bus has departed.",
        "wildlife": "Blackbirds work through the wet grass.",
        "village": "Doors are opening and the first errands of the day are underway.",
    },
    "npcs": {
        "jonah": {"name": "Jonah", "location": "bakery", "activity": "baking", "visible": True},
        "mara": {"name": "Mara", "location": "ashcroft_cottage", "activity": "checking the neglected garden", "visible": False},
        "mrs_ellis": {"name": "Mrs Ellis", "location": "village_road", "activity": "walking toward the shops", "visible": True},
        "asha": {"name": "Asha Patel", "location": "village_shop", "activity": "checking the morning delivery against her ledger", "visible": True},
        "tom": {"name": "Tom Mercer", "location": "railway_halt", "activity": "checking the platform clock against the working timetable", "visible": True},
        "ruth": {"name": "Ruth Calder", "location": "churchyard", "activity": "copying a weathered inscription into a notebook", "visible": True}
    },
    "traffic": {
        "bus_7": {"name": "Route 7 bus", "location": "away", "activity": "en route to the next village"},
        "delivery_van": {"name": "Delivery van", "location": "village_road", "activity": "making morning deliveries"},
        "train": {"name": "Morning train", "location": "away", "activity": "approaching Bellwether"}
    },
    "day_events": [],
    "dialogue": None,
    "social_memory": {nid: [] for nid in NPC_MODEL.npcs},
    "conversation_sessions": {nid: [] for nid in NPC_MODEL.npcs},
    "relationships": {
        "jonah": {"affinity": 0, "familiarity": 0, "trust": 0, "talks": 0, "last_interaction": None, "impressions": []},
        "mara": {"affinity": 0, "familiarity": 0, "trust": 0, "talks": 0, "last_interaction": None, "impressions": []},
        "mrs_ellis": {"affinity": 0, "familiarity": 0, "trust": 0, "talks": 0, "last_interaction": None, "impressions": []},
        "asha": {"affinity": 0, "familiarity": 0, "trust": 0, "talks": 0, "last_interaction": None, "impressions": []},
        "tom": {"affinity": 0, "familiarity": 0, "trust": 0, "talks": 0, "last_interaction": None, "impressions": []},
        "ruth": {"affinity": 0, "familiarity": 0, "trust": 0, "talks": 0, "last_interaction": None, "impressions": []}
    },
    "overheard": [],
    "world_events": [],
    "npc_action_history": {nid: [] for nid in NPC_MODEL.npcs},
    "traffic_action_history": {"bus_7": [], "delivery_van": [], "train": []},
    "location_state": {
        "bakery": {"open": True, "staffed": True, "bread_available": True, "last_change": "09:10"},
        "village_green": {"activity_level": 0, "last_change": "09:10"},
        "village_road": {"traffic_level": 1, "last_change": "09:10"},
        "ashcroft_cottage": {"garden_progress": 0, "last_change": "09:10"},
        "village_shop": {"open": True, "activity_level": 1, "last_change": "09:10"},
        "churchyard": {"activity_level": 0, "last_change": "09:10"},
        "riverside_path": {"river_level": "normal", "activity_level": 0, "last_change": "09:10"},
        "railway_halt": {"activity_level": 0, "next_train_window": "late morning", "last_change": "09:10"}
    },
    "encounters": [],
    "location_observations": {},
    "player_life": {
        "cottage_care": 0,
        "garden_work": 0,
        "location_familiarity": {k: 0 for k in WORLD},
        "attentiveness": 0,
        "tea_breaks": 0,
        "meals": 0,
        "errands_done": 0,
        "books_read": 0,
        "activity_history": [],
        "discoveries": [],
    },
    "investigation": {
        "evidence": [],
        "leads": [],
        "place_notes": {k: [] for k in WORLD},
        "observation_counts": {k: 0 for k in WORLD},
        "connections": [],
    },
    "llm_context": {
        "schema_version": 1,
        "canon_summary": "The player has inherited Ashcroft Cottage from Eleanor and has just arrived in Bellwether. Authored story facts are authoritative; AI may add texture but never canon.",
        "story_summary": "Arrival is beginning.",
        "player_style": {
            "conversation_tendency": "unknown",
            "life_tendency": "unknown",
            "investigation_tendency": "unknown",
        },
        "notable_player_choices": [],
        "story_beats": [],
        "session_summary": [],
        "run_history": [],
        "last_compiled": None
    },
    "story_integration": {
        "unlocked_beats": [],
        "authored_signals_seen": []
    },
    "director_status": {
        "mode": "deterministic",
        "last_ai_domains": [],
        "accepted_proposals": 0
    },
    "world_model": WORLD_MODEL.runtime_state_defaults(),
    "npc_lives": NPC_MODEL.runtime_defaults(),
    "npc_autonomous_lives": NPC_LIFE_MODEL.runtime_defaults(),
    "npc_epistemic_projects": NPC_PROJECT_MODEL.runtime_defaults(),
    "social_obligations": SOCIAL_OBLIGATION_MODEL.defaults(),
    "npc_social_web": SOCIAL_MODEL.runtime_defaults(),
    "npc_knowledge": KNOWLEDGE_MODEL.runtime_defaults(list(NPC_MODEL.npcs)),
    "mystery_investigation": INVESTIGATION_MODEL.runtime_defaults(),
    "systemic_horror": HORROR_MODEL.runtime_defaults(),
    "horror_aftermath": HORROR_AFTERMATH_MODEL.runtime_defaults(),
    "interface_horror": INTERFACE_HORROR_MODEL.runtime_defaults(),
    "property": PROPERTY_MODEL.runtime_defaults(),
    "player_businesses": PLAYER_BUSINESS_MODEL.runtime_defaults(),
    "player_identity": PLAYER_IDENTITY_MODEL.runtime_defaults(),
    "danger": DANGER_MODEL.runtime_defaults(),
    "failure_recovery": FAILURE_RECOVERY_MODEL.runtime_defaults(),
    "recurrence": RECURRENCE_MODEL.runtime_defaults(),
    "content_progression": CONTENT_MODEL.runtime_defaults(),
    "life_simulation": LIFE_SIMULATION_MODEL.runtime_defaults(),
    "memory_system": MEMORY_MODEL.runtime_defaults(list(NPC_MODEL.npcs)),
    "population": POPULATION_MODEL.runtime_defaults(),
    "society": SOCIETY_MODEL.runtime_defaults(),
    "village_evolution": VILLAGE_EVOLUTION_MODEL.runtime_defaults(),
    "social_consequences": SOCIAL_CONSEQUENCE_MODEL.runtime_defaults(list(NPC_MODEL.npcs)),
    "travel": TRAVEL_MODEL.runtime_defaults(),
    "town_mind": TOWN_MIND_MODEL.runtime_defaults(),
    "interpretation_system": INTERPRETATION_MODEL.runtime_defaults(),
    "resistance": RESISTANCE_MODEL.runtime_defaults(),
    "npc_cognition": COGNITION_MODEL.runtime_defaults(list(NPC_MODEL.npcs)),
    "procedural_arcs": PROCEDURAL_ARC_MODEL.runtime_defaults(),
    "quest_runtime": {"schema_version":1,"transactions":{},"history":[],"completion_checks":0},
    "authored_story": STORY_MODEL.runtime_defaults(),
    "authored_narrative": NARRATIVE_EXPANSION_MODEL.runtime_defaults(),
    "story_consciousness_integration": STORY_CONSCIOUSNESS_INTEGRATION_MODEL.runtime_defaults(),
    "systemic_horror_integration": SYSTEMIC_HORROR_INTEGRATION_MODEL.runtime_defaults(),
    "player_activities": ACTIVITY_MODEL.runtime_defaults(),
    "cottage_animals": ANIMAL_MODEL.runtime_defaults(),
    "economy": ECONOMY_MODEL.runtime_defaults(),
    "jobs": JOB_MODEL.runtime_defaults(),
    "dynamic_events": EVENT_MODEL.runtime_defaults(),
    "seasonal_life": SEASONAL_MODEL.runtime_defaults(),
    "world_runtime": WORLD_RUNTIME_MODEL.runtime_defaults(),
    "map_exploration": {
        "schema_version": 1,
        "discovered_locations": ["bus_stop"],
        "discovered_paths": [],
    },
    "ui": {
        "message_cursor": 0
    },
    "ai_events": [],
    "ai_runtime": {
        "last_world_pulse": -999,
        "world_rounds": 0,
        "failed_rounds": 0
    },
}


SEASONS = [
    {"id":"early_spring","label":"Early spring","temperature_range_c":[2,13],"daylight":"rapidly lengthening days","character":"chilly mornings, showers, bright intervals and occasional late frost"},
    {"id":"late_spring","label":"Late spring","temperature_range_c":[7,18],"daylight":"longening days","character":"mild, changeable, with cool mornings and occasional showers"},
    {"id":"early_summer","label":"Early summer","temperature_range_c":[10,22],"daylight":"very long days","character":"mild to warm days, cool nights, showers and clear spells"},
    {"id":"high_summer","label":"High summer","temperature_range_c":[13,27],"daylight":"long days","character":"warm spells broken by cloud, rain or occasional thunderstorms"},
    {"id":"late_summer","label":"Late summer","temperature_range_c":[11,23],"daylight":"slowly shortening days","character":"warm afternoons, cooler evenings, haze and intermittent rain"},
    {"id":"early_autumn","label":"Early autumn","temperature_range_c":[7,18],"daylight":"shortening days","character":"cooler mornings, mild afternoons, mist and passing rain"},
    {"id":"late_autumn","label":"Late autumn","temperature_range_c":[3,13],"daylight":"short days","character":"damp, windy and changeable with misty mornings"},
    {"id":"early_winter","label":"Early winter","temperature_range_c":[0,10],"daylight":"very short days","character":"cold rain, grey skies, brisk wind and occasional frost"},
    {"id":"deep_winter","label":"Deep winter","temperature_range_c":[-3,8],"daylight":"very short days","character":"cold, frost-prone and damp, with rare sleet or snow"},
    {"id":"late_winter","label":"Late winter","temperature_range_c":[0,10],"daylight":"slowly lengthening days","character":"cold and unsettled with rain, frost and occasional clear bright days"},
]

class Game:
    def __init__(self):
        self.state = deepcopy(INITIAL_STATE)
        self._overview_cache_key = None
        self._overview_cache = None
        self.initialize_season()

    def initialize_season(self):
        """Ask the local model for a bounded random-feeling UK season; fall back locally."""
        print("[Bellwether] Asking the local model to choose this playthrough's season...", flush=True)
        candidates = [dict(s) for s in SEASONS]
        context = {
            "setting": "a fictional rural English village with a UK-like maritime climate",
            "purpose": "choose the opening seasonal atmosphere for a new playthrough",
            "variation_request": "Any listed season is valid. Choose freely for replay variety rather than defaulting to mild weather.",
        }
        choice = provider.ask_choice(
            "season",
            "Choose the season in which this Bellwether playthrough begins. Any option is valid; vary openings between playthroughs.",
            context,
            candidates,
        )
        selected = choice if choice else random.SystemRandom().choice(SEASONS)
        self.state["season"] = deepcopy(selected)
        source = "Qwen" if choice else "local fallback"
        # Persist startup-season evidence so repeated-run bias can be measured rather than guessed.
        try:
            season_log = Path(__file__).resolve().parents[2] / "diagnostics" / "season_selection_history.jsonl"
            season_log.parent.mkdir(exist_ok=True)
            with season_log.open("a", encoding="utf-8") as f:
                f.write(json.dumps({"ts": time.time(), "selected_id": selected.get("id"), "selected_label": selected.get("label"), "source": source, "provider_state": provider.last_status.get("state"), "provider_error": provider.last_status.get("last_error")}, default=str)+"\n")
        except Exception:
            pass
        print(f"[Bellwether] Season selected by {source}: {selected['label']}", flush=True)
        # Start at a season-appropriate 09:10 temperature.
        self.state["weather"]["temperature_c"] = self.seasonal_temperature(self.state["minute"], self.state["weather"]["state"])
        self.state["history"].insert(0, {
            "speaker": "Bellwether",
            "text": f"It is {selected['label'].lower()} in Bellwether: {selected['character']}."
        })

    def seasonal_temperature(self, minute=None, weather_state=None):
        """Deterministic diurnal baseline plus small bounded variation for UK-like seasons."""
        s = self.state
        season = s.get("season", SEASONS[1])
        low, high = season["temperature_range_c"]
        minute = s["minute"] if minute is None else minute
        hour = (minute % 1440) / 60.0
        # Coolest near dawn, warmest mid-afternoon; smooth piecewise daily cycle.
        if hour < 6:
            phase = 0.05
        elif hour < 15:
            phase = 0.05 + 0.95 * ((hour - 6) / 9)
        else:
            phase = max(0.05, 1.0 - 0.95 * ((hour - 15) / 9))
        base = low + (high - low) * phase
        offsets = {"clear": 1.5, "soft_overcast": 0, "light_rain": -1.5, "heavy_rain": -2.5, "mist": -1.0, "snow": -3.5, "storm": -4.0}
        return int(round(max(low - 2, min(high + 2, base + offsets.get(weather_state or s["weather"]["state"], 0)))))

    def update_temperature_for_time(self):
        s = self.state
        target = self.seasonal_temperature(s["minute"], s["weather"]["state"])
        current = int(s["weather"].get("temperature_c", target))
        # Temperatures move gradually instead of snapping each tick.
        if current < target: current += 1
        elif current > target: current -= 1
        s["weather"]["temperature_c"] = current

    def compile_llm_overview(self):
        """Build compact whole-playthrough metadata from authoritative state."""
        s=self.state
        cache_key=(
            s.get("day"),s.get("minute"),s.get("location"),
            len(s.get("world_events",[])),len(s.get("investigation",{}).get("evidence",[])),
            len(s.get("player_life",{}).get("activity_history",[])),
            tuple((k,v.get("location"),v.get("activity")) for k,v in s.get("npcs",{}).items()),
            s.get("psychological_state",{}).get("familiarity_disruptions",0),
            s.get("branch_state",{}).get("run_complete",False),
            len(getattr(provider,"recent_call_memory",[])),
        )
        if self._overview_cache_key == cache_key and self._overview_cache is not None:
            provider.set_overview_context(self._overview_cache)
            return self._overview_cache
        ctx=s.setdefault("llm_context", deepcopy(INITIAL_STATE["llm_context"]))
        completed=[q["title"] for group in ("main","side") for q in s["quests"][group] if q.get("done")]
        active=[{"title":q["title"],"objective":q["objective"]} for group in ("main","side")
                for q in s["quests"][group] if not q.get("done") and not q.get("hidden")]
        activities=s.get("player_life",{}).get("activity_history",[])
        counts={}
        for a in activities:
            counts[a.get("activity","unknown")]=counts.get(a.get("activity","unknown"),0)+1
        talks=sum(r.get("talks",0) for r in s.get("relationships",{}).values() if isinstance(r,dict))
        inv_count=len(s.get("investigation",{}).get("evidence",[]))
        ctx["story_summary"] = (
            f"Day {s['day']}, {self.time_label()}. Completed: {', '.join(completed) or 'none'}. "
            f"Active: {', '.join(x['title'] for x in active) or 'none'}. "
            f"Current place: {WORLD[s['location']]['name']}."
        )
        total_life=sum(counts.values())
        dominant_life=max(counts,key=counts.get) if counts else "still forming"
        branch=s.get("branch_state",{})
        ctx["player_style"]={
            "conversation_tendency": "socially engaged" if talks>=4 else "occasionally social" if talks>=1 else "reserved so far",
            "life_tendency": dominant_life,
            "routine_strength": "strongly routine-bound" if total_life>=8 and counts.get(dominant_life,0)/max(1,total_life)>=0.5 else "varied" if total_life>=4 else "still forming",
            "investigation_tendency": "highly observant" if inv_count>=6 else "curious" if inv_count>=2 else "not yet established",
            "community_orientation": "community-oriented" if branch.get("community",0)>=6 else "independent so far",
            "care_orientation": "care-focused" if branch.get("care",0)>=6 else "still forming",
        }
        ctx["player_evolving_identity"]=PLAYER_IDENTITY_MODEL.public_context(s)
        ctx["recurrence_context"]={"run_index":s.get("recurrence",{}).get("run_index",1),"fragment_ids":[x.get("id") for x in s.get("recurrence",{}).get("fragments",[])],"instinct_ids":[x.get("id") for x in s.get("recurrence",{}).get("instincts",[])]}
        ctx["world_now"]={
            "season":s.get("season"), "weather":s.get("weather"),
            "village_mood":s["village_brain"].get("mood"),
            "village_focus":s["village_brain"].get("focus"),
            "supernatural_pressure":s["village_brain"].get("supernatural_pressure"),
            "npc_positions":{nid:{"location":n.get("location"),"activity":n.get("activity")} for nid,n in s["npcs"].items()},
        }
        ctx["relationships"]={nid:{
            "affinity":r.get("affinity",0),"familiarity":r.get("familiarity",0),"trust":r.get("trust",0),
            "recent_impressions":r.get("impressions",[])[-3:]
        } for nid,r in s.get("relationships",{}).items() if isinstance(r,dict)}
        ctx["investigation_overview"]={
            "evidence_titles":[e.get("title") for e in s.get("investigation",{}).get("evidence",[])[-8:]],
            "open_leads":[l.get("title") for l in s.get("investigation",{}).get("leads",[]) if not l.get("resolved")][-6:],
        }
        ctx["recent_world_history"]=s.get("world_events",[])[-10:]
        ctx["story_beats"]=s.get("story_integration",{}).get("unlocked_beats",[])[-8:]
        ctx["branch_context"]=deepcopy(s.get("branch_state",{}))
        ctx["psychological_context"]={
            "state":deepcopy(s.get("psychological_state",{})),
            "eligibility":self.horror_eligibility(),
            "rule":"Do not invent anomalies or advance horror. React only to authored experienced anomalies listed here."
        }
        if getattr(provider, "recent_call_memory", None):
            ctx["session_summary"] = deepcopy(provider.recent_call_memory[-12:])
        ctx["last_compiled"]={"day":s["day"],"time":self.time_label()}
        # A compact detached copy is cached; repeated Director calls in the same state
        # no longer rebuild and deepcopy the full overview.
        self._overview_cache=deepcopy(ctx)
        self._overview_cache_key=cache_key
        provider.set_overview_context(self._overview_cache)
        return self._overview_cache

    def remember_player_choice(self, summary):
        ctx=self.state.setdefault("llm_context", deepcopy(INITIAL_STATE["llm_context"]))
        item={"day":self.state["day"],"time":self.time_label(),"summary":summary}
        ctx["notable_player_choices"].append(item)
        ctx["notable_player_choices"]=ctx["notable_player_choices"][-20:]

    def branch_score(self, branch, amount=1, reason=None):
        b=self.state.setdefault("branch_state",deepcopy(INITIAL_STATE["branch_state"]))
        b[branch]=max(0,b.get(branch,0)+amount)
        if reason:
            self.remember_player_choice(reason)

    def evaluate_failure_and_recovery(self):
        """Setbacks constrain choices temporarily but never silently end a run."""
        s=self.state; ps=s["psychological_state"]; b=s["branch_state"]
        if ps["unease"] >= 55 and "overwhelmed" not in b["setbacks"] and "overwhelmed" not in b["recoveries"]:
            b["setbacks"].append("overwhelmed")
            self.add("Narrator","You realise you have begun moving through Bellwether too quickly, checking and rechecking things without learning anything new.")
            self.add("Journal","Setback: Overwhelmed. Rest, return to an ordinary routine, or seek familiar company.")
        if s["money"] <= 0 and "short_of_money" not in b["setbacks"] and "short_of_money" not in b["recoveries"]:
            b["setbacks"].append("short_of_money")
            self.add("Journal","Setback: Short of money. Ordinary help and practical work can open a recovery path.")

    def recover_setback(self, method):
        s=self.state; b=s["branch_state"]; ps=s["psychological_state"]
        if method=="ground" and "overwhelmed" in b["setbacks"]:
            self.advance(30); ps["unease"]=max(0,ps["unease"]-18); ps["certainty"]=min(100,ps["certainty"]+8)
            b["setbacks"].remove("overwhelmed"); b["recoveries"].append("overwhelmed")
            self.branch_score("care",1,"Chose to slow down and recover rather than force the investigation.")
            self.add("Narrator","You let an ordinary half hour remain ordinary. By the end of it, the village has edges again.")
        elif method=="help" and "short_of_money" in b["setbacks"]:
            self.advance(40); s["money"]+=6
            b["setbacks"].remove("short_of_money"); b["recoveries"].append("short_of_money")
            self.branch_score("community",1,"Accepted practical village work to recover from being short of money.")
            self.add("Narrator","A small practical job takes most of an hour. It is unremarkable work, and the money helps.")

    def evaluate_endgame(self):
        """Unlock authored endgame only after substantial lived, social and investigative play."""
        s=self.state; b=s["branch_state"]; ps=s["psychological_state"]
        evidence=len(s["investigation"].get("evidence",[]))
        familiar=sum(1 for v in s["player_life"]["location_familiarity"].values() if v>=8)
        social=sum(r.get("familiarity",0) for r in s["relationships"].values() if isinstance(r,dict))
        ready=(s["flags"].get("read_letter") and ps["familiarity_disruptions"]>=3
               and evidence>=6 and familiar>=3 and social>=6)
        if ready and not b["endgame_unlocked"]:
            b["endgame_unlocked"]=True
            self.add("Journal","A decision is forming. Return to Ashcroft Cottage when you are ready to decide what Bellwether means to you.")
            self.record_world_event("The player's accumulated relationships, observations and experiences have opened the endgame decision.","endgame")
        return b["endgame_unlocked"]

    def resolve_ending(self, ending_id):
        """Resolve one deterministic canonical ending family after eligibility validation."""
        s=self.state; rt=ENDING_MODEL.migrate(s)
        if rt.get("resolved") or ending_id not in ENDING_MODEL.refresh(s): return False
        data=FAMILIES[ending_id]
        rt["resolved"]={"id":ending_id,"title":data["title"],"day":s["day"],"time":self.time_label(),"metrics":ENDING_MODEL.metrics(s)}
        b=s.setdefault("branch_state",{}); b["run_complete"]=True; b["ending"]=deepcopy(rt["resolved"])
        self.add("Ending",data["title"]); self.add("Narrator",data["text"])
        POSTGAME_MODEL.activate(s,ending_id)
        self.add("Journal","The central crisis has resolved, but life in Bellwether continues. Work, relationships, hobbies, farming and remaining mysteries are still yours to pursue.")
        self.record_world_event(f"Canonical ending reached: {data['title']}.","ending","player")
        self.compile_llm_overview(); return True

    def horror_eligibility(self):
        """Horror requires learned normality; time alone cannot force escalation."""
        s=self.state
        life=s["player_life"]
        familiar=sum(1 for v in life.get("location_familiarity",{}).values() if v >= 6)
        ordinary_actions=len(life.get("activity_history",[]))
        evidence=len(s["investigation"].get("evidence",[]))
        social=sum(r.get("familiarity",0) for r in s.get("relationships",{}).values() if isinstance(r,dict))
        return {
            "eligible": bool(s["flags"].get("read_letter") and ordinary_actions >= 8 and familiar >= 2),
            "ordinary_actions":ordinary_actions,
            "familiar_places":familiar,
            "evidence":evidence,
            "social_familiarity":social,
        }

    def maybe_apply_controlled_horror(self):
        """Apply one bounded systemic anomaly only after the player learned normality."""
        s=self.state; ps=s.setdefault("psychological_state",deepcopy(INITIAL_STATE["psychological_state"])); rt=s.setdefault("systemic_horror",HORROR_MODEL.runtime_defaults())
        HORROR_MODEL.expire(s)
        elig=self.horror_eligibility(); pulse=s["village_brain"]["pulse_count"]
        if not elig["eligible"] or pulse-int(rt.get("last_trigger_pulse",-999))<8: return False
        candidates=HORROR_MODEL.eligible(s)
        if not candidates:return False
        chosen=HORROR_MODEL.choose(s,candidates)
        if not chosen:return False
        event=HORROR_MODEL.apply(s,chosen)
        if not event:return False
        HORROR_AFTERMATH_MODEL.register_anomaly(s,event,list(s.get("npcs",{})),MEMORY_MODEL,COGNITION_MODEL)
        self.add("Narrator",event["text"])
        legacy={"id":event["id"],"day":s["day"],"time":self.time_label(),"location":s["location"],"summary":event["summary"],"domain":event["domain"]}
        ps["recent_anomalies"].append(legacy); ps["recent_anomalies"]=ps["recent_anomalies"][-8:]; ps["last_anomaly_pulse"]=pulse; ps["familiarity_disruptions"]+=1; ps["unease"]=min(100,ps["unease"]+6); ps["certainty"]=max(0,ps["certainty"]-3); ps["stage"]="first_doubts" if ps["familiarity_disruptions"]<3 else "pattern_doubt"
        s["village_brain"]["supernatural_pressure"]=min(20,ps["familiarity_disruptions"]*3)
        self.record_world_event(event["summary"],"systemic_anomaly",event["id"])
        return True

    def evaluate_danger(self):
        """Evaluate bounded causal hazards after world/horror state changes."""
        s=self.state; rt=s.setdefault("danger",DANGER_MODEL.runtime_defaults())
        if rt.get("status") != "alive": return False
        candidates=DANGER_MODEL.eligible(s)
        if not candidates: return False
        hid=candidates[0]
        # First exposure teaches the warning; repeated risky presence can cause harm.
        if hid not in rt.get("warnings_seen",[]):
            warning=DANGER_MODEL.warn(s,hid); self.add("Narrator",warning); return False
        event=DANGER_MODEL.apply(s,hid)
        if not event:return False
        self.add("Narrator",event["text"])
        if event["fatal"]:
            self.add("Journal","This run has ended. Bellwether will remember that it happened, even if the next run does not remember cleanly.")
            self.record_world_event(f"Player death: {event['id']}","player_death",event["id"])
        else:
            self.add("Journal",f"Injury: {DANGER_MODEL.injuries[event['injury']]['label']}.")
            self.record_world_event(f"Player injured: {event['injury']}","player_injury",event["id"])
        return True

    def treat_injury(self):
        iid=DANGER_MODEL.treat(self.state)
        if not iid:
            self.add("Narrator","You have no untreated injury that needs attention."); return False
        self.add("Narrator",f"You clean, bind and rest the {DANGER_MODEL.injuries[iid]['label'].lower()}. Recovery will still take time.")
        self.advance(30); return True

    def evaluate_story_integration(self):
        """Unlock authored connective beats from simulation state; AI cannot create canon."""
        s=self.state
        integ=s.setdefault("story_integration",{"unlocked_beats":[],"authored_signals_seen":[]})
        seen=integ["authored_signals_seen"]
        def unlock(key, summary, speaker=None, text=None):
            if key in seen:return
            seen.append(key)
            integ["unlocked_beats"].append({"id":key,"day":s["day"],"time":self.time_label(),"summary":summary})
            if text:self.add(speaker or "Narrator",text)
            self.record_world_event(summary,"story_integration")
        if s["flags"].get("read_letter") and s["player_life"].get("cottage_care",0)>=16:
            unlock("cottage_becoming_home","The player has begun turning Ashcroft Cottage into a lived-in home.",
                   "Narrator","The cottage no longer feels merely opened. Your routines have begun to leave their own shape in the rooms.")
        if s["flags"].get("met_mara") and s["location_state"]["ashcroft_cottage"].get("garden_progress",0)>=10:
            unlock("garden_shared_work","The Ashcroft garden is becoming a shared project shaped by the player and Mara.",
                   "Narrator","The garden now bears signs of more than one pair of hands. The work has become a quiet form of conversation.")
        if s["flags"].get("read_letter") and len(s["investigation"].get("evidence",[]))>=5:
            unlock("player_pattern_seeker","The player has begun actively connecting observations around Bellwether.",
                   "Notebook","You have enough separate observations now that Bellwether is beginning to feel less like scenery and more like a set of patterns.")
        if s["flags"].get("read_letter") and s["weather"].get("state")=="heavy_rain" and s["location"]=="ashcroft_cottage":
            unlock("first_storm_at_ashcroft","The player experienced heavy rain at Ashcroft Cottage after reading Eleanor's letter.",
                   "Narrator","Rain works across the cottage in layers: roof, glass, gutter, leaves. For a while, every sound has an ordinary source.")
        for scene in NARRATIVE_EXPANSION_MODEL.evaluate(s):
            self.add(scene["speaker"], scene["text"])
            self.record_world_event(f"Authored narrative scene: {scene['id']}", "authored_narrative")
            STORY_CONSCIOUSNESS_INTEGRATION_MODEL.record_authored_signal(s, scene["id"], scene["chapter"])
        story_step=STORY_MODEL.advance_if_ready(s)
        if story_step:
            self.add("Story", story_step["text"])
            if story_step.get("next"):
                nxt=STORY_MODEL.current(s)
                self.add("Journal", f"Main Story added: {nxt['title']} — {nxt['objective']}")
            elif story_step.get("ending_eligible"):
                self.add("Journal", "The central story has reached ending eligibility. The ending families are reserved for v1.0 RC2.")
            self.record_world_event(f"Authored story gate completed: {story_step['completed']}","authored_story")
        self.compile_llm_overview()

    def time_label(self):
        m = self.state["minute"]
        return f"{(m // 60) % 24:02d}:{m % 60:02d}"

    def visible_quests(self, group):
        return [q for q in self.state["quests"][group] if not q.get("hidden", False)]

    def migrate_state(self):
        """Make older Part 6 saves compatible with this build."""
        self.state.setdefault("ui", {"message_cursor": 0})
        map_state = self.state.setdefault("map_exploration", deepcopy(INITIAL_STATE["map_exploration"]))
        map_state.setdefault("schema_version", 1)
        map_state.setdefault("discovered_locations", [])
        map_state.setdefault("discovered_paths", [])
        current_location = self.state.get("location", "bus_stop")
        if current_location not in map_state["discovered_locations"]:
            map_state["discovered_locations"].append(current_location)
        self.state.setdefault("world_model", WORLD_MODEL.runtime_state_defaults())
        self.state.setdefault("npc_lives", NPC_MODEL.runtime_defaults())
        NPC_LIFE_MODEL.migrate(self.state)
        self.state.setdefault("npcs", {})
        for npc_id, npc_defaults in INITIAL_STATE["npcs"].items():
            self.state["npcs"].setdefault(npc_id, deepcopy(npc_defaults))
        QUEST_MODEL.migrate(self.state)
        PRESENTATION_LEDGER_MODEL.migrate(self.state)
        CAUSAL_HISTORY_MODEL.migrate(self.state)
        PLAYER_STATUS_MODEL.migrate(self.state)
        self.state.setdefault("npc_social_web", SOCIAL_MODEL.runtime_defaults())
        self.state.setdefault("npc_knowledge", KNOWLEDGE_MODEL.runtime_defaults(list(self.state.get("npcs",{}))))
        self.state.setdefault("mystery_investigation", INVESTIGATION_MODEL.runtime_defaults())
        INVESTIGATION_MODEL.refresh(self.state["mystery_investigation"])
        HORROR_MODEL.migrate(self.state)
        HORROR_AFTERMATH_MODEL.migrate(self.state)
        INTERFACE_HORROR_MODEL.migrate(self.state)
        PROPERTY_MODEL.migrate(self.state)
        PLAYER_BUSINESS_MODEL.migrate(self.state)
        self.state.setdefault("player_identity", PLAYER_IDENTITY_MODEL.runtime_defaults())
        self.state.setdefault("danger", DANGER_MODEL.runtime_defaults())
        FAILURE_RECOVERY_MODEL.migrate(self.state)
        self.state.setdefault("recurrence", RECURRENCE_MODEL.runtime_defaults())
        self.state.setdefault("content_progression", CONTENT_MODEL.runtime_defaults())
        MEMORY_MODEL.migrate(self.state, list(self.state.get("npcs",{})))
        COGNITION_MODEL.migrate(self.state, list(self.state.get("npcs",{})))
        COGNITION_MODEL.bootstrap_authoritative_context(self.state, NPC_MODEL, KNOWLEDGE_MODEL)
        PROCEDURAL_ARC_MODEL.migrate(self.state)
        STORY_MODEL.migrate(self.state)
        NARRATIVE_EXPANSION_MODEL.migrate(self.state)
        STORY_CONSCIOUSNESS_INTEGRATION_MODEL.migrate(self.state)
        SYSTEMIC_HORROR_INTEGRATION_MODEL.migrate(self.state)
        ENDING_MODEL.migrate(self.state)
        POSTGAME_MODEL.migrate(self.state)
        POPULATION_MODEL.migrate(self.state)
        SOCIAL_CONSEQUENCE_MODEL.migrate(self.state, list(self.state.get("npcs",{})))
        RELATIONSHIP_LIFE_MODEL.migrate(self.state)
        TRAVEL_MODEL.migrate(self.state)
        TRANSPORT_MODEL.migrate(self.state)
        CONTENT_MODEL.migrate_v040(self.state)
        LIFE_SIMULATION_MODEL.migrate(self.state)
        SOCIETY_MODEL.migrate(self.state)
        VILLAGE_EVOLUTION_MODEL.migrate(self.state)
        RECURRENCE_MODEL.migrate(self.state["recurrence"])
        self.state.setdefault("player_activities", ACTIVITY_MODEL.runtime_defaults())
        ACTIVITY_MODEL.migrate(self.state)
        self.state.setdefault("economy", ECONOMY_MODEL.runtime_defaults())
        self.state.setdefault("jobs", JOB_MODEL.runtime_defaults())
        ECONOMY_MODEL.migrate(self.state)
        JOB_MODEL.migrate(self.state)
        self.state.setdefault("dynamic_events", EVENT_MODEL.runtime_defaults())
        self.state.setdefault("seasonal_life", SEASONAL_MODEL.runtime_defaults())
        WORLD_RUNTIME_MODEL.migrate(self.state)
        econ_defaults=ECONOMY_MODEL.runtime_defaults()
        for key,value in econ_defaults.items():
            self.state["economy"].setdefault(key,deepcopy(value))
        social_defaults=SOCIAL_MODEL.runtime_defaults()
        for edge_id, defaults in social_defaults.items():
            edge=self.state["npc_social_web"].setdefault(edge_id,deepcopy(defaults))
            for key,value in defaults.items(): edge.setdefault(key,deepcopy(value))
            for dim,value in defaults["state"].items(): edge.setdefault("state",{}).setdefault(dim,value)
        npc_life_defaults=NPC_MODEL.runtime_defaults()
        for npc_id, defaults in npc_life_defaults.items():
            life=self.state["npc_lives"].setdefault(npc_id,deepcopy(defaults))
            for key,value in defaults.items():
                life.setdefault(key,deepcopy(value))
            for need,value in defaults["needs"].items():
                life.setdefault("needs",{}).setdefault(need,value)
        world_state = self.state["world_model"]
        defaults = WORLD_MODEL.runtime_state_defaults()
        for key, value in defaults.items():
            world_state.setdefault(key, deepcopy(value))
        for loc_id in WORLD:
            world_state.setdefault("location_modifiers", {}).setdefault(loc_id, [])
        self.state.setdefault("social_memory", {})
        for npc_id in self.state.get("npcs", {}):
            memories=self.state["social_memory"].setdefault(npc_id, [])
            self.state["social_memory"][npc_id]=memories[-40:]
        # Mara becomes physically available once Eleanor's letter opens her side story.
        if self.state.get("flags", {}).get("mara_intro_available") or self.state.get("flags", {}).get("met_mara"):
            self.state.setdefault("npcs", {}).setdefault("mara", deepcopy(INITIAL_STATE["npcs"]["mara"]))["visible"] = True
        self.state.setdefault("relationships", deepcopy(INITIAL_STATE["relationships"]))
        for npc_id, defaults in INITIAL_STATE["relationships"].items():
            rel = self.state["relationships"].setdefault(npc_id, deepcopy(defaults))
            for key, value in defaults.items():
                rel.setdefault(key, deepcopy(value))
        self.state.setdefault("overheard", [])
        self.state.setdefault("world_events", [])
        self.state.setdefault("npc_action_history", {k: [] for k in self.state.get("npcs", {})})
        self.state.setdefault("traffic_action_history", {k: [] for k in self.state.get("traffic", {})})
        self.state.setdefault("season", deepcopy(INITIAL_STATE["season"]))
        self.state.setdefault("location_state", deepcopy(INITIAL_STATE["location_state"]))
        for loc_id, defaults in INITIAL_STATE["location_state"].items():
            place = self.state["location_state"].setdefault(loc_id, deepcopy(defaults))
            for key, value in defaults.items():
                place.setdefault(key, deepcopy(value))
        # Expansion locations receive generic persistent place state on both new and migrated saves.
        for loc_id in WORLD:
            self.state["location_state"].setdefault(loc_id, {"activity_level": 0, "last_change": self.time_label()})
        self.state.setdefault("conversation_sessions", deepcopy(INITIAL_STATE["conversation_sessions"]))
        for npc_id in self.state.get("npcs", {}):
            self.state["conversation_sessions"].setdefault(npc_id, [])
        self.state.setdefault("encounters", [])
        self.state["encounters"] = self.state["encounters"][-30:]
        self.state.setdefault("location_observations", {})
        self.state.setdefault("player_life", deepcopy(INITIAL_STATE["player_life"]))
        life = self.state["player_life"]
        for key, value in INITIAL_STATE["player_life"].items():
            life.setdefault(key, deepcopy(value))
        for loc_id in WORLD:
            life.setdefault("location_familiarity", {}).setdefault(loc_id, 0)
        self.state.setdefault("investigation", deepcopy(INITIAL_STATE["investigation"]))
        self.state.setdefault("llm_context", deepcopy(INITIAL_STATE["llm_context"]))
        self.state.setdefault("story_integration", deepcopy(INITIAL_STATE["story_integration"]))
        self.state.setdefault("simulation_scheduler", deepcopy(INITIAL_STATE["simulation_scheduler"]))
        self.state.setdefault("psychological_state", deepcopy(INITIAL_STATE["psychological_state"]))
        self.state.setdefault("branch_state", deepcopy(INITIAL_STATE["branch_state"]))
        inv = self.state["investigation"]
        for key, value in INITIAL_STATE["investigation"].items():
            inv.setdefault(key, deepcopy(value))
        for loc_id in WORLD:
            inv.setdefault("place_notes", {}).setdefault(loc_id, [])
            inv.setdefault("observation_counts", {}).setdefault(loc_id, 0)
        self.state.setdefault("ai_events", [])
        self.state["ai_events"] = self.state["ai_events"][-100:]
        self.state.setdefault("ai_runtime", {
            "last_world_pulse": -999,
            "world_rounds": 0,
            "failed_rounds": 0
        })
        self.state.setdefault("town_mind", TOWN_MIND_MODEL.runtime_defaults())
        for key, value in TOWN_MIND_MODEL.runtime_defaults().items():
            self.state["town_mind"].setdefault(key, deepcopy(value))
        self.state.setdefault("director_status", {
            "mode": "deterministic",
            "last_ai_domains": [],
            "accepted_proposals": 0
        })

    def weather_environment_effect(self):
        """Player-facing environmental consequence of current weather."""
        state=self.state.get("weather",{}).get("state","clear")
        effects={
            "light_rain":"Rain darkens paths, feeds exposed soil and reduces outdoor wildlife activity.",
            "heavy_rain":"Standing water gathers in low ground; paths soften, gardens soak and animals seek shelter.",
            "storm":"Strong gusts and driving rain batter vegetation, flood low paths and suppress most outdoor activity.",
            "snow":"Snow settles on roofs, hedges and paths; travel is slower, vegetation is insulated and wildlife activity contracts.",
            "mist":"Mist reduces visibility and muffles movement across exposed ground.",
        }
        return effects.get(state,"")

    def simulation_pacing_status(self):
        """Return bounded simulation-debt state used for adaptive, diegetic pacing.

        Real-world inference speed may delay AI influence, but should not silently
        determine how much meaningful village life occurs.  The game therefore
        tracks uncovered pulses and meaningful opportunities while the single
        background worker is busy.  This method is advisory: deterministic play
        remains authoritative and the UI only pauses *large time advances* for a
        short, strictly bounded interval.
        """
        s=self.state
        rt=s.setdefault("ai_runtime", {})
        coverage=rt.setdefault("coverage", {"last_applied_revision":0, "opportunity_journal":[], "compressed_events":0})
        worker=ASYNC_AI_RUNTIME.status()
        revision=self._async_state_revision()
        last=int(coverage.get("last_applied_revision",0) or 0)
        uncovered=max(0, revision-last)
        opportunities=len(coverage.get("opportunity_journal",[]))
        active=int(worker.get("queued_or_running",0) or 0)+int(worker.get("completed_waiting",0) or 0)
        score=uncovered + min(12, opportunities) + min(6, active*2)
        if score>=24 and active: band="critical"
        elif score>=14 and active: band="high"
        elif score>=7 and active: band="moderate"
        else: band="low"
        hold_seconds={"low":0,"moderate":0,"high":6,"critical":10}[band]
        label={"low":"The village is keeping pace.","moderate":"The village is gathering its threads.","high":"Bellwether is catching up with the passing hours.","critical":"The Village Turns — recent hours are settling into consequence."}[band]
        return {"band":band,"score":score,"hold_seconds":hold_seconds,"message":label,
                "uncovered_pulses":uncovered,"meaningful_events_waiting":opportunities,
                "active_ai_jobs":active,"worker":worker}

    def view(self):
        self.migrate_state()
        PLAYER_IDENTITY_MODEL.refresh(self.state, "view_refresh")
        loc = WORLD[self.state["location"]]
        state = deepcopy(self.state)
        cursor = min(self.state["ui"].get("message_cursor", 0), len(self.state["history"]))
        state["new_messages"] = deepcopy(self.state["history"][cursor:])
        state["time"] = self.time_label()
        state["mystery_overview"] = self.investigation_overview()
        state["authored_story_overview"] = STORY_MODEL.public(self.state)
        state["authored_narrative_overview"] = NARRATIVE_EXPANSION_MODEL.public(self.state)
        state["story_consciousness_overview"] = STORY_CONSCIOUSNESS_INTEGRATION_MODEL.public(self.state)
        state["systemic_horror_integration_overview"] = SYSTEMIC_HORROR_INTEGRATION_MODEL.public(self.state)
        state["ending_families_overview"] = ENDING_MODEL.public(self.state)
        state["postgame_overview"] = POSTGAME_MODEL.public(self.state)
        state["quest_lifecycle"] = QUEST_MODEL.developer_context(self.state)
        state["presentation_backlog"] = PRESENTATION_LEDGER_MODEL.public(self.state,80)
        state["life_simulation_overview"] = LIFE_SIMULATION_MODEL.public(self.state)
        state["player_status_overview"] = deepcopy(PLAYER_STATUS_MODEL.migrate(self.state))
        state["cottage_animals_overview"] = ANIMAL_MODEL.public(self.state)
        state["society_overview"] = SOCIETY_MODEL.public(self.state)
        state["village_evolution_overview"] = VILLAGE_EVOLUTION_MODEL.public(self.state)
        state["presentation_horror"] = INTERFACE_HORROR_MODEL.resolve(self.state)
        state["property_overview"] = PROPERTY_MODEL.public(self.state)
        state["player_business_overview"] = PLAYER_BUSINESS_MODEL.public(self.state)
        state["transport_overview"] = TRANSPORT_MODEL.public(self.state)
        state["relationship_life_overview"] = RELATIONSHIP_LIFE_MODEL.public(self.state)
        state["town_consciousness_overview"] = TOWN_MIND_MODEL.developer_context(self.state)
        state["playstyle_pacing_overview"] = PLAYSTYLE_PACING_MODEL.public(self.state)
        state["resistance_overview"] = RESISTANCE_MODEL.public(self.state)
        story_public=STORY_MODEL.public(self.state)
        main_quests=self.visible_quests("main")
        if not story_public.get("ending_eligible"):
            main_quests=main_quests + [{"id":"rc1:"+story_public["chapter"],"title":story_public["title"],"objective":story_public["objective"],"done":False}]
        procedural_opportunities=[]
        for arc in self.state.get("procedural_arcs",{}).get("active",[]):
            procedural_opportunities.append({"id":"arc:"+str(arc.get("id")),"title":arc.get("label","Village opportunity"),"objective":("You have offered help; allow the situation to unfold and check back as village time passes." if arc.get("player_involved") else "Follow the situation where it is unfolding in Bellwether."),"location":arc.get("location"),"done":False,"status":("in_progress" if arc.get("player_involved") else "available"),"procedural":True})
        for arc in self.state.get("procedural_arcs",{}).get("history",[])[-12:]:
            if arc.get("player_involved"):
                procedural_opportunities.append({"id":"arc:"+str(arc.get("id")),"title":arc.get("label","Village opportunity"),"objective":"Resolved through your involvement in village life.","location":arc.get("location"),"done":True,"status":"completed","procedural":True,"reward_applied":arc.get("reward_applied",False),"completed_day":arc.get("resolved_day")})
        state["quests"] = {
            "main": main_quests,
            "side": self.visible_quests("side") + procedural_opportunities,
        }
        present_npcs = [
            npc for npc in self.state.get("npcs", {}).values()
            if npc.get("visible", True) and npc.get("location") == self.state["location"]
        ]
        # Lightweight residents are visible village life, but remain outside the
        # expensive core-NPC dialogue/cognition loops.
        present_npcs.extend(POPULATION_MODEL.present(self.state, self.state["location"]))
        present_traffic = [
            vehicle for vehicle in self.state.get("traffic", {}).values()
            if vehicle.get("location") == self.state["location"]
        ]
        return {
            "state": state,
            "location": {"id": self.state["location"], **loc},
            "world_context": {**WORLD_MODEL.public_location_context(self.state["location"]), "active_events": EVENT_MODEL.location_context(self.state, self.state["location"]), "supernatural_overlay": HORROR_MODEL.location_context(self.state, self.state["location"]), "weather_effect": self.weather_environment_effect()},
            "actions": compact_action_surface(self.actions() + ([{"id":"danger:treat","label":"Treat your injury","kind":"life"}] if self.state.get("danger",{}).get("injuries") and self.state.get("danger",{}).get("status")=="alive" else [])),
            "present": {"npcs": present_npcs, "traffic": present_traffic},
            "simulation_pacing": self.simulation_pacing_status(),
        }

    def actions(self):
        s = self.state
        loc = s["location"]
        if s.setdefault("danger", DANGER_MODEL.runtime_defaults()).get("status") == "dead":
            return [{"id":"failure:recover","label":"Accept recovery","kind":"life"},{"id":"new_run","label":"Begin another run","kind":"story"}]

        if s.get("dialogue"):
            return [
                {"id": f"choice:{c['id']}", "label": c["label"], "kind": "choice"}
                for c in s["dialogue"]["choices"]
            ]

        actions = [{"id": "look", "label": "Look Around", "kind": "observe"},
                   {"id": "ask_village", "label": "Wait and Observe the Village", "kind": "observe"}]

        # Any NPC physically sharing the player's location can be spoken to.  This
        # follows the simulation state rather than hard-coded buildings: if Jonah,
        # Mara, or Mrs Ellis walks elsewhere, conversation travels with them.
        for npc_id, npc in s.get("npcs", {}).items():
            if npc.get("visible", True) and npc.get("location") == loc:
                if self._story_conversation_required(npc_id):
                    actions.append({"id": f"talk:{npc_id}", "label": f"Talk to {npc['name']}", "kind": "talk", "npc_id": npc_id, "npc_name": npc["name"]})
                else:
                    actions.append({
                        "id": f"free_talk:{npc_id}",
                        "label": f"Speak to {npc['name']}",
                        "kind": "free_talk",
                        "npc_id": npc_id,
                        "npc_name": npc["name"],
                    })
                actions.append({"id":f"social:greet:{npc_id}","label":f"Greet {npc['name']}","kind":"social","npc_id":npc_id,"npc_name":npc["name"]})
        if loc == "ashcroft_cottage" and not s["flags"]["read_letter"]:
            actions.append({"id": "read_letter", "label": "Read Eleanor's Letter", "kind": "story"})
        if loc == "ashcroft_cottage" and s["flags"]["read_letter"]:
            actions.append({"id": "sleep", "label": "Sleep Until Morning", "kind": "life"})

        # Cottage animals: deterministic truth, bounded LLM-selected intentions.
        animals=ANIMAL_MODEL.migrate(s)
        if loc == "ashcroft_cottage":
            if not animals["shelters"].get("coop"):
                actions.append({"id":"animals:build:coop","label":"Build a Small Coop (฿60, 2 supplies)","kind":"life","category":"home"})
            elif not animals["shelters"].get("goat_shed") and int(s.get("player_status",{}).get("life_level",1))>=3:
                actions.append({"id":"animals:build:goat_shed","label":"Build a Small Goat Shelter (฿140, 4 supplies)","kind":"life","category":"home"})
            if animals["animals"]:
                actions.append({"id":"animals:feed","label":"Feed the Cottage Animals","kind":"life","category":"home"})
                if any(a.get("production_ready") for a in animals["animals"].values()): actions.append({"id":"animals:collect","label":"Collect Eggs and Milk","kind":"life","category":"home"})
                actions.append({"id":"animals:spend_time","label":"Spend Time with the Animals","kind":"life","category":"home"})
        if loc == "calder_farm" and animals["shelters"].get("coop"):
            actions.append({"id":"animals:buy:chicken","label":"Buy a Chicken (฿35)","kind":"economy","category":"work"})
            actions.append({"id":"animals:buy:duck","label":"Buy a Duck (฿45)","kind":"economy","category":"work"})
        if loc == "calder_farm" and animals["shelters"].get("goat_shed"):
            actions.append({"id":"animals:buy:goat","label":"Buy a Goat (฿120)","kind":"economy","category":"work"})
        if loc == "village_shop" and animals["animals"]:
            actions.append({"id":"animals:buy_feed","label":"Buy Animal Feed (฿12)","kind":"economy","category":"work"})

        # Investigation is player-driven and contextual. Repeated observation,
        # familiarity and attentiveness can expose different layers without forcing
        # the authored story forward.
        actions.append({"id": "investigate:observe", "label": "Observe Carefully", "kind": "investigate"})
        if s["player_life"].get("attentiveness", 0) >= 4 or s["player_life"]["location_familiarity"].get(loc, 0) >= 6:
            actions.append({"id": "investigate:search", "label": "Examine the Area Closely", "kind": "investigate"})
        if s.get("investigation", {}).get("evidence"):
            actions.append({"id": "investigate:review", "label": "Review What You Have Noticed", "kind": "investigate"})

        # Daily-life activities are location-specific and consume meaningful time.
        # The village continues to pulse while the player is occupied.
        life_actions = {
            "ashcroft_cottage": [
                ("life:tea", "Make Tea and Sit for a While"),
                ("life:tidy", "Tidy a Room"),
                # Part 4: gardening is now a staged system, not a one-click activity.
                *ACTIVITY_MODEL.available_garden_actions(s),
                ("life:read", "Read from Eleanor's Shelves"),
                ("life:post", "Check the Post and Front Step"),
            ],
            "bakery": [
                ("life:breakfast", "Buy Something to Eat"),
                ("life:bakery_watch", "Sit by the Window and Watch the Street"),
            ],
            "village_green": [
                ("life:bench", "Sit on the Bench and Watch the Green"),
                ("life:noticeboard", "Read the Noticeboard Carefully"),
                ("life:walk_green", "Take a Slow Walk Around the Green"),
            ],
            "village_road": [
                ("life:errand", "Run a Small Household Errand"),
                ("life:walk_road", "Walk the Road Without Hurrying"),
            ],
            "bus_stop": [
                ("life:watch_road", "Wait and Watch the Road"),
            ],
            "village_shop": [
                ("life:shop_browse", "Browse the Shelves"),
                ("life:newspaper", "Read the Local Newspaper"),
            ],
            "churchyard": [
                ("life:churchyard_walk", "Walk Among the Old Stones"),
                ("life:sit_churchyard", "Sit Quietly by the Yews"),
            ],
            "riverside_path": [
                ("life:river_walk", "Walk Along the River"),
                ("life:watch_water", "Watch the Water for a While"),
            ],
            "railway_halt": [
                ("life:watch_platform", "Wait on the Platform"),
                ("life:read_timetable", "Study the Timetable and Notices"),
            ],
            "field_lane": [("life:field_walk", "Walk the Hedgerow Lane"), ("life:watch_fields", "Watch the Fields for a While")],
            "calder_farm": [("life:farm_observe", "Watch the Farm at Work"), ("life:orchard_walk", "Walk by the Orchard Boundary")],
            "north_woods": [("life:woods_walk", "Follow the Woodland Track"), ("life:listen_woods", "Stop and Listen Beneath the Trees")],
            "old_quarry": [("life:quarry_walk", "Walk the Safe Quarry Terrace"), ("life:study_stone", "Study the Exposed Stone")],
            "quarry_caves": [("life:cave_listen", "Listen in the First Chamber"), ("life:study_passage", "Examine the Worked Passage")],
            "mill_bridge": [("life:watch_water", "Watch the Water Below the Bridge"), ("life:river_walk", "Walk the Mill Race")],
            "orchard_lane": [("life:orchard_walk", "Walk the Orchard Lane"), ("life:watch_fields", "Watch the Orchard Work")],
            "south_pasture": [("life:field_walk", "Walk the Pasture Footpath"), ("life:watch_fields", "Watch the Sheep and Weather")],
            "moor_gate": [("life:field_walk", "Walk Beyond the Moor Gate"), ("life:watch_fields", "Watch Weather Cross the High Ground")],
            "ridge_path": [("life:quarry_walk", "Walk the Ridge Path"), ("life:watch_fields", "Look Out Across Bellwether")],
            "east_hamlet": [("life:walk_road", "Walk Through East Hamlet"), ("life:errand", "Help with a Small Hamlet Errand")],
            "workshop_yard": [("life:farm_observe", "Watch the Workshop at Work"), ("life:errand", "Carry Materials Across the Yard")],
        }
        for action_id, label in life_actions.get(loc, []):
            actions.append({"id": action_id, "label": label, "kind": "life"})
        for action_id, label in ACTIVITY_MODEL.available_hobby_actions(s):
            actions.append({"id": action_id, "label": label, "kind": "life"})

        # v0.7.2: active procedural arcs can expose bounded, location-specific player involvement.
        for action_id, label in PROCEDURAL_ARC_MODEL.available_player_actions(s):
            actions.append({"id":action_id,"label":label,"kind":"social"})

        # Part 16: harvested food and cottage repair supplies now feed deep ordinary-life loops.
        for action_id, label in CONTENT_MODEL.cooking_actions(s):
            actions.append({"id":action_id,"label":label,"kind":"life"})
        for action_id, label in CONTENT_MODEL.repair_actions(s):
            actions.append({"id":action_id,"label":label,"kind":"life"})
        for action_id, label in CONTENT_MODEL.home_actions(s):
            actions.append({"id":action_id,"label":label,"kind":"life"})
        for action_id, label in LIFE_SIMULATION_MODEL.actions(s):
            actions.append({"id":action_id,"label":label,"kind":"life"})
        for action_id, label in PLAYER_STATUS_MODEL.actions(s):
            actions.append({"id":action_id,"label":label,"kind":"life"})
        for action_id, label in PROPERTY_MODEL.actions(s):
            actions.append({"id":action_id,"label":label,"kind":"economy"})
        for action_id, label in PLAYER_BUSINESS_MODEL.actions(s):
            actions.append({"id":action_id,"label":label,"kind":"economy"})
        for action_id, label in TRANSPORT_MODEL.actions(s):
            actions.append({"id":action_id,"label":label,"kind":"travel"})
        for action_id, label in RELATIONSHIP_LIFE_MODEL.actions(s):
            actions.append({"id":action_id,"label":label,"kind":"social"})
        for action_id, label in RESISTANCE_MODEL.actions(s):
            actions.append({"id":action_id,"label":label,"kind":"life"})
        for resident in POPULATION_MODEL.present(s, s.get("location"))[:6]:
            actions.append({"id":"society:greet:"+resident["id"],"label":"Greet "+resident["name"],"kind":"social"})

        # Part 6: applications and scheduled shifts use authored job definitions and real world locations.
        for action_id, label in JOB_MODEL.available_actions(s):
            actions.append({"id":action_id,"label":label,"kind":"job"})

        # Part 5: purchases and produce sales use the same location/open-hours world state.
        if WORLD_MODEL.access_status(loc, s.get("minute",0))[0]:
            for action_id, label in ECONOMY_MODEL.actions(s):
                actions.append({"id":action_id,"label":label,"kind":"economy"})

        setbacks=s.get("branch_state",{}).get("setbacks",[])
        if "overwhelmed" in setbacks:
            actions.append({"id":"recover:ground","label":"Slow Down and Ground Yourself","kind":"life"})
        if "short_of_money" in setbacks:
            actions.append({"id":"recover:help","label":"Ask Around for Practical Work","kind":"life"})

        # v1.0 RC2: expose only deterministic ending families earned by authoritative play state.
        if STORY_MODEL.public(s).get("ending_eligible") and not s.get("ending_families",{}).get("resolved"):
            for ending_id in ENDING_MODEL.refresh(s):
                actions.append({"id":f"ending:{ending_id}","label":f"Choose: {FAMILIES[ending_id]['title']}","kind":"story"})

        for action_id, label in POSTGAME_MODEL.actions(s):
            actions.append({"id":action_id,"label":label,"kind":"life"})

        for label, target in WORLD[loc]["exits"].items():
            actions.append({"id": f"move:{target}", "label": label, "kind": "travel"})

        actions.append({"id": "rest", "label": "Take a Moment", "kind": "life"})
        return actions

    def add(self, speaker, text):
        """Add player-facing prose with conservative consecutive deduplication."""
        row={"speaker": str(speaker), "text": str(text).strip()}
        if not row["text"]: return
        history=self.state.setdefault("history", [])
        if history and history[-1].get("speaker")==row["speaker"] and history[-1].get("text")==row["text"]:
            return
        history.append(row)
        self.state["history"] = history[-120:]
        PRESENTATION_LEDGER_MODEL.append(self.state, row["speaker"], row["text"])

    def advance(self, minutes):
        """Advance chronologically and coalesce AI work into one batch per player action.

        Part 27 jumped the clock to the final minute before replaying all 10-minute
        pulses, so every pulse saw the same time/temperature target. It also allowed
        a long action to trigger several separate Director rounds. Both are fixed here.
        """
        if minutes <= 0:
            return
        s=self.state
        scheduler=s.setdefault("simulation_scheduler", deepcopy(INITIAL_STATE["simulation_scheduler"]))
        scheduler["advance_active"]=True
        scheduler["pending_domains"]=[]
        remaining=int(minutes)
        while remaining > 0:
            step=min(10, remaining)
            s["minute"] += step
            # Simple day rollover; preserve absolute simulation continuity.
            while s["minute"] >= 1440:
                WORLD_RUNTIME_MODEL.record_day(s, s["day"])
                s["minute"] -= 1440
                s["day"] += 1
                HORROR_AFTERMATH_MODEL.daily_recovery(s)
                FAILURE_RECOVERY_MODEL.evaluate_adaptive_pressure(s)
                for echo in RECURRENCE_MODEL.advance_day(s): self.add(echo["speaker"], echo["text"])
            self.update_temperature_for_time()
            self.update_npc_personal_lives(step)
            ACTIVITY_MODEL.advance(s, step)
            PLAYER_STATUS_MODEL.advance(s, step)
            for animal_event in ANIMAL_MODEL.advance_day(s): self.add("Narrator", animal_event)
            SEASONAL_MODEL.refresh(s)
            WORLD_RUNTIME_MODEL.advance(s, step)
            POPULATION_MODEL.advance_batch(s)
            SOCIETY_MODEL.advance_day(s, POPULATION_MODEL)
            for life_event in NPC_LIFE_MODEL.advance_day(s):
                self.record_world_event(life_event["text"], "npc_life", life_event["kind"])
            for evolution_event in VILLAGE_EVOLUTION_MODEL.advance_day(s):
                self.record_world_event(evolution_event["text"], "village_evolution", evolution_event["kind"])
            HORROR_MODEL.expire(s)
            for event_kind,event_id,message in EVENT_MODEL.advance(s):
                self.add("Bellwether", message)
                self.record_world_event(message, "dynamic_event", event_id)
            if step == 10:
                self.update_npc_social_web()
                self.propagate_npc_knowledge()
                self.village_pulse(run_directors=False)
            remaining -= step
        scheduler["advance_active"]=False
        domains=list(scheduler.get("pending_domains",[]))
        scheduler["pending_domains"]=[]
        if domains:
            self.queue_ai_directors(domains, "coalesced_player_action")
        # Strategic systems must also be considered after ordinary time advancement.
        # Earlier builds only called these from village_pulse(run_directors=True), while
        # advance() deliberately uses False, making procedural arcs unreachable in normal play.
        self.maybe_run_town_mind()
        self.maybe_run_procedural_arcs()
        self.maybe_run_ecology_review()


    def village_pulse(self, run_directors=True):
        s = self.state
        brain = s["village_brain"]
        brain["pulse_count"] += 1
        minute = s["minute"]

        if minute < 660:
            brain["mood"] = "quietly_busy"
            brain["focus"] = "morning_routines"
            s["ambient"]["village"] = "Bellwether is settling into its morning rhythm."
        elif minute < 900:
            brain["mood"] = "sociable"
            brain["focus"] = "shops_and_errands"
            s["ambient"]["village"] = "The village has grown busier around the green and shops."
        else:
            brain["mood"] = "winding_down"
            brain["focus"] = "homeward_routines"
            s["ambient"]["village"] = "The day's movement is beginning to turn homeward."

        pulse = brain["pulse_count"]
        if pulse % 3 == 0:
            s["ambient"]["traffic"] = "A delivery van passes through the village."
        elif pulse % 3 == 1:
            s["ambient"]["traffic"] = "The road is quiet between scheduled buses."
        else:
            s["ambient"]["traffic"] = "A cyclist rattles past with a basket on the rear rack."

        if pulse % 2 == 0:
            s["ambient"]["wildlife"] = "A robin patrols the hedges while rooks call beyond the church."
        else:
            s["ambient"]["wildlife"] = "Blackbirds work through the wet grass."

        # Every pulse leaves a small persistent consequence: the village lives even
        # when no AI Director happens to be scheduled on this tick.
        self.apply_tick_consequence()
        COGNITION_MODEL.fade(s)
        self.propagate_world_consequences("pulse")

        self.harvest_async_ai_results()

        # Universal AI World round: ordinary movement, dialogue, rest, quests,
        # and sleep all reach this path through time advancement.
        self.maybe_run_ai_directors(run_now=run_directors)
        if run_directors:
            self.maybe_run_town_mind()
            self.maybe_run_procedural_arcs()

    def record_world_event(self, text, domain="village", actor=None):
        event = {"time": self.time_label(), "domain": domain, "text": text}
        if actor: event["actor"] = actor
        events=self.state.setdefault("world_events", [])
        if events and events[-1].get("text")==event["text"] and events[-1].get("domain")==event["domain"]:
            return
        events.append(event)
        self.state["world_events"] = events[-40:]
        # v1.0.4: retain a bounded journal of meaningful changes that occurred
        # while AI may have been busy. Tick boilerplate is intentionally excluded.
        if domain not in {"tick", "ai_pacing"}:
            rt=self.state.setdefault("ai_runtime", {})
            coverage=rt.setdefault("coverage", {"last_applied_revision":0, "opportunity_journal":[], "compressed_events":0})
            journal=coverage.setdefault("opportunity_journal", [])
            compact={"revision":self._async_state_revision(),"day":self.state.get("day"),"time":self.time_label(),"domain":domain,"text":str(text)[:220]}
            if not journal or (journal[-1].get("domain"),journal[-1].get("text")) != (compact["domain"],compact["text"]):
                journal.append(compact)
            if len(journal)>40:
                coverage["compressed_events"]=int(coverage.get("compressed_events",0))+len(journal)-40
                coverage["opportunity_journal"]=journal[-40:]

    def apply_tick_consequence(self):
        """Give every Village Pulse a lightweight stateful consequence."""
        s=self.state; pulse=s["village_brain"]["pulse_count"]
        if pulse % 3 == 0:
            text="A delivery has been made somewhere in the village; doors open and close along the road."
        elif pulse % 3 == 1:
            text="Another small errand is completed as Bellwether moves through its day."
        else:
            text="Footsteps and wheels shift between the road and green, changing who may meet next."
        self.record_world_event(text, "tick")

    def propagate_world_consequences(self, cause_domain="pulse"):
        """Derive second-order consequences from the current world state.

        Director outputs change actors; this pass changes places, creates meetings,
        leaves memories, and records player-observable traces for later ticks.
        """
        s = self.state
        now = self.time_label()
        loc_state = s.setdefault("location_state", deepcopy(INITIAL_STATE["location_state"]))

        # Occupation and place state are linked: Jonah's choices affect the bakery.
        jonah = s["npcs"].get("jonah", {})
        bakery = loc_state["bakery"]
        staffed = jonah.get("location") == "bakery"
        if bakery.get("staffed") != staffed:
            bakery["staffed"] = staffed
            bakery["last_change"] = now
            text = "Jonah has returned to the bakery; the counter is staffed again." if staffed else "Jonah has left the bakery; the counter is temporarily unattended."
            self.record_world_event(text, "place", "jonah")
        bakery["open"] = 420 <= s["minute"] < 1020
        bakery["bread_available"] = bakery["open"] and (staffed or "baking" in jonah.get("activity", ""))

        # Mara's work has cumulative physical effect instead of being cosmetic text.
        mara = s["npcs"].get("mara", {})
        garden = loc_state["ashcroft_cottage"]
        if mara.get("location") == "ashcroft_cottage" and any(w in mara.get("activity", "") for w in ("garden", "weed", "clearing")):
            before = garden.get("garden_progress", 0)
            garden["garden_progress"] = min(100, before + 1)
            garden["last_change"] = now
            if garden["garden_progress"] in (1, 5, 10, 20, 40, 60, 80, 100):
                self.record_world_event(f"Work in the Ashcroft garden has reached progress {garden['garden_progress']}.", "place", "mara")

        # Traffic changes the road's immediate state and leaves an observation trace.
        on_road = [v for v in s["traffic"].values() if v.get("location") == "village_road"]
        road = loc_state["village_road"]
        new_level = min(3, len(on_road))
        if road.get("traffic_level") != new_level:
            road["traffic_level"] = new_level
            road["last_change"] = now
        green_people = [i for i,n in s["npcs"].items() if n.get("location") == "village_green"]
        loc_state["village_green"]["activity_level"] = len(green_people)
        loc_state["village_green"]["last_change"] = now

        # Co-location creates a persistent encounter once per pair/location/time window.
        by_location = {}
        for npc_id, npc in s["npcs"].items():
            by_location.setdefault(npc.get("location"), []).append(npc_id)
        recent_keys = {e.get("key") for e in s.setdefault("encounters", [])[-12:]}
        for location, ids in by_location.items():
            if not location or location == "away" or len(ids) < 2:
                continue
            for i in range(len(ids)):
                for j in range(i + 1, len(ids)):
                    pair = sorted((ids[i], ids[j]))
                    key = f"{s['day']}:{s['minute']//30}:{location}:{pair[0]}:{pair[1]}"
                    if key in recent_keys:
                        continue
                    names = [s["npcs"][x]["name"] for x in pair]
                    event = {"time": now, "location": location, "participants": pair, "key": key,
                             "cause": cause_domain, "summary": f"{names[0]} and {names[1]} crossed paths at {WORLD[location]['name']}."}
                    s["encounters"].append(event)
                    self.record_world_event(event["summary"], "encounter")
                    for actor, other in ((pair[0], pair[1]), (pair[1], pair[0])):
                        s["social_memory"].setdefault(actor, []).append(f"Crossed paths with {s['npcs'][other]['name']} at {WORLD[location]['name']} around {now}.")
                        s["social_memory"][actor] = s["social_memory"][actor][-12:]
        s["encounters"] = s["encounters"][-30:]

        # Store concise place traces. Look/arrival can reveal consequences produced off-screen.
        obs = s.setdefault("location_observations", {})
        obs["bakery"] = ("The bakery counter is staffed and warm with work." if bakery["staffed"] else "The bakery is open, but the counter is unattended for the moment.")
        gp = garden.get("garden_progress", 0)
        if gp:
            obs["ashcroft_cottage"] = "Freshly disturbed soil and a growing cleared patch show that someone has been working in the garden."
        obs["village_road"] = ("The road is busy with passing traffic." if new_level >= 2 else "The road has settled into a quieter interval.")
        light_green = POPULATION_MODEL.present(s, "village_green")
        total_green = len(green_people) + len(light_green)
        if total_green:
            obs["village_green"] = f"There are {total_green} villager{'s' if total_green != 1 else ''} moving around the green."
        else:
            obs["village_green"] = "For the moment, the green has fallen quiet."

    def surface_location_consequence(self, location):
        text = self.state.get("location_observations", {}).get(location)
        if text:
            self.add("Bellwether", text)

    def complete(self, group, quest_id):
        result = QUEST_MODEL.complete(self.state, group, quest_id)
        if result and result.get("newly_completed"):
            reward=(result.get("transaction") or {}).get("reward",{})
            parts=[]
            if reward.get("money"): parts.append(f"฿{reward['money']}")
            if reward.get("life_xp"): parts.append(f"{reward['life_xp']} life XP")
            parts.extend(reward.get("items",[]) or [])
            if reward.get("community"): parts.append(f"community standing +{reward['community']}")
            if parts:self.add("Journal", "Reward received: " + ", ".join(parts) + ".")
        return result

    def reveal(self, group, quest_id):
        for q in self.state["quests"][group]:
            if q["id"] == quest_id:
                q["hidden"] = False


    def start_jonah_dialogue(self):
        s = self.state
        if not s["flags"]["met_jonah"]:
            self.add("Jonah", "You must be Eleanor's relation. I had a loaf riding on whether you'd take the morning bus.")
            s["dialogue"] = {
                "npc": "jonah",
                "choices": [
                    {"id": "jonah_warm", "label": "“You knew I was coming?”"},
                    {"id": "jonah_guarded", "label": "“People talk about strangers here, then?”"},
                    {"id": "jonah_eleanor", "label": "Ask how well he knew Eleanor."}
                ]
            }
        else:
            self.add("Jonah", "How are you finding the cottage?")
            choices = [
                {"id": "jonah_settling", "label": "“I'm beginning to settle in.”"},
                {"id": "jonah_bells", "label": "Ask about the church bells."},
                {"id": "leave_dialogue", "label": "Say goodbye."}
            ]
            s["dialogue"] = {"npc": "jonah", "choices": choices}

    def resolve_choice(self, choice):
        s = self.state

        if choice == "jonah_warm":
            self.branch_score("community",2,"Responded warmly to Jonah's welcome.")
            self.add("You", "You knew I was coming?")
            self.add("Jonah", "Bellwether is a small place. News usually arrives before the bus does.")
            self.add("Jonah", "Take this. First morning in a new house shouldn't begin with an empty bread bin.")
            self._update_relationship("jonah", "responded warmly at the first meeting", affinity=2, familiarity=3, trust=1)
            s["social_memory"]["jonah"].append("The newcomer responded warmly on their first meeting.")
            self.finish_jonah_intro()

        elif choice == "jonah_guarded":
            self.branch_score("avoidance",1,"Kept some distance from Jonah's village curiosity.")
            self.add("You", "People talk about strangers here, then?")
            self.add("Jonah", "Only until they stop being strangers. Around here, that rarely takes long.")
            self.add("Jonah", "Here. Bread. Consider it an apology from the village gossip network.")
            self._update_relationship("jonah", "showed guarded curiosity", affinity=1, familiarity=2, trust=0)
            s["social_memory"]["jonah"].append("The newcomer was guarded about village curiosity.")
            self.finish_jonah_intro()

        elif choice == "jonah_eleanor":
            self.branch_score("inquiry",2,"Asked Jonah directly about Eleanor.")
            self.add("You", "How well did you know Eleanor?")
            self.add("Jonah", "Well enough to know she'd hate me answering that before you've even unpacked.")
            self.add("Jonah", "But she was a friend. Here—take a loaf. She'd complain if I let you go hungry.")
            self._update_relationship("jonah", "responded warmly at the first meeting", affinity=2, familiarity=3, trust=1)
            s["social_memory"]["jonah"].append("The newcomer immediately asked about Eleanor.")
            self.finish_jonah_intro()

        elif choice == "jonah_settling":
            self.add("You", "I'm beginning to settle in.")
            self.add("Jonah", "Good. Bellwether rewards patience more than enthusiasm.")
            self._update_relationship("jonah", "showed guarded curiosity", affinity=1, familiarity=2, trust=0)
            s["dialogue"] = None

        elif choice == "jonah_bells":
            self.add("You", "Eleanor wrote something about the bells waking me.")
            self.add("Jonah", "Did she?")
            self.add("Narrator", "For the first time, Jonah's hands stop moving.")
            self.add("Jonah", "Old houses make ordinary sounds seem important at night. That's all.")
            s["social_memory"]["jonah"].append("The newcomer asked about Eleanor's warning concerning the bells.")
            s["dialogue"] = None

        elif choice == "mara_garden":
            self.branch_score("care",2,"Committed to restoring Eleanor's garden with Mara.")
            self.branch_score("community",1)
            self.add("You", "I'd like to restore the garden, if you'll help me.")
            self.add("Mara", "Then we'll begin with what the garden wants, not what we want from it.")
            self._update_relationship("mara", "committed to restoring the garden together", affinity=2, familiarity=3, trust=2)
            s["social_memory"]["mara"].append("The newcomer committed to restoring Eleanor's garden.")
            self.finish_mara_intro()

        elif choice == "mara_eleanor":
            self.branch_score("inquiry",2,"Asked Mara about Eleanor's garden history.")
            self.add("You", "What did Eleanor grow?")
            self.add("Mara", "Everything badly suited to the soil, mostly. She enjoyed proving the ground wrong.")
            self._update_relationship("mara", "asked about Eleanor and the garden", affinity=1, familiarity=2, trust=1)
            s["social_memory"]["mara"].append("The newcomer asked about Eleanor's garden.")
            self.finish_mara_intro()

        elif choice == "leave_dialogue":
            self.branch_score("avoidance",1,"Chose to end an authored conversation without committing further.")
            self.add("Narrator", "The conversation ends naturally.")
            s["dialogue"] = None

    def finish_jonah_intro(self):
        s = self.state
        if "Warm country loaf" not in s["inventory"]:
            s["inventory"].append("Warm country loaf")
        s["flags"]["met_jonah"] = True
        self.complete("side", "jonah")
        self.add("Journal", "Side Story completed: A Warm Welcome.")
        s["dialogue"] = None

    def finish_mara_intro(self):
        s = self.state
        s["flags"]["met_mara"] = True
        self.complete("side", "mara")
        self.add("Journal", "Side Story completed: The Cottage Garden.")
        s["dialogue"] = None

    def start_mara_dialogue(self):
        s = self.state
        if not s["flags"]["met_mara"]:
            self.add("Mara", "Ashcroft Cottage? Then you're the one who's inherited Eleanor's place.")
            self.add("Mara", "I'm Mara. I helped Eleanor with the garden once her knees started objecting to every useful task.")
            s["dialogue"] = {
                "npc": "mara",
                "choices": [
                    {"id": "mara_garden", "label": "Ask Mara to help restore the garden."},
                    {"id": "mara_eleanor", "label": "Ask what Eleanor used to grow."},
                    {"id": "leave_dialogue", "label": "Say you'll speak another time."}
                ]
            }
        else:
            self.add("Mara", "The garden will still be there tomorrow. Gardens are patient that way.")
            s["dialogue"] = {"npc":"mara","choices":[{"id":"leave_dialogue","label":"Say goodbye."}]}



    def _story_conversation_required(self, npc_id):
        """True only when Talk must enter an authored story/quest conversation."""
        s = self.state
        if npc_id == "jonah" and not s["flags"]["met_jonah"]:
            return True
        if npc_id == "mara" and not s["flags"]["met_mara"] and s["flags"].get("mara_intro_available"):
            return True
        return False

    def _conversation_story_context(self):
        """Compact evolving story context for ambient dialogue grounding."""
        s = self.state
        active_main = [
            {"title": q["title"], "objective": q["objective"]}
            for q in s["quests"]["main"] if not q.get("done") and not q.get("hidden")
        ][-3:]
        active_side = [
            {"title": q["title"], "objective": q["objective"]}
            for q in s["quests"]["side"] if not q.get("done") and not q.get("hidden")
        ][-3:]
        return {
            "day": s["day"],
            "story_flags": {
                "reached_cottage": s["flags"].get("reached_cottage", False),
                "read_letter": s["flags"].get("read_letter", False),
                "met_jonah": s["flags"].get("met_jonah", False),
                "met_mara": s["flags"].get("met_mara", False),
            },
            "active_main_story": active_main,
            "active_side_stories": active_side,
            "village_focus": s["village_brain"].get("focus"),
        }

    def _relationship_context(self, npc_id):
        rel = self.state["relationships"][npc_id]
        return {
            "affinity": rel["affinity"], "familiarity": rel["familiarity"],
            "trust": rel["trust"], "talks": rel["talks"],
            "recent_impressions": rel["impressions"][-5:],
            "stage": SOCIAL_CONSEQUENCE_MODEL.relationship_stage(rel),
            "social_consequences": SOCIAL_CONSEQUENCE_MODEL.context(self.state,npc_id,limit=5),
        }

    def _update_relationship(self, npc_id, reason, affinity=0, familiarity=0, trust=0):
        rel = self.state["relationships"][npc_id]
        rel["affinity"] = max(-100, min(100, rel["affinity"] + affinity))
        rel["familiarity"] = max(0, min(100, rel["familiarity"] + familiarity))
        rel["trust"] = max(-100, min(100, rel["trust"] + trust))
        rel["last_interaction"] = self.time_label()
        rel["impressions"].append({"time": self.time_label(), "reason": reason,
                                   "affinity": affinity, "trust": trust})
        rel["impressions"] = rel["impressions"][-12:]

    def _social_consequences_from_life(self, activity_id):
        """Repeated visible behaviour slowly shapes NPC impressions."""
        s = self.state
        nearby = [nid for nid,n in s["npcs"].items()
                  if n.get("visible", True) and n.get("location") == s["location"]]
        signals = {
            "garden": ("saw the newcomer caring for the Ashcroft garden", 1, 1),
            "tidy": ("noticed the cottage being cared for", 1, 0),
            "errand": ("saw the newcomer becoming part of ordinary village life", 1, 0),
            "bench": ("has grown used to seeing the newcomer quietly on the green", 1, 0),
            "noticeboard": ("noticed the newcomer taking an interest in village affairs", 1, 1),
            "breakfast": ("has seen the newcomer returning to the bakery", 1, 0),
        }
        if activity_id in signals:
            reason, aff, trust = signals[activity_id]
            for nid in nearby:
                self._update_relationship(nid, reason, aff, 1, trust)

    def _player_conversation_fallback(self, npc_id, player_text):
        """Short deterministic reply when foreground generation is unavailable."""
        text=(player_text or "").strip().lower()
        name=self.state["npcs"][npc_id]["name"]
        farewells=("bye","goodbye","see you","see ya","later","take care","cheers")
        thanks=("thank","thanks","appreciate")
        greetings=("hello","hi","hey","morning","afternoon","evening")
        if any(x in text for x in farewells):
            replies={
                "jonah":"See you around. Take care.",
                "mara":"See you. Take care on the way.",
                "mrs_ellis":"Goodbye, dear. Mind how you go.",
            }
            return replies.get(npc_id,"See you. Take care.")
        if any(x in text for x in thanks):
            replies={
                "jonah":"You're welcome. Any time.",
                "mara":"Of course. You're welcome.",
                "mrs_ellis":"You're very welcome, dear.",
            }
            return replies.get(npc_id,"You're welcome.")
        if any(x in text for x in greetings):
            replies={
                "jonah":"Hello. Good to see you.",
                "mara":"Hello. How are you settling in?",
                "mrs_ellis":"Hello, dear. How are you getting on?",
            }
            return replies.get(npc_id,"Hello. Good to see you.")
        replies={
            "jonah":"Sorry, I lost the thread for a moment. Go on.",
            "mara":"Sorry, my mind wandered for a moment. Go on.",
            "mrs_ellis":"Forgive me, dear, my mind wandered. Go on.",
        }
        return replies.get(npc_id,"Sorry, I missed that. Go on.")

    def _npc_social_personality(self, npc_id):
        """Stable authored identity for dialogue and social interpretation."""
        if npc_id in NPC_MODEL.npcs:
            ident = NPC_MODEL.dialogue_identity(npc_id)
            return {"values": ident["values"], "dislikes": ident["dislikes"], "style": ident["social_style"]}
        return {"values":["respect","honesty"],"dislikes":["hostility"],"style":"grounded and observant"}

    def update_npc_personal_lives(self, elapsed_minutes):
        """Slow deterministic need drift. Directors may react to this state later; canon cannot be changed here."""
        lives=self.state.setdefault("npc_lives", NPC_MODEL.runtime_defaults())
        for npc_id, runtime in lives.items():
            if npc_id not in self.state.get("npcs",{}):
                continue
            needs=runtime.setdefault("needs", deepcopy(NPC_MODEL.npcs[npc_id]["needs"]))
            npc=self.state["npcs"][npc_id]; activity=npc.get("activity","").lower()
            scale=max(0.0,float(elapsed_minutes)/60.0)
            needs["food"]=min(100, needs.get("food",0)+1.5*scale)
            needs["rest"]=min(100, needs.get("rest",0)+(0.5 if "rest" in activity or "tea" in activity else 1.0)*scale)
            if any(x in activity for x in ("chat","greet","word with","social")):
                needs["social"]=max(0,needs.get("social",0)-3.0*scale)
            else:
                needs["social"]=min(100,needs.get("social",0)+0.5*scale)
            if any(x in activity for x in ("work","baking","garden","errand","serving","checking")):
                needs["purpose"]=max(0,needs.get("purpose",0)-2.0*scale)
            else:
                needs["purpose"]=min(100,needs.get("purpose",0)+0.4*scale)
            for key in list(needs): needs[key]=round(max(0,min(100,needs[key])),2)
            runtime["last_need_update_minute"]=self.state["day"]*1440+self.state["minute"]

    def npc_life_context(self, npc_id):
        runtime=deepcopy(self.state.setdefault("npc_lives",NPC_MODEL.runtime_defaults()).get(npc_id,{}))
        authored=NPC_MODEL.purpose_context(npc_id,self.state["minute"],self.state["weather"]["state"])
        return {"runtime":runtime,"authored_constraints":authored}


    def update_npc_social_web(self):
        """Record bounded autonomous social contact when core NPCs share a place.

        A 60-minute cooldown prevents ten-minute simulation pulses from inflating
        relationships. This layer creates hooks for Part 10 information flow but
        does not invent rumours or canon.
        """
        web=self.state.setdefault("npc_social_web",SOCIAL_MODEL.runtime_defaults())
        now=(int(self.state.get("day",1))-1)*1440+int(self.state.get("minute",0))
        ids=[nid for nid in SOCIAL_MODEL.npcs] if hasattr(SOCIAL_MODEL,"npcs") else list(self.state.get("npcs",{}))
        ids=[nid for nid in ids if nid in self.state.get("npcs",{}) and nid in {x for edge in SOCIAL_MODEL.edges for x in edge.split("|")}]
        for i,a in enumerate(ids):
            for b in ids[i+1:]:
                eid=SOCIAL_MODEL.edge_id(a,b)
                if eid not in SOCIAL_MODEL.edges: continue
                na,nb=self.state["npcs"][a],self.state["npcs"][b]
                if na.get("location")!=nb.get("location") or not na.get("visible",True) or not nb.get("visible",True): continue
                rt=web.setdefault(eid,deepcopy(SOCIAL_MODEL.runtime_defaults()[eid]))
                last=rt.get("last_encounter_minute")
                if last is not None and now-int(last)<60: continue
                loc=na.get("location"); effect=SOCIAL_MODEL.bounded_encounter_effect(a,b,loc,[na.get("activity",""),nb.get("activity","")])
                for dim,delta in effect.items(): rt["state"][dim]=max(-100,min(100,rt["state"].get(dim,0)+delta))
                event={"absolute_minute":now,"day":self.state.get("day"),"time":self.time_label(),"location":loc,"activities":{a:na.get("activity"),b:nb.get("activity")},"effect":effect}
                rt["encounter_count"]+=1; rt["last_encounter_minute"]=now; rt["encounter_history"].append(event); rt["encounter_history"]=rt["encounter_history"][-24:]
                rt["recent_effects"].append(effect); rt["recent_effects"]=rt["recent_effects"][-8:]
                MEMORY_MODEL.record(self.state,"encounter",f"{na.get('name',a)} and {nb.get('name',b)} crossed paths at {WORLD[loc]['name']}.",actors=[a,b],location=loc,witnesses=[a,b],importance=1,tags=["npc_social_encounter"])

    def npc_social_context(self, npc_id):
        """Return bounded relationship context for Directors/dialogue without exposing canon mutation."""
        web=self.state.setdefault("npc_social_web",SOCIAL_MODEL.runtime_defaults()); out={}
        for eid in SOCIAL_MODEL.edges:
            if npc_id in eid.split("|"):
                other=next(x for x in eid.split("|") if x!=npc_id)
                out[other]=SOCIAL_MODEL.context(npc_id,other,web)
        return out

    def share_npc_topic(self, source_id, target_id, topic_id):
        """Bounded information-flow hook. Part 3 stores topic identifiers only; Part 10 will own propagation rules."""
        eid=SOCIAL_MODEL.edge_id(source_id,target_id)
        if eid not in SOCIAL_MODEL.edges: return False
        rt=self.state.setdefault("npc_social_web",SOCIAL_MODEL.runtime_defaults()).setdefault(eid,deepcopy(SOCIAL_MODEL.runtime_defaults()[eid]))
        topic=str(topic_id).strip()[:80]
        if not topic: return False
        if topic not in rt["shared_topics"]: rt["shared_topics"].append(topic); rt["shared_topics"]=rt["shared_topics"][-20:]
        return True

    def npc_knowledge_context(self, npc_id):
        """Bounded inspectable beliefs for dialogue and future decision systems."""
        runtime=self.state.setdefault("npc_knowledge",KNOWLEDGE_MODEL.runtime_defaults(list(self.state.get("npcs",{}))))
        return KNOWLEDGE_MODEL.context(npc_id,runtime)

    def learn_npc_fact(self, npc_id, fact_id, confidence=0.8, source="observation"):
        """Add only catalogue-backed knowledge; generative systems cannot invent canon facts."""
        if fact_id not in KNOWLEDGE_MODEL.facts or npc_id not in self.state.get("npcs",{}): return False
        runtime=self.state.setdefault("npc_knowledge",KNOWLEDGE_MODEL.runtime_defaults(list(self.state.get("npcs",{}))))
        nr=runtime["npcs"].setdefault(npc_id,{"schema_version":1,"beliefs":{},"withheld":[],"transmission_log":[]})
        now=(int(self.state.get("day",1))-1)*1440+int(self.state.get("minute",0))
        old=nr["beliefs"].get(fact_id)
        if old: old["confidence"]=max(float(old.get("confidence",0)),float(confidence)); old["heard_count"]=int(old.get("heard_count",0))+1; old["last_heard_minute"]=now
        else: nr["beliefs"][fact_id]={"confidence":max(0,min(1,float(confidence))),"variant":"truth","source":source,"heard_count":1,"last_heard_minute":now}
        return True

    def propagate_npc_knowledge(self):
        """Propagate at most one bounded catalogue fact per fresh social encounter."""
        runtime=self.state.setdefault("npc_knowledge",KNOWLEDGE_MODEL.runtime_defaults(list(self.state.get("npcs",{}))))
        web=self.state.setdefault("npc_social_web",SOCIAL_MODEL.runtime_defaults())
        now=(int(self.state.get("day",1))-1)*1440+int(self.state.get("minute",0))
        for eid,edge in web.items():
            hist=edge.get("encounter_history",[])
            if not hist or int(hist[-1].get("absolute_minute",-1))!=now: continue
            a,b=eid.split("|")
            for source,target in ((a,b),(b,a)):
                fid,belief=KNOWLEDGE_MODEL.choose_transfer(source,target,edge.get("state",{}),runtime,now)
                if not fid: continue
                target_rt=runtime["npcs"].setdefault(target,{"schema_version":1,"beliefs":{},"withheld":[],"transmission_log":[]})
                target_rt["beliefs"][fid]=belief
                event={"absolute_minute":now,"source":source,"target":target,"fact_id":fid,"variant":belief["variant"],"confidence":belief["confidence"]}
                runtime["propagation_log"].append(event); runtime["propagation_log"]=runtime["propagation_log"][-100:]
                target_rt["transmission_log"].append(event); target_rt["transmission_log"]=target_rt["transmission_log"][-30:]
                self.share_npc_topic(source,target,fid)
                SOCIAL_CONSEQUENCE_MODEL.record_gossip(self.state,source,target,fid,belief["variant"],belief["confidence"])

    def _daypart(self):
        minute=int(self.state.get("minute",0))%1440
        if 300 <= minute < 720: return "morning"
        if 720 <= minute < 1020: return "afternoon"
        if 1020 <= minute < 1260: return "evening"
        return "night"

    def _conversation_recent_exchange_context(self, npc_id):
        """Compact recent-turn continuity for small local models; never re-inject full NPC prose."""
        now_day=int(self.state.get("day",1)); now_minute=int(self.state.get("minute",0)); now_abs=(now_day-1)*1440+now_minute
        out=[]
        for item in self.state.setdefault("conversation_sessions",{}).setdefault(npc_id,[])[-3:]:
            saved_abs=item.get("absolute_minute")
            elapsed=None if saved_abs is None else max(0,now_abs-int(saved_abs))
            player=" ".join(str(item.get("player","")).split())[:140]
            npc=" ".join(str(item.get("npc","")).split())
            # Topic/act summary plus a short reply fingerprint for repetition detection; prompt never sees full prior prose.
            summary={"player_message":player,"npc_reply_summary":self._summarize_recent_npc_reply(npc)}
            if elapsed is not None: summary["elapsed_minutes"]=elapsed
            out.append(summary)
        return out

    def _summarize_recent_npc_reply(self, text):
        """Deterministic compact continuity summary, avoiding malformed character truncation."""
        clean=" ".join((text or "").split())
        if not clean: return "No substantive reply recorded."
        words=clean.split()
        return "NPC replied: "+" ".join(words[:12])+("…" if len(words)>12 else "")

    def _clamp_acknowledgement_social(self, player_text, social):
        """Small-model guardrail: trivial acknowledgements cannot create major familiarity."""
        if not social:
            return social
        low=(player_text or "").strip().lower().strip(" .!?")
        acknowledgements={"ok","okay","perfect","fine","right","sure","great","good","yes","no","thanks","thank you","cheers","alright"}
        social=dict(social)
        if low in acknowledgements:
            social["familiarity"]=min(int(social.get("familiarity",0)),1)
            social["trust"]=0
        # Ordinary greetings and weather small talk cannot manufacture trust or major familiarity.
        weather_words={"weather","day","rain","raining","sunny","sun","cloudy","overcast","cold","warm","fine","lovely"}
        tokens=set(re.findall(r"[a-z']+",low))
        greeting=low in {"hi","hello","hey","morning","good morning","good afternoon","good evening"}
        weather_smalltalk=bool(tokens & weather_words) and len(tokens)<=12
        if greeting or weather_smalltalk:
            social["trust"]=0
            social["affinity"]=max(-1,min(int(social.get("affinity",0)),1))
            social["familiarity"]=min(int(social.get("familiarity",0)),1)
        return social

    def _social_memory_supported_by_player(self, player_text, memory):
        """Reject only clearly topic-substituted memories; keep nuanced social summaries."""
        p=set(re.findall(r"[a-z']+",(player_text or "").lower()))
        m=set(re.findall(r"[a-z']+",(memory or "").lower()))
        stop={"the","a","an","i","you","we","it","is","are","was","were","to","for","of","in","on",
              "at","and","or","but","about","asked","player","mentioned","said","talked","speaking",
              "conversation","briefly","earlier","next","what","do","should","any","ideas","me","my"}
        p_content=p-stop
        m_content=m-stop
        plow=(player_text or "").lower()
        mlow=(memory or "").lower()
        # Explicit intent anchors: reject a memory that substitutes an unrelated concrete topic.
        if any(x in plow for x in ("what should i do","ideas what i should do","what do i do next")):
            if any(x in mlow for x in ("weather","morning watch","sunset","rain","temperature")):
                return False
        # Short acknowledgements are already excluded from long-term memory elsewhere.
        # For substantive messages, a memory introducing a wholly disjoint concrete topic
        # is likely model drift. Empty content sets are not rejected.
        if p_content and m_content and not (p_content & m_content):
            social_words={"greeted","greeting","friendly","warm","kind","rude","hostile","apologized",
                          "apology","thanked","gratitude","concern","advice","help","helpful","remember",
                          "remembered","trust","respect","respectful"}
            if not (m_content & social_words):
                return False
        return True

    def _conversation_memory_is_meaningful(self, player_text, social):
        """Keep long-term memory selective; exact recent turns live in conversation_sessions."""
        if not social or not social.get("memory"):
            return False
        text=(player_text or "").strip()
        low=text.lower().strip(" .!?")
        acknowledgements={"ok","okay","perfect","fine","right","sure","great","good","yes","no","thanks","thank you","cheers"}
        if low in acknowledgements:
            return False
        emotional=abs(int(social.get("affinity",0)))+abs(int(social.get("trust",0)))
        return emotional>0 or len(text.split())>=7 or int(social.get("familiarity",0))>=2

    def _append_conversation_exchange(self, npc_id, player_text, npc_reply):
        sessions=self.state.setdefault("conversation_sessions",{}).setdefault(npc_id,[])
        sessions.append({
            "time":self.time_label(),
            "absolute_minute":(int(self.state.get("day",1))-1)*1440+int(self.state.get("minute",0)),
            "player":player_text[:240],
            "npc":npc_reply[:240],
        })
        self.state["conversation_sessions"][npc_id]=sessions[-6:]

    def start_ai_player_conversation(self, npc_id, player_text=None):
        """Generate exactly one NPC reply, grounded in live village and story context."""
        s = self.state
        self.compile_llm_overview()
        npc = s["npcs"][npc_id]
        player_text = (player_text or "Hello.").strip()[:600]
        overview = self.compile_llm_overview()
        ctx = {
            "npc_activity": npc["activity"],
            "location": WORLD[s["location"]]["name"],
            "time": self.time_label(),
            "daypart": self._daypart(),
            "weather": {
                "label": s["weather"].get("label"),
                "temperature_c": s["weather"].get("temperature_c"),
                "wind": s["weather"].get("wind"),
            },
            "village_mood": s["village_brain"]["mood"],
            "npc_memories": s.get("social_memory", {}).get(npc_id, [])[-3:],
            "structured_memory": MEMORY_MODEL.context(s,npc_id,limit=6),
            "npc_cognition": COGNITION_MODEL.context(s,npc_id,limit=6),
            "social_consequences": SOCIAL_CONSEQUENCE_MODEL.context(s,npc_id,limit=6),
            "recent_conversation": self._conversation_recent_exchange_context(npc_id),
            "npc_personality": self._npc_social_personality(npc_id),
            "dialogue_expression": DIALOGUE_EXPRESSION_MODEL.context(s,npc_id),
            "npc_life_context": self.npc_life_context(npc_id),
            "npc_social_web": self.npc_social_context(npc_id),
            "npc_knowledge": self.npc_knowledge_context(npc_id),
            "relationship": {
                "affinity": s["relationships"][npc_id]["affinity"],
                "familiarity": s["relationships"][npc_id]["familiarity"],
                "trust": s["relationships"][npc_id]["trust"],
            },
            "player_style": overview.get("player_style", {}),
            "player_evolving_identity": PLAYER_IDENTITY_MODEL.public_context(s),
            "recurrence_echo": deepcopy(s.get("recurrence",{}).get("npc_echoes",{}).get(npc_id)),
            "recent_player_choices": s.get("llm_context", {}).get("notable_player_choices", [])[-3:],
            "story": self._conversation_story_context(),
            "psychological_stage": s.get("psychological_state", {}).get("stage", "ordinary"),
        }
        result = provider.ask_player_reply(npc["name"], player_text, ctx)
        dialogue = result.get("dialogue") if isinstance(result,dict) else None
        social = result.get("social") if isinstance(result,dict) else None
        social = self._clamp_acknowledgement_social(player_text, social)

        if not dialogue:
            dialogue = self._player_conversation_fallback(npc_id, player_text)

        self.add("You", player_text)
        self.add(npc["name"], dialogue)
        self._append_conversation_exchange(npc_id, player_text, dialogue)
        self.remember_player_choice(f"Said to {npc['name']}: {player_text[:180]}")
        self.branch_score("community",1)

        rel = s["relationships"][npc_id]
        rel["talks"] += 1
        if social:
            memory = social.get("memory") or f"The newcomer spoke with {npc['name']} at {WORLD[s['location']]['name']}."
            reason = "free conversation: " + ", ".join(social.get("tone") or ["neutral"])
            self._update_relationship(
                npc_id, reason,
                social.get("affinity",0),
                social.get("familiarity",0),
                social.get("trust",0)
            )
        else:
            # A failed metadata parse must not discard good dialogue or manufacture
            # positive sentiment. Contact alone adds only slight familiarity.
            memory = f"The newcomer spoke with {npc['name']} at {WORLD[s['location']]['name']}."
            self._update_relationship(npc_id, "shared an ordinary conversation", 0, 1, 0)

        if (self._conversation_memory_is_meaningful(player_text, social)
                and self._social_memory_supported_by_player(player_text, memory)):
            memories=s.setdefault("social_memory", {}).setdefault(npc_id, [])
            normalized=memory.strip().lower().rstrip(".")
            existing={m.strip().lower().rstrip(".") for m in memories[-6:]}
            if normalized and normalized not in existing:
                memories.append(memory[:220])
            s["social_memory"][npc_id] = memories[-12:]
        self.record_world_event(
            f"The newcomer stopped to speak with {npc['name']} at {WORLD[s['location']]['name']}.",
            "conversation", npc_id
        )
        event_id=MEMORY_MODEL.record(s,"conversation",f"The player spoke with {npc['name']} at {WORLD[s['location']]['name']}.",actors=[npc_id],location=s["location"],witnesses=[npc_id],importance=2,tags=["player_contact"])
        COGNITION_MODEL.ingest_event(s,npc_id,event_id)
        if social and social.get("memory") and self._social_memory_supported_by_player(player_text,social.get("memory")):
            MEMORY_MODEL.remember_impression(s,npc_id,social.get("memory"),event_id,0.65)
        # v0.5.2: only explicit, conservatively recognized social acts become structured consequences.
        explicit_act=SOCIAL_CONSEQUENCE_MODEL.extract_explicit_player_act(player_text)
        if explicit_act:
            act_type,act_summary=explicit_act
            act_id=SOCIAL_CONSEQUENCE_MODEL.record_act(s,npc_id,act_type,act_summary,explicit=True)
            if act_id:
                MEMORY_MODEL.record(s,"commitment" if act_type in {"promise","invitation","request"} else "relationship",act_summary,actors=[npc_id],location=s["location"],witnesses=[npc_id],importance=3,tags=["social_act",act_type],metadata={"social_act_id":act_id})
                if act_type=="insult": self._update_relationship(npc_id,"remembered a direct insult",-2,0,-2)
                elif act_type=="apology":
                    resolved=SOCIAL_CONSEQUENCE_MODEL.resolve_grievance(s,npc_id,act_summary)
                    self._update_relationship(npc_id,"received an explicit apology",1,0,1 if resolved else 0)
                elif act_type in {"promise","invitation"}: self._update_relationship(npc_id,"received an explicit social commitment",0,1,1)

    def free_talk(self, npc_id, player_text):
        """Server-side entry point for player-authored ambient conversation."""
        s = self.state
        npc = s.get("npcs", {}).get(npc_id)
        if not npc or not npc.get("visible", True) or npc.get("location") != s["location"]:
            self.add("Narrator", "There is no one here to answer.")
            return self.view()
        if self._story_conversation_required(npc_id):
            # Story-bearing conversations remain authored and cannot be bypassed
            # through the free-text endpoint.
            if npc_id == "jonah":
                self.start_jonah_dialogue()
            elif npc_id == "mara":
                self.start_mara_dialogue()
            return self.view()
        clean = (player_text or "").strip()
        if not clean:
            return self.view()
        self.advance(5)
        self.start_ai_player_conversation(npc_id, clean)
        view = self.view()
        # Explicit foreground exchange contract: the scene dialogue window must show
        # the just-completed free-form conversation even if another UI acknowledgement
        # advanced the ordinary message cursor.
        recent = self.state.get("conversation_sessions", {}).get(npc_id, [])
        if recent:
            exchange = recent[-1]
            view["conversation_exchange"] = {
                "npc_id": npc_id, "npc_name": npc.get("name", npc_id),
                "player": exchange.get("player", clean), "npc": exchange.get("npc", "")
            }
        return view

    def describe_current_village_activity(self):
        """Describe already-simulated state without causing actors to decide again."""
        s=self.state
        here=s["location"]
        visible=[n for n in s["npcs"].values() if n.get("visible",True) and n.get("location")==here]
        nearby=[v for v in s["traffic"].values() if v.get("location")==here]
        if visible:
            for npc in visible[:2]:
                self.add("Bellwether", f"{npc['name']} is {npc['activity']}.")
        if nearby:
            vehicle=nearby[0]
            self.add("Bellwether", f"{vehicle['name']} is nearby, {vehicle['activity']}.")
        if not visible and not nearby:
            self.add("Bellwether", s["ambient"].get("village","The village carries on around you."))

    def _async_state_revision(self):
        s=self.state
        return int(s.get("village_brain",{}).get("pulse_count",0))

    def harvest_async_ai_results(self):
        """Apply completed background choices only on the game thread and only if still legal."""
        s=self.state; applied=0; stale=0
        for job in ASYNC_AI_RUNTIME.harvest():
            kind=job.get("kind"); choice=job.get("result")
            if job.get("error"):
                stale+=1; ASYNC_AI_RUNTIME.record_application(job,"failed"); continue
            before_applied=applied; before_stale=stale
            if kind=="emergent_situation":
                if EMERGENT_SITUATION_MODEL.apply_proposal(s,choice,provider.model_for_task("town_mind")): applied+=1
                else: stale+=1
            elif kind=="npc_goal_reasoning":
                npc=str(job.get("key","")).split(":",1)[1] if ":" in str(job.get("key","")) else ""
                if SOCIAL_OBLIGATION_MODEL.apply_goal(s,npc,choice,provider.model_for_task("town_mind")): applied+=1
                else: stale+=1
            elif kind=="npc_project_reasoning":
                npc=str(job.get("key","")).split(":",1)[1] if ":" in str(job.get("key","")) else ""
                if NPC_PROJECT_MODEL.apply_reasoning(s,npc,choice,provider.model_for_task("town_mind")): applied+=1
                else: stale+=1
            elif kind=="interpretation_review":
                observer=str(job.get("key","")).split(":",1)[1] if ":" in str(job.get("key","")) else "town_mind"
                if INTERPRETATION_MODEL.apply_review(s,observer,choice,provider.model_for_task("town_mind")): applied+=1
                else: stale+=1
            elif kind=="town_mind":
                candidates=TOWN_MIND_MODEL.candidates(s); legal={x.get("id") for x in candidates}
                if choice and choice.get("id") in legal:
                    if TOWN_MIND_MODEL.validate_and_apply(s,choice,provider.model_for_task("town_mind"),"async_review"): applied+=1
                else: stale+=1
            elif kind=="procedural_arc":
                root=PROCEDURAL_ARC_MODEL.migrate(s); legal={x.get("id") for x in PROCEDURAL_ARC_MODEL.candidates(s)}
                if choice and choice.get("id") in legal and len(root.get("active",[]))<PROCEDURAL_ARC_MODEL.MAX_ACTIVE:
                    if PROCEDURAL_ARC_MODEL.start(s,choice.get("id"),provider.model_for_task("procedural_arc")): applied+=1
                else: stale+=1
            elif kind=="ecology_review":
                if choice and ECOLOGY_AI_MODEL.apply(s,choice,provider.model_for_task("weather")): applied+=1
                else: stale+=1
            elif kind=="animal_intention":
                aid=str(job.get("key","")).split(":",1)[1] if ":" in str(job.get("key","")) else None
                if choice and aid and ANIMAL_MODEL.apply_intention(s,aid,choice.get("id"),"llm"): applied+=1
                else: stale+=1
            elif kind=="director_batch":
                proposals=choice if isinstance(choice,dict) else {}
                revision_age=max(0,self._async_state_revision()-int(job.get("revision",0)))
                if revision_age>8:
                    stale+=1
                elif proposals:
                    self.apply_director_proposals(proposals); self.propagate_world_consequences("async_director"); s["ai_runtime"]["world_rounds"]+=1; applied+=1
                    coverage=s.setdefault("ai_runtime",{}).setdefault("coverage", {"last_applied_revision":0,"opportunity_journal":[],"compressed_events":0})
                    covered=int(job.get("revision",0) or 0); coverage["last_applied_revision"]=max(int(coverage.get("last_applied_revision",0) or 0),covered)
                    coverage["opportunity_journal"]=[e for e in coverage.get("opportunity_journal",[]) if int(e.get("revision",0) or 0)>covered]
                else: stale+=1
            if applied>before_applied: ASYNC_AI_RUNTIME.record_application(job,"applied")
            elif stale>before_stale: ASYNC_AI_RUNTIME.record_application(job,"rejected_or_stale")
        rt=s.setdefault("ai_runtime",{}); rt["async_applied"]=rt.get("async_applied",0)+applied; rt["async_stale_or_rejected"]=rt.get("async_stale_or_rejected",0)+stale
        rt["background_worker"]=ASYNC_AI_RUNTIME.status(); return applied

    def queue_animal_intention_review(self, animal_id):
        if self.state.get("diagnostic_mode"): return False
        candidates=ANIMAL_MODEL.legal_intentions(self.state,animal_id)
        if not candidates:return False
        context=deepcopy(ANIMAL_MODEL.compact_context(self.state,animal_id)); frozen=deepcopy(candidates); pulse=self._async_state_revision()
        return ASYNC_AI_RUNTIME.submit(f"animal_intention:{animal_id}","animal_intention",pulse,tuple(x["id"] for x in frozen),lambda: provider.ask_choice("animal_intention","Choose one plausible immediate animal intention. Choose only from the candidates; do not invent state or outcomes.",context,frozen),domain="ecology",priority=15)

    def queue_emergent_situation_review(self):
        if self.state.get("diagnostic_mode"): return False
        rt=EMERGENT_SITUATION_MODEL.migrate(self.state); day=int(self.state.get("day",1))
        if int(rt.get("last_review_day",0))>=day or ASYNC_AI_RUNTIME.has_job("emergent_situation"): return False
        context=EMERGENT_SITUATION_MODEL.context(self.state); frozen=deepcopy(context); pulse=self._async_state_revision()
        return ASYNC_AI_RUNTIME.submit("emergent_situation","emergent_situation",pulse,(day,len(context.get("recent_world_events",[]))),lambda: provider.ask_emergent_situation(frozen),domain="interpretation",priority=46)

    def queue_npc_goal_reasoning(self, npc_id):
        if self.state.get("diagnostic_mode") or npc_id not in SOCIAL_OBLIGATION_MODEL.CORE: return False
        context=SOCIAL_OBLIGATION_MODEL.context_for(self.state,npc_id)
        if not context.get("social_facts") and not context.get("obligations"): return False
        frozen=deepcopy(context); pulse=self._async_state_revision()
        return ASYNC_AI_RUNTIME.submit(f"npc_goal:{npc_id}","npc_goal_reasoning",pulse,(npc_id,self.state.get("day",1),len(context.get("social_facts",[])),len(context.get("obligations",[]))),lambda: provider.ask_npc_goal(npc_id,frozen),domain="interpretation",priority=43)

    def queue_npc_project_reasoning(self, npc_id):
        if self.state.get("diagnostic_mode") or npc_id not in NPC_PROJECT_MODEL.CORE: return False
        context=NPC_PROJECT_MODEL.reasoning_context(self.state,npc_id)
        if not context.get("legal_attempts"): return False
        frozen=deepcopy(context); pulse=self._async_state_revision()
        return ASYNC_AI_RUNTIME.submit(f"npc_project:{npc_id}","npc_project_reasoning",pulse,(npc_id,self.state.get("day",1),len(context["legal_attempts"])),lambda: provider.ask_npc_project(npc_id,frozen),domain="interpretation",priority=44)

    def queue_interpretation_review(self, observer="town_mind"):
        if self.state.get("diagnostic_mode"): return False
        context=INTERPRETATION_MODEL.observer_context(self.state,observer)
        if len(context.get("evidence",[]))<3:return False
        frozen=deepcopy(context); pulse=self._async_state_revision()
        return ASYNC_AI_RUNTIME.submit(f"interpretation:{observer}","interpretation_review",pulse,(observer,self.state.get("day",1),len(context["evidence"])),lambda: provider.ask_interpretation(observer,frozen),domain="interpretation",priority=48)

    def queue_town_mind_review(self, reason="scheduled"):
        if self.state.get("diagnostic_mode"): return False
        s=self.state; tm=s.setdefault("town_mind",TOWN_MIND_MODEL.runtime_defaults()); pulse=self._async_state_revision(); candidates=TOWN_MIND_MODEL.candidates(s); context=TOWN_MIND_MODEL.compact_context(s)
        if not candidates:return False
        tm["review_count"]+=1; tm["last_review_pulse"]=pulse
        frozen_candidates=deepcopy(candidates); frozen_context=deepcopy(context)
        return ASYNC_AI_RUNTIME.submit("town_mind","town_mind",pulse,tuple(sorted(x.get("id") for x in candidates)),lambda: provider.ask_choice("town_mind","Choose one strategic intention for the village simulation. Prefer an intention justified by current state and player pacing. Do not invent facts or events; choose only a direction for specialist systems to consider.",frozen_context,frozen_candidates), domain="strategy", priority=50)

    def run_town_mind_review(self, reason="scheduled"):
        """One bounded strategic review. Town Mind creates intentions, never direct world mutations."""
        s=self.state
        tm=s.setdefault("town_mind", TOWN_MIND_MODEL.runtime_defaults())
        pulse=s.get("village_brain",{}).get("pulse_count",0)
        TOWN_MIND_MODEL.expire(s)
        candidates=TOWN_MIND_MODEL.candidates(s)
        context=TOWN_MIND_MODEL.compact_context(s)
        choice=provider.ask_choice(
            "town_mind",
            "Choose one strategic intention for the village simulation. Prefer an intention justified by current state and player pacing. Do not invent facts or events; choose only a direction for specialist systems to consider.",
            context,candidates
        )
        tm["review_count"]+=1; tm["last_review_pulse"]=pulse
        if choice is None:
            # Deterministic fallback keeps the architecture active without pretending AI succeeded.
            choice=candidates[pulse % len(candidates)] if candidates else None
            model_name="deterministic_fallback"
        else:
            model_name=provider.model_for_task("town_mind")
        accepted=TOWN_MIND_MODEL.validate_and_apply(s,choice,model_name,reason) if choice else False
        if accepted:
            self.record_world_event("The village's underlying pressures have been reconsidered.","town_mind")
        return accepted

    def maybe_run_town_mind(self):
        """Review at the beginning of a run and then infrequently to protect low-end hardware."""
        s=self.state; pulse=s.get("village_brain",{}).get("pulse_count",0)
        tm=s.setdefault("town_mind",TOWN_MIND_MODEL.runtime_defaults())
        due=(tm.get("review_count",0)==0 and pulse>=1) or (pulse-tm.get("last_review_pulse",-999)>=18)
        if due:
            return self.queue_town_mind_review("opening_review" if tm.get("review_count",0)==0 else "periodic_review")
        TOWN_MIND_MODEL.expire(s)
        return False

    def queue_procedural_arc_proposal(self, reason="scheduled"):
        if self.state.get("diagnostic_mode"): return False
        s=self.state; root=PROCEDURAL_ARC_MODEL.migrate(s); candidates=PROCEDURAL_ARC_MODEL.candidates(s); pulse=self._async_state_revision()
        if not candidates or len(root.get("active",[]))>=PROCEDURAL_ARC_MODEL.MAX_ACTIVE:return False
        root["proposal_count"]+=1; root["last_proposal_pulse"]=pulse
        frozen_candidates=deepcopy(candidates); frozen_context=deepcopy(PROCEDURAL_ARC_MODEL.compact_context(s))
        return ASYNC_AI_RUNTIME.submit("procedural_arc","procedural_arc",pulse,tuple(sorted(x.get("id") for x in candidates)),lambda: provider.ask_choice("procedural_arc","Choose one grounded multi-day village social situation that fits current pressures. Select only from the legal templates; do not invent facts, residents, outcomes, or stages.",frozen_context,frozen_candidates), domain="social_arcs", priority=40)

    def run_procedural_arc_proposal(self, reason="scheduled"):
        """Choose one legal multi-day social arc template; no free-form state mutation."""
        s=self.state; root=PROCEDURAL_ARC_MODEL.migrate(s)
        candidates=PROCEDURAL_ARC_MODEL.candidates(s)
        root["proposal_count"]+=1
        root["last_proposal_pulse"]=s.get("village_brain",{}).get("pulse_count",0)
        if not candidates or len(root.get("active",[]))>=PROCEDURAL_ARC_MODEL.MAX_ACTIVE: return False
        choice=provider.ask_choice("procedural_arc","Choose one grounded multi-day village social situation that fits current pressures. Select only from the legal templates; do not invent facts, residents, outcomes, or stages.",PROCEDURAL_ARC_MODEL.compact_context(s),candidates)
        if choice is None:
            choice=candidates[(s.get("day",1)+root["proposal_count"])%len(candidates)]
            model_name="deterministic_fallback"
        else: model_name=provider.model_for_task("procedural_arc")
        arc=PROCEDURAL_ARC_MODEL.start(s,choice.get("id"),model_name)
        if arc: self.record_world_event("A small situation has begun to develop through ordinary village life.","procedural_arc"); return True
        return False

    def maybe_run_procedural_arcs(self):
        """Advance due stages and propose arcs infrequently to protect low-end hardware."""
        s=self.state; root=PROCEDURAL_ARC_MODEL.migrate(s)
        templates={t["id"]:t for t in ARC_TEMPLATES}
        for arc,t,stage in list(PROCEDURAL_ARC_MODEL.due_stages(s)):
            eid=PROCEDURAL_ARC_MODEL.apply_stage(s,arc,t,stage,MEMORY_MODEL,COGNITION_MODEL)
            if eid: self.record_world_event(stage["text"],"procedural_arc")
        pulse=s.get("village_brain",{}).get("pulse_count",0)
        due=(not root.get("active") and pulse>=3) or (len(root.get("active",[]))<PROCEDURAL_ARC_MODEL.MAX_ACTIVE and pulse-root.get("last_proposal_pulse",-999)>=24)
        if due: return self.queue_procedural_arc_proposal("opening_arc" if root.get("proposal_count",0)==0 else "periodic_arc")
        return False

    def queue_ecology_review(self):
        if self.state.get("diagnostic_mode"): return False
        s=self.state; rt=ECOLOGY_AI_MODEL.migrate(s); day=int(s.get("day",1))
        if int(rt.get("last_review_day",0))>=day or ASYNC_AI_RUNTIME.has_job("ecology_review"):return False
        candidates=ECOLOGY_AI_MODEL.candidates(s); context=deepcopy(ECOLOGY_AI_MODEL.context(s))
        return ASYNC_AI_RUNTIME.submit("ecology_review","ecology_review",self._async_state_revision(),tuple(x["id"] for x in candidates),lambda: provider.ask_choice("ecology","Choose the ecological response best supported by season, temperature, weather, soil moisture, drying pressure and garden moisture. This choice governs bounded crop growth, vegetation response and animal movement for the day.",context,candidates),domain="ecology",priority=35)

    def maybe_run_ecology_review(self):
        rt=ECOLOGY_AI_MODEL.migrate(self.state)
        if int(rt.get("last_review_day",0)) < int(self.state.get("day",1)):
            return self.queue_ecology_review()
        return False

    def queue_ai_directors(self, domains, reason="scheduled"):
        if self.state.get("diagnostic_mode"): return False
        """Queue ordinary Director inference without blocking deterministic gameplay."""
        domains=list(dict.fromkeys(domains)); s=self.state
        if not domains: return False
        self.compile_llm_overview()
        frozen_state=deepcopy(s); frozen_overview=deepcopy(getattr(provider,"overview_context",{}))
        coverage=s.setdefault("ai_runtime",{}).setdefault("coverage", {"last_applied_revision":0,"opportunity_journal":[],"compressed_events":0})
        frozen_state["ai_catchup_context"]={"covered_from_revision":coverage.get("last_applied_revision",0),"through_revision":self._async_state_revision(),"meaningful_changes":deepcopy(coverage.get("opportunity_journal",[])[-12:])}
        revision=self._async_state_revision(); signature=tuple(domains)
        def work():
            with provider.scoped_overview_context(frozen_overview):
                return run_specific_round(frozen_state,domains)
        ok=ASYNC_AI_RUNTIME.submit("director_batch","director_batch",revision,signature,work, domain="+".join(domains), priority=20)
        if ok:
            s.setdefault("ai_runtime",{})["last_async_director_reason"]=reason
        return ok

    def run_ai_directors(self, domains, reason="scheduled"):
        """Run one non-reentrant Director batch."""
        s = self.state
        scheduler=s.setdefault("simulation_scheduler", deepcopy(INITIAL_STATE["simulation_scheduler"]))
        if scheduler.get("round_in_progress"):
            scheduler["rounds_skipped_busy"] = scheduler.get("rounds_skipped_busy",0)+1
            pending=scheduler.setdefault("pending_domains",[])
            for domain in domains:
                if domain not in pending: pending.append(domain)
            return False
        scheduler["round_in_progress"]=True
        try:
            self.compile_llm_overview()
            proposals = run_specific_round(s, list(dict.fromkeys(domains)))
        finally:
            scheduler["round_in_progress"]=False
        if not proposals:
            s["ai_runtime"]["failed_rounds"] += 1
            return False
        for proposal in proposals.values():
            trace = proposal.get("_ai_trace")
            if trace:
                trace["reason"] = reason
        self.apply_director_proposals(proposals)
        self.propagate_world_consequences("director")
        s["ai_runtime"]["world_rounds"] += 1
        return True

    def maybe_run_ai_directors(self, run_now=True):
        """Schedule due domains once; coalesce them while a player action advances time."""
        s=self.state
        pulse=s["village_brain"]["pulse_count"]
        scheduler=s.setdefault("simulation_scheduler", deepcopy(INITIAL_STATE["simulation_scheduler"]))
        due=[]
        cadence={"npc":2,"traffic":3,"conversation":4,"weather":12}
        last=scheduler.setdefault("last_director_pulse",{})
        for domain,every in cadence.items():
            if pulse % every == 0 and last.get(domain) != pulse:
                due.append(domain)
                last[domain]=pulse
        if not due:
            return False
        if scheduler.get("advance_active") or not run_now:
            pending=scheduler.setdefault("pending_domains",[])
            for domain in due:
                if domain not in pending:
                    pending.append(domain)
            return False
        return self.queue_ai_directors(due,"normal_gameplay")


    def apply_director_proposals(self, proposals):
        s = self.state
        accepted = []

        pending_traces = {}
        for domain, proposal in proposals.items():
            trace = proposal.pop("_ai_trace", None) if isinstance(proposal, dict) else None
            if trace:
                pending_traces[domain] = trace
        s["ai_events"] = s["ai_events"][-30:]

        weather = proposals.get("weather")
        if weather and weather != s["weather"]:
            previous=s["weather"].get("state")
            temp=float(weather.get("temperature_c", s["weather"].get("temperature_c",10)))
            if temp <= 0 and weather.get("state") in {"light_rain","heavy_rain","rain","showers","drizzle"}:
                weather=dict(weather); weather["state"]="snow"; weather["label"]="Snow"
            s["weather"] = weather
            self.record_world_event(f"Weather changed from {previous} to {weather['state']}.","weather")
            accepted.append("weather")

        npc = proposals.get("npc")
        npc_applied = False
        if npc and npc.get("changes"):
            for change in npc.get("changes", []):
                npc_id = change.get("npc")
                if npc_id not in s["npcs"]:
                    continue
                destination = change.get("destination")
                current_location=s["npcs"][npc_id].get("location")
                if destination in WORLD and npc_transition_is_valid(current_location,destination):
                    s["npcs"][npc_id]["location"] = destination
                elif destination != current_location:
                    self.record_world_event(
                        f"Rejected an implausible movement proposal for {s['npcs'][npc_id]['name']}.",
                        "simulation_guard", npc_id
                    )
                    continue
                if change.get("activity"):
                    s["npcs"][npc_id]["activity"] = change["activity"]
                entry={"time":self.time_label(),"choice":change.get("choice"),"label":change.get("label"),"kind":change.get("kind"),
                       "activity":s["npcs"][npc_id]["activity"],"destination":s["npcs"][npc_id]["location"]}
                s.setdefault("npc_action_history",{}).setdefault(npc_id,[]).append(entry)
                s["npc_action_history"][npc_id]=s["npc_action_history"][npc_id][-8:]
                SOCIAL_OBLIGATION_MODEL.record_intention_outcome(s,npc_id,change.get("choice"),change.get("kind","routine"),s["npcs"][npc_id]["location"])
                self.record_world_event(f"{s['npcs'][npc_id]['name']} is now {s['npcs'][npc_id]['activity']}.","npc",npc_id)
                npc_applied = True
            if npc_applied:
                accepted.append("npc")

        traffic = proposals.get("traffic")
        traffic_applied = False
        if traffic and traffic.get("changes"):
            for change in traffic.get("changes", []):
                vehicle = change.get("vehicle")
                if vehicle not in s["traffic"]:
                    continue
                destination = change.get("destination")
                current_vehicle=dict(s["traffic"][vehicle])
                if not traffic_transition_is_valid(
                    vehicle,current_vehicle,change.get("choice"),destination,s
                ):
                    self.record_world_event(
                        f"Rejected an implausible route transition for {s['traffic'][vehicle]['name']}.",
                        "simulation_guard", vehicle
                    )
                    continue
                if destination in WORLD or destination == "away":
                    s["traffic"][vehicle]["location"] = destination
                if change.get("activity"):
                    s["traffic"][vehicle]["activity"] = change["activity"]
                entry={"time":self.time_label(),"choice":change.get("choice"),"label":change.get("label"),
                       "activity":s["traffic"][vehicle]["activity"],"destination":s["traffic"][vehicle]["location"]}
                s.setdefault("traffic_action_history",{}).setdefault(vehicle,[]).append(entry)
                s["traffic_action_history"][vehicle]=s["traffic_action_history"][vehicle][-8:]
                self.record_world_event(f"{s['traffic'][vehicle]['name']} is {s['traffic'][vehicle]['activity']}.","traffic",vehicle)
                traffic_applied = True
            if traffic_applied:
                accepted.append("traffic")

        conversation = proposals.get("conversation")
        conversation_applied = False
        if conversation and conversation.get("interactions"):
            for interaction in conversation.get("interactions", []):
                participants = interaction.get("participants", [])
                if len(participants) < 2:
                    continue
                if not all(p in s["npcs"] for p in participants):
                    continue
                locations = {s["npcs"][p]["location"] for p in participants}
                if len(locations) != 1:
                    continue
                names = [s["npcs"][p]["name"] for p in participants]
                summary = interaction.get("summary") or interaction.get("topic", "village matters")
                event = f"{' and '.join(names)} talked together at {next(iter(locations))}."
                s["overheard"].append(event)
                self.record_world_event(event, "conversation")
                s["ambient"]["village"] = summary
                lines = interaction.get("dialogue_lines", [])
                if lines:
                    # Surface ambient AI dialogue only when the player is present.
                    if next(iter(locations)) == s["location"]:
                        self.add("Nearby", "You catch part of a conversation.")
                        for line in lines[:8]:
                            if ":" in line:
                                speaker, text = line.split(":", 1)
                                self.add(speaker.strip(), text.strip())
                            else:
                                self.add("Nearby", line)
                    for pid in participants:
                        s["social_memory"].setdefault(pid, []).append(
                            f"Spoke with {', '.join(n for n in names if n != s['npcs'][pid]['name'])}: {summary[:180]}"
                        )
                        s["social_memory"][pid] = s["social_memory"][pid][-12:]
                conversation_applied = True
            if conversation_applied:
                accepted.append("conversation")

        if accepted:
            s["director_status"]["mode"] = "AI-assisted"
            s["director_status"]["last_ai_domains"] = accepted
            s["director_status"]["accepted_proposals"] += len(accepted)

            # Translate state consequences into restrained in-world observations.
            if "weather" in accepted:
                self.add("Bellwether", f"The weather has shifted: {s['weather']['label'].lower()}, {s['weather']['temperature_c']}°C, with {s['weather']['wind']} wind.")
            if "npc" in accepted:
                visible = [n for n in s["npcs"].values() if n.get("location") == s["location"]]
                for npc in visible[:2]:
                    self.add("Bellwether", f"{npc['name']} is {npc['activity']}.")
            if "traffic" in accepted:
                nearby = [v for v in s["traffic"].values() if v.get("location") == s["location"]]
                for vehicle in nearby[:1]:
                    self.add("Bellwether", f"{vehicle['name']} is nearby, {vehicle['activity']}.")
            for domain in accepted:
                trace = pending_traces.get(domain, {})
                if domain == "weather": applied = dict(s["weather"])
                elif domain == "npc": applied = {k:dict(v) for k,v in s["npcs"].items()}
                elif domain == "traffic": applied = {k:dict(v) for k,v in s["traffic"].items()}
                else: applied = {"latest_activity":s["overheard"][-3:]}
                s["ai_events"].append({"time":self.time_label(),"director":domain,"reason":trace.get("reason","unknown"),"raw":trace.get("raw",{}),"repaired":trace.get("repaired",{}),"applied":applied})
            s["ai_events"] = s["ai_events"][-30:]

    def register_investigation_observation(self, entry):
        runtime=self.state.setdefault("mystery_investigation",INVESTIGATION_MODEL.runtime_defaults())
        eid=entry.get("id")
        if not eid: return False
        runtime["observations"].setdefault(eid,deepcopy(entry))
        for mid in INVESTIGATION_MODEL.links_for_evidence(eid):
            prog=runtime["mystery_progress"].setdefault(mid,{"evidence":[],"testimony":[],"hypotheses":[]})
            if eid not in prog["evidence"]: prog["evidence"].append(eid)
        INVESTIGATION_MODEL.refresh(runtime)
        return True

    def record_testimony(self, npc_id, fact_id):
        """Record what an NPC currently believes; testimony is not promoted to truth."""
        if fact_id not in KNOWLEDGE_MODEL.facts or npc_id not in self.state.get("npcs",{}): return False
        beliefs=self.state.setdefault("npc_knowledge",KNOWLEDGE_MODEL.runtime_defaults(list(self.state.get("npcs",{}))))["npcs"].get(npc_id,{}).get("beliefs",{})
        belief=beliefs.get(fact_id)
        if not belief: return False
        runtime=self.state.setdefault("mystery_investigation",INVESTIGATION_MODEL.runtime_defaults())
        key=(npc_id,fact_id,belief.get("variant","truth"))
        if any((x.get("npc_id"),x.get("fact_id"),x.get("variant"))==key for x in runtime["testimony"]): return False
        item={"npc_id":npc_id,"fact_id":fact_id,"variant":belief.get("variant","truth"),"confidence":belief.get("confidence",0),"text":KNOWLEDGE_MODEL.text(fact_id,belief.get("variant","truth")),"day":self.state["day"],"time":self.time_label()}
        runtime["testimony"].append(item)
        for mid in INVESTIGATION_MODEL.links_for_fact(fact_id):
            prog=runtime["mystery_progress"].setdefault(mid,{"evidence":[],"testimony":[],"hypotheses":[]})
            token=f"{npc_id}:{fact_id}:{item['variant']}"
            if token not in prog["testimony"]: prog["testimony"].append(token)
        # Contradiction means differing bounded variants of the same fact, not a canon rewrite.
        variants={x.get("variant") for x in runtime["testimony"] if x.get("fact_id")==fact_id}
        if len(variants)>1 and not any(x.get("fact_id")==fact_id for x in runtime["contradictions"]):
            runtime["contradictions"].append({"fact_id":fact_id,"variants":sorted(variants),"status":"unresolved"})
        INVESTIGATION_MODEL.refresh(runtime)
        return True

    def assess_hypothesis(self, hypothesis_id):
        runtime=self.state.setdefault("mystery_investigation",INVESTIGATION_MODEL.runtime_defaults())
        result=INVESTIGATION_MODEL.assess(hypothesis_id,runtime)
        if not result: return None
        runtime["hypotheses"][hypothesis_id]=result
        mid=result["mystery"]; prog=runtime["mystery_progress"].setdefault(mid,{"evidence":[],"testimony":[],"hypotheses":[]})
        if hypothesis_id not in prog["hypotheses"]: prog["hypotheses"].append(hypothesis_id)
        INVESTIGATION_MODEL.refresh(runtime)
        return deepcopy(result)

    def investigation_overview(self):
        runtime=self.state.setdefault("mystery_investigation",INVESTIGATION_MODEL.runtime_defaults())
        return INVESTIGATION_MODEL.public_overview(runtime)

    def record_evidence(self, evidence_id, title, text, location=None, source="observation"):
        """Add one durable, player-facing observation without duplicating it."""
        inv = self.state["investigation"]
        if any(e["id"] == evidence_id for e in inv["evidence"]):
            return False
        entry = {
            "id": evidence_id, "title": title, "text": text,
            "location": location or self.state["location"],
            "time": self.time_label(), "day": self.state["day"], "source": source,
        }
        inv["evidence"].append(entry)
        inv["evidence"] = inv["evidence"][-40:]
        inv["place_notes"].setdefault(entry["location"], []).append(evidence_id)
        self.add("Notebook", f"{title}: {text}")
        self.record_world_event(f"The newcomer noticed something worth remembering: {title}.", "investigation", "player")
        self.register_investigation_observation(entry)
        self.update_investigation_leads()
        return True

    def add_lead(self, lead_id, title, prompt, evidence_ids):
        inv = self.state["investigation"]
        if any(l["id"] == lead_id for l in inv["leads"]):
            return False
        inv["leads"].append({
            "id": lead_id, "title": title, "prompt": prompt,
            "evidence": list(evidence_ids), "resolved": False,
        })
        self.add("Notebook", f"New question — {title}: {prompt}")
        return True

    def update_investigation_leads(self):
        """Connections arise from accumulated observations, never from arbitrary clicks."""
        ids = {e["id"] for e in self.state["investigation"]["evidence"]}
        if {"green_worn_paths", "noticeboard_names"}.issubset(ids):
            self.add_lead(
                "village_networks", "The village's small circles",
                "Who keeps Bellwether's errands, notices, and routines connected?",
                ["green_worn_paths", "noticeboard_names"]
            )
        if {"cottage_lived_patterns", "eleanor_bookmarks"}.issubset(ids):
            self.add_lead(
                "eleanor_routines", "Eleanor's routines",
                "What habits did Eleanor keep in the cottage, and who would remember them?",
                ["cottage_lived_patterns", "eleanor_bookmarks"]
            )

    def perform_investigation(self, mode):
        s = self.state
        inv = s["investigation"]
        life = s["player_life"]
        loc = s["location"]

        if mode == "review":
            if not inv["evidence"]:
                self.add("Notebook", "You have not written down anything significant yet.")
                return
            latest = inv["evidence"][-5:]
            self.add("Notebook", "You review the last few things you thought worth remembering.")
            for e in latest:
                self.add("Notebook", f"{e['title']} — {e['text']}")
            unresolved = [l for l in inv["leads"] if not l.get("resolved")]
            if unresolved:
                self.add("Notebook", "Open questions: " + "; ".join(l["title"] for l in unresolved) + ".")
            return

        self.branch_score("inquiry",1)
        minutes = 10 if mode == "observe" else 20
        inv["observation_counts"][loc] = inv["observation_counts"].get(loc, 0) + 1
        count = inv["observation_counts"][loc]
        life["attentiveness"] = min(100, life.get("attentiveness", 0) + (2 if mode == "observe" else 4))
        familiarity = life["location_familiarity"].get(loc, 0)

        ordinary = {
            "bus_stop": ("road_timing", "The road has a rhythm", "Long quiet gaps separate the traffic; regular vehicles are easy to distinguish from unfamiliar ones."),
            "village_road": ("road_households", "Doors and errands", "The same few doors account for much of the morning's coming and going."),
            "bakery": ("bakery_rhythm", "The bakery's rhythm", "The busiest moments arrive in short clusters, with quiet intervals Jonah seems able to predict."),
            "village_green": ("green_worn_paths", "Paths across the green", "The palest tracks do not simply cross the grass; they connect the bench, noticeboard, road and cottage path in a practiced circuit."),
            "ashcroft_cottage": ("cottage_lived_patterns", "Patterns in the cottage", "Wear on handles, shelves and floorboards suggests a small set of rooms were used far more often than the rest."),
            "village_shop": ("shop_local_rhythm", "What people actually buy", "The village shop's practical shelves reveal the difference between visitors' wants and residents' routines."),
            "churchyard": ("churchyard_names", "Names that recur", "Several surnames repeat across old stones and current village notices."),
            "riverside_path": ("river_paths", "Paths beside the water", "Some meadow tracks are used daily while others vanish into reeds and nettles."),
            "railway_halt": ("halt_timing", "A sparse timetable", "With so few trains, arrivals and departures become memorable village events."),
            "field_lane": ("field_lane_boundaries", "Hedges older than the road", "The lane follows boundaries that predate the modern road surface; gates and bends preserve an older division of the land."),
            "calder_farm": ("farm_working_rhythm", "A farm clock", "Animal care, deliveries and machinery create a daily rhythm that shifts with weather more than the village timetable."),
            "north_woods": ("woods_path_network", "Tracks beneath the canopy", "Forestry tracks, footpaths and animal trails overlap, but only some routes appear on the public waymarkers."),
            "old_quarry": ("quarry_work_layers", "Work written in stone", "Different drill patterns and terrace cuts show that the quarry was expanded in distinct phases."),
            "quarry_caves": ("cave_worked_natural", "Worked stone and natural passage", "Tool cuts interrupt natural solution channels, showing that quarry workers followed older voids beneath the face."),
        }
        deeper = {
            "bus_stop": ("stop_sightline", "A clear sightline", "From the shelter, anyone waiting can see traffic from the village before the driver can clearly see them."),
            "village_road": ("road_repeated_routes", "Repeated routes", "Several ordinary errands seem to pass the same junction twice rather than taking the shortest path."),
            "bakery": ("bakery_regulars", "Regular habits", "A few orders appear to be prepared before their buyers enter; routine here is social knowledge."),
            "village_green": ("green_bell_sightline", "The green and the bell", "From one side of the oak the church is hidden, but its bell carries across the whole green with surprising clarity."),
            "ashcroft_cottage": ("cottage_threshold_marks", "Marks at the threshold", "The front step is worn more deeply at one side, as though people often paused there before entering or leaving."),
            "village_shop": ("shop_informal_credit", "A pencilled ledger", "A small ledger behind the counter suggests that several households settle ordinary purchases later."),
            "churchyard": ("churchyard_recent_visits", "Fresh visits among old stones", "A few graves are tended with a regularity that contrasts sharply with their age."),
            "riverside_path": ("river_highwater_marks", "Old water lines", "Debris caught above the present bank shows how far the river can rise after sustained rain."),
            "railway_halt": ("halt_regular_waiting", "Signs of regular waiting", "Wear beneath the shelter suggests the same few positions are occupied often despite the sparse service."),
            "field_lane": ("field_lane_repeated_turn", "A repeated turn", "One worn verge path leaves the lane and returns to it without offering an obvious shortcut."),
            "calder_farm": ("farm_boundary_discrepancy", "A boundary that moved", "An old wall line and the working fence disagree by several metres, leaving a narrow strip nobody seems to cultivate."),
            "north_woods": ("woods_waymarker_mismatch", "A missing route", "An old waymarker points toward a path that is absent from the current forestry map but still faintly worn under leaves."),
            "old_quarry": ("quarry_shift_marks", "Marks beyond the last working face", "Numbered paint and tool scars continue farther than the documented final quarry terrace."),
            "quarry_caves": ("cave_acoustic_return", "An echo from the wrong direction", "A sharp sound returns first from deeper in the passage rather than from the open quarry mouth behind you."),
        }

        # Expanded-world locations may not yet have bespoke investigation prose.
        # Keep the globally exposed investigation action valid everywhere instead
        # of crashing when the player observes a newer location.
        place_name = WORLD.get(loc, {}).get("name", loc.replace("_", " ").title())
        evidence = ordinary.get(loc, (
            f"ordinary_{loc}",
            f"The shape of {place_name}",
            f"Small signs of use, weather and repeated passage reveal how {place_name} fits into the village's ordinary routines.",
        ))
        if mode == "search" and (familiarity >= 6 or life["attentiveness"] >= 8 or count >= 2):
            evidence = deeper.get(loc, (
                f"deeper_{loc}",
                f"A detail at {place_name}",
                f"Closer attention reveals a detail at {place_name} that is easy to miss when simply passing through.",
            ))

        self.add("Narrator", "You slow down and pay attention to the place rather than merely passing through it.")
        self.record_evidence(*evidence, location=loc)
        # Preserve useful consequences generated by the living village as notes.
        obs = s.get("location_observations", {}).get(loc)
        if obs:
            recent = obs[-1] if isinstance(obs, list) else obs
            text = recent.get("text", str(recent)) if isinstance(recent, dict) else str(recent)
            self.record_evidence(
                f"event_{loc}_{abs(hash(text)) % 100000}",
                f"Recent activity at {WORLD[loc]['name']}", text, location=loc, source="world_event"
            )

        self.record_player_activity(f"investigate_{mode}", f"{mode}ing {WORLD[loc]['name']}", minutes,
                                    {"attentiveness": life["attentiveness"]})
        self.advance(minutes)
        self.propagate_world_consequences("investigation")

    def record_player_activity(self, activity_id, label, minutes, effects=None):
        """Persist how the player spent time; later systems can react to it."""
        life = self.state["player_life"]
        entry = {
            "day": self.state["day"], "time": self.time_label(),
            "location": self.state["location"], "activity": activity_id,
            "label": label, "minutes": minutes,
        }
        if effects:
            entry["effects"] = effects
        life["activity_history"].append(entry)
        life["activity_history"] = life["activity_history"][-30:]
        if activity_id not in ("investigate_observe","investigate_search"):
            self.remember_player_choice(f"Spent {minutes} minutes {label.lower()} at {WORLD[self.state['location']]['name']}.")
        self.record_world_event(f"The newcomer spent time {label.lower()}.", "player_activity", "player")

    def add_discovery(self, discovery_id, text):
        life = self.state["player_life"]
        if discovery_id in life["discoveries"]:
            return False
        life["discoveries"].append(discovery_id)
        self.add("Observation", text)
        self.record_world_event(text, "discovery", "player")
        return True

    def perform_garden_activity(self, action):
        """Part 4 vertical slice: persistent multi-stage gardening."""
        s=self.state
        if s.get("location") != "ashcroft_cottage": return
        rt=s.setdefault("player_activities",ACTIVITY_MODEL.runtime_defaults())
        g=rt["garden"]
        parts=action.split(":")
        verb=parts[1] if len(parts)>1 else ""
        minutes=10
        if verb=="prepare" and not g["soil_prepared"]:
            minutes=45; g["soil_prepared"]=True; g["soil_condition"]=min(100,g["soil_condition"]+25); g["weeds"]=max(0,g["weeds"]-25)
            self.add("Narrator","You turn the neglected beds a section at a time, lifting roots and stones until three workable plots emerge from the garden's old shape.")
        elif verb=="sow" and len(parts)>2:
            crop_id=parts[2]
            if crop_id not in CROPS or g["seed_stock"].get(crop_id,0)<=0 or not g["soil_prepared"]: return
            try: idx=g["plots"].index(None)
            except ValueError: return
            crop=CROPS[crop_id]; g["seed_stock"][crop_id]-=1
            g["plots"][idx]={"crop_id":crop_id,"growth":0.0,"growth_required":crop["growth_minutes"],"health":100,"sown_day":s["day"]}
            minutes=20; self.add("Narrator",f"You mark a shallow row, sow the {crop['name'].lower()} seeds, cover them carefully, and press the soil down with the flat of your hand.")
        elif verb=="water" and any(g["plots"]):
            minutes=20; g["moisture"]=min(100,g["moisture"]+45)
            self.add("Narrator","You water slowly enough for the soil to drink rather than run. The darkened earth holds the pattern of the rows.")
        elif verb=="tend":
            minutes=30; g["weeds"]=max(0,g["weeds"]-45); g["soil_condition"]=min(100,g["soil_condition"]+4)
            for p in g["plots"]:
                if p: p["health"]=min(100,p.get("health",100)+6)
            self.add("Narrator","You work along the beds by hand, pulling weeds close to the root and checking each planted row before moving on.")
        elif verb=="harvest":
            ready=[(i,p) for i,p in enumerate(g["plots"]) if p and ACTIVITY_MODEL.stage(p)=="ready"]
            if not ready: return
            minutes=25; names=[]
            for i,p in ready:
                crop=CROPS[p["crop_id"]]; amount=max(1,round(crop["yield"]*p.get("health",100)/100))
                g["harvest_store"][p["crop_id"]]=g["harvest_store"].get(p["crop_id"],0)+amount; names.append(f"{amount} {crop['name'].lower()}"); g["plots"][i]=None
            self.add("Narrator","You harvest " + ", ".join(names) + ". What began as work in neglected soil is now food you grew yourself.")
        elif verb=="inspect":
            stages=[]
            for i,p in enumerate(g["plots"],1): stages.append(f"plot {i}: empty" if not p else f"plot {i}: {CROPS[p['crop_id']]['name']} ({ACTIVITY_MODEL.stage(p)})")
            self.add("Garden","; ".join(stages)+f". Soil moisture {round(g['moisture'])}%, weeds {round(g['weeds'])}%.")
        else: return
        g["actions_completed"]+=1
        rt["skills"]["gardening"]=min(100,rt["skills"].get("gardening",0)+1)
        life=s["player_life"]; life["garden_work"]=min(100,life.get("garden_work",0)+(3 if verb!="inspect" else 0))
        if verb!="inspect":
            s["location_state"]["ashcroft_cottage"]["garden_progress"]=min(100,s["location_state"]["ashcroft_cottage"].get("garden_progress",0)+2)
        self.record_player_activity("garden_"+verb,"working in the Ashcroft garden",minutes,{"garden_action":verb,"gardening_skill":rt["skills"]["gardening"]})
        HORROR_AFTERMATH_MODEL.note_recovery_activity(s, "garden")
        self._social_consequences_from_life("garden")
        if verb!="inspect": CONTENT_MODEL.note_activity(s,"garden")
        self.advance(minutes)

    def perform_hobby_activity(self, action):
        """v0.4.2: location-, season- and weather-aware persistent hobbies."""
        from backend.core.activity_model import HOBBY_DISCOVERIES
        s=self.state; ACTIVITY_MODEL.migrate(s)
        rt=s["player_activities"]; h=rt["hobbies"]; loc=s.get("location"); season=s.get("season",{}).get("id","")
        weather=s.get("weather",{}).get("state",""); verb=action.split(":",1)[1] if ":" in action else ""
        rainy=("rain" in weather or weather in {"storm","showers"})
        key={"birdwatch":"birdwatching","forage":"foraging","fish":"fishing","history":"local_history","sketch":"sketching"}.get(verb)
        legal={a for a,_ in ACTIVITY_MODEL.available_hobby_actions(s)}
        if action not in legal or not key: return
        minutes={"birdwatch":45,"forage":60,"fish":90,"history":60,"sketch":50}[verb]
        skill=rt["skills"].get(key,0); coll=h["collections"]; found=None
        if verb=="birdwatch":
            pool=HOBBY_DISCOVERIES["birds"].get(loc,[])
            idx=(s["day"]+h["sessions"][key]+skill//5+(0 if rainy else 1)) % max(1,len(pool))
            if pool:
                found=pool[idx]
                if found not in coll["birds"]: coll["birds"].append(found); self.add("Field Notes",f"You add {found.replace('_',' ')} to your bird list.")
                else: self.add("Narrator",f"You spend a patient while observing {found.replace('_',' ')} behaviour you are beginning to recognise.")
        elif verb=="forage":
            pool=HOBBY_DISCOVERIES["foraged"].get(season,[])
            if pool:
                found=pool[(s["day"]+h["sessions"][key])%len(pool)]; amount=1+(skill//20)
                coll["foraged"][found]=coll["foraged"].get(found,0)+amount
                self.add("Narrator",f"You return with {amount} useful portion{'s' if amount!=1 else ''} of {found.replace('_',' ')}.")
            else:self.add("Narrator","You search carefully, but the season offers little worth taking. Learning when not to harvest is part of knowing a place.")
        elif verb=="fish":
            pool=HOBBY_DISCOVERIES["fish"]; chance=35+skill*2-(20 if weather=="storm" else 0)
            roll=(s["day"]*17+h["sessions"][key]*23+skill*7)%100
            if roll<min(85,chance):
                found=pool[(s["day"]+h["sessions"][key])%len(pool)]; coll["fish"][found]=coll["fish"].get(found,0)+1
                s.setdefault("inventory",[]).append(found.replace("_"," ").title())
                self.add("Narrator",f"Patience pays off: a {found.replace('_',' ')} comes to the bank. You record the catch before packing up.")
            else:self.add("Narrator","The river gives you no catch today, but the time is not empty; you learn a little more about current, shade and patience.")
        elif verb=="history":
            note=HOBBY_DISCOVERIES["history"].get(loc)
            if note and note not in coll["history_notes"]:
                coll["history_notes"].append(note); found=note
                self.add("Local History",{"churchyard_masons_marks":"Repeated mason's marks link several old stones to the same nineteenth-century workshop.","halt_freight_siding":"An old notice confirms that the halt once handled small agricultural freight consignments.","green_old_market_charter":"A copied parish notice refers to a much older seasonal market held on the green.","farm_boundary_ledger":"A copied farm ledger describes a boundary strip that no longer matches the working fence line.","quarry_shift_register":"A surviving shift register records work crews assigned to a terrace beyond the documented final face.","worked_passage_marks":"Local notes describe worked passages following natural cavities beneath the quarry face."}[note])
            else:self.add("Narrator","You compare dates, names and small public records. No revelation arrives, but the village becomes a little less anonymous.")
        elif verb=="sketch":
            sketch=f"{loc}_day_{s['day']}"
            if sketch not in coll["sketches"]: coll["sketches"].append(sketch)
            self.add("Narrator","You sit long enough to draw what is actually in front of you. Looking for proportion and shadow makes familiar details newly specific.")
        h["sessions"][key]+=1; h["last_practised_day"][key]=s["day"]
        rt["skills"][key]=min(100,skill+1+(1 if found else 0))
        total=sum(h["sessions"].values())
        for threshold,label in [(5,"first_hobby_rhythm"),(20,"settled_interests"),(50,"village_naturalist")]:
            if total>=threshold and label not in h["milestones"]: h["milestones"].append(label)
        self.record_player_activity("hobby_"+key,f"practising {key.replace('_',' ')}",minutes,{"hobby":key,"skill":rt["skills"][key],"discovery":found})
        self.advance(minutes); self.propagate_world_consequences("player_activity")

    def perform_job_action(self, action):
        """Part 6 employment actions: applications and bounded scheduled shifts."""
        s=self.state; parts=action.split(":")
        if len(parts)!=3:return
        verb,jid=parts[1],parts[2]
        if verb=="apply":
            ok,message=JOB_MODEL.apply(s,jid); minutes=15
        elif verb=="work":
            ok,message,minutes,wage=JOB_MODEL.work(s,jid)
            if ok:
                s["money"]+=wage; ECONOMY_MODEL.record(s,"wage",wage,jid)
        elif verb=="leave":
            ok,message=JOB_MODEL.leave(s,jid); minutes=15
        else:return
        self.add("Narrator",message)
        if ok:
            self.record_player_activity("job_"+verb,message,minutes,{"job_id":jid,"money":s.get("money",0)})
            if verb=="work": CONTENT_MODEL.note_activity(s,"work")
            self.advance(minutes)

    def perform_economy_action(self, action):
        """Part 5 bounded transactions. Location and opening hours are authoritative."""
        s=self.state; parts=action.split(":")
        if len(parts)<3:return
        verb=parts[1]; loc=s.get("location"); sid=ECONOMY_MODEL.shop_for_location(loc)
        if not sid or not WORLD_MODEL.access_status(loc,s.get("minute",0))[0]:
            self.add("Narrator","The business is not available for trade right now."); return
        ok=False; message="Nothing happens."
        if verb=="buy" and len(parts)==4 and parts[2]==sid:
            ok,message=ECONOMY_MODEL.buy(s,sid,parts[3])
        elif verb=="sell" and len(parts)==3 and SHOPS[sid].get("buys_produce"):
            ok,message=ECONOMY_MODEL.sell_produce(s,parts[2])
        elif verb=="support" and len(parts)==4 and parts[2]==sid:
            ok,message=ECONOMY_MODEL.support_business(s,sid,int(parts[3]))
        self.add("Narrator",message)
        if ok:
            self.record_player_activity("economy_"+verb, message, 10, {"money":s.get("money",0)})
            self.advance(10)

    def perform_content_action(self, action):
        parts=action.split(":")
        if len(parts)!=3:return
        _,kind,item_id=parts
        if kind=="cook": ok,msg,minutes=CONTENT_MODEL.cook(self.state,item_id)
        elif kind=="repair": ok,msg,minutes=CONTENT_MODEL.repair(self.state,item_id)
        elif kind=="home": ok,msg,minutes=CONTENT_MODEL.home_action(self.state,item_id)
        else:return
        self.add("Narrator",msg)
        if ok:
            self.record_player_activity(f"{kind}:{item_id}",msg,minutes,{"content":item_id})
            if kind=="cook": CONTENT_MODEL.note_activity(self.state,"cooked")
            self.branch_score("care",1)
            self.advance(minutes)
            self.propagate_world_consequences("player_activity")

    def perform_life_activity(self, activity_id):
        """Meaningful ordinary activity: time passes, state changes, village lives."""
        s = self.state; life = s["player_life"]; loc = s["location"]
        specs = {
            "tea": ("making tea and sitting with it", 20),
            "tidy": ("tidying part of Ashcroft Cottage", 30),
            "garden": ("working in the Ashcroft garden", 30),
            "read": ("reading quietly from Eleanor's shelves", 25),
            "post": ("checking the post and front step", 10),
            "breakfast": ("having something warm at the bakery", 20),
            "bakery_watch": ("watching the street from the bakery window", 20),
            "bench": ("sitting on the green and watching village life", 25),
            "noticeboard": ("reading the village noticeboard", 15),
            "walk_green": ("walking slowly around the village green", 20),
            "errand": ("running a small household errand", 25),
            "walk_road": ("walking the village road without hurrying", 20),
            "watch_road": ("waiting at the bus stop and watching the road", 20),
            "shop_browse": ("browsing the village shop shelves", 15),
            "newspaper": ("reading the local newspaper", 20),
            "churchyard_walk": ("walking among the old churchyard stones", 20),
            "sit_churchyard": ("sitting quietly beneath the churchyard yews", 20),
            "river_walk": ("walking along the riverside path", 25),
            "watch_water": ("watching the river and meadow", 20),
            "watch_platform": ("waiting on the quiet railway platform", 20),
            "read_timetable": ("studying the railway timetable and notices", 15),
            "field_walk": ("walking the hedgerow lane", 25),
            "watch_fields": ("watching the working fields", 20),
            "farm_observe": ("watching the farm at work", 25),
            "orchard_walk": ("walking the orchard boundary", 25),
            "woods_walk": ("following the woodland track", 35),
            "listen_woods": ("listening beneath the woodland canopy", 20),
            "quarry_walk": ("walking the safe quarry terrace", 30),
            "study_stone": ("studying the exposed limestone", 25),
            "cave_listen": ("listening in the first cave chamber", 20),
            "study_passage": ("examining the worked cave passage", 30),
        }
        allowed = {
            "ashcroft_cottage": {"tea","tidy","garden","read","post"},
            "bakery": {"breakfast","bakery_watch"},
            "village_green": {"bench","noticeboard","walk_green"},
            "village_road": {"errand","walk_road"},
            "bus_stop": {"watch_road"},
            "village_shop": {"shop_browse","newspaper"},
            "churchyard": {"churchyard_walk","sit_churchyard"},
            "riverside_path": {"river_walk","watch_water"},
            "railway_halt": {"watch_platform","read_timetable"},
            "field_lane": {"field_walk","watch_fields"},
            "calder_farm": {"farm_observe","orchard_walk"},
            "north_woods": {"woods_walk","listen_woods"},
            "old_quarry": {"quarry_walk","study_stone"},
            "quarry_caves": {"cave_listen","study_passage"},
            "mill_bridge": {"watch_water","river_walk"}, "orchard_lane": {"orchard_walk","watch_fields"}, "south_pasture": {"field_walk","watch_fields"}, "moor_gate": {"field_walk","watch_fields"}, "ridge_path": {"quarry_walk","watch_fields"}, "east_hamlet": {"walk_road","errand"}, "workshop_yard": {"farm_observe","errand"},
        }
        if activity_id not in allowed.get(loc, set()) or activity_id not in specs:
            return
        label, minutes = specs[activity_id]
        effects = {}

        # Apply the player's immediate choice before time advances; village pulses
        # during the activity then react to a world in which that choice occurred.
        fam = life["location_familiarity"]
        fam[loc] = min(100, fam.get(loc, 0) + (2 if minutes < 20 else 4))
        effects["familiarity"] = fam[loc]
        if activity_id == "tea":
            life["tea_breaks"] += 1; effects["tea_breaks"] = life["tea_breaks"]
            self.add("Narrator", "You make tea and sit with the cup warming both hands. For a little while, the cottage is simply a house.")
        elif activity_id == "tidy":
            life["cottage_care"] = min(100, life["cottage_care"] + 8); effects["cottage_care"] = life["cottage_care"]
            self.add("Narrator", "Dust rises, cloths darken, and one small part of the cottage begins to feel inhabited again.")
        elif activity_id == "garden":
            life["garden_work"] = min(100, life["garden_work"] + 7)
            s["location_state"]["ashcroft_cottage"]["garden_progress"] = min(100, s["location_state"]["ashcroft_cottage"].get("garden_progress",0)+5)
            effects["garden_work"] = life["garden_work"]
            self.add("Narrator", "You pull weeds, loosen compacted soil, and clear enough ground to see the garden's old shape beneath the neglect.")
        elif activity_id == "read":
            life["books_read"] += 1; life["attentiveness"] = min(100, life["attentiveness"]+2); effects["books_read"] = life["books_read"]
            self.add("Narrator", "You choose a book from Eleanor's shelves and read until the sounds outside become part of the room.")
            if life["books_read"] >= 2:
                self.add_discovery("eleanor_bookmarks", "Several of Eleanor's books contain old receipts and pressed leaves used as bookmarks. The dates span years; she seems to have reread the same few volumes often.")
        elif activity_id == "post":
            life["attentiveness"] = min(100, life["attentiveness"]+2)
            self.add("Narrator", "There is no letter today. The stone by the step is damp where the morning has not quite dried.")
        elif activity_id == "breakfast":
            if s["money"] >= 2:
                PLAYER_STATUS_MODEL.eat(s,28)
                s["money"] -= 2; life["meals"] += 1; effects["money"] = s["money"]
                self.add("Narrator", "You spend ฿2 on something warm and eat without rushing.")
            else:
                self.add("Narrator", "You check your pockets and decide to save what little money you have.")
                return
        elif activity_id in ("bakery_watch","bench","walk_green","walk_road","watch_road"):
            life["attentiveness"] = min(100, life["attentiveness"]+3); effects["attentiveness"] = life["attentiveness"]
            messages = {
                "bakery_watch":"You take a place by the window. Bellwether passes in fragments: shopping bags, bicycle wheels, a dog that knows where it is going.",
                "bench":"You sit beneath the old oak. People cross the green on errands that make sense to them and, slowly, begin to make sense to you.",
                "walk_green":"You follow the worn paths around the green, learning which gate sticks and where the ground stays damp.",
                "walk_road":"You walk without a destination. Familiar doors and hedges begin to separate themselves from the blur of arrival.",
                "watch_road":"You wait beneath the shelter. Traffic is sparse enough that every engine can be heard before it appears.",
            }
            self.add("Narrator", messages[activity_id])
        elif activity_id == "noticeboard":
            life["attentiveness"] = min(100, life["attentiveness"]+2)
            self.add("Narrator", "You read the notices instead of merely glancing at them: a jumble sale, a lost glove, choir practice, someone offering ladder repairs.")
            self.add_discovery("noticeboard_names", "A few surnames recur across unrelated notices. Bellwether's clubs, errands, and favours seem to run through the same small circle of households.")
        elif activity_id == "errand":
            if s["money"] >= 1:
                s["money"] -= 1
            life["errands_done"] += 1; effects["errands_done"] = life["errands_done"]
            self.add("Narrator", "You pick up a few ordinary household necessities. It is a small thing, but carrying them back makes your stay feel less temporary.")

        elif activity_id in ("shop_browse","newspaper","churchyard_walk","sit_churchyard","river_walk","watch_water","watch_platform","read_timetable","field_walk","watch_fields","farm_observe","orchard_walk","woods_walk","listen_woods","quarry_walk","study_stone","cave_listen","study_passage"):
            life["attentiveness"] = min(100, life["attentiveness"] + 2)
            effects["attentiveness"] = life["attentiveness"]
            messages = {
                "shop_browse":"You browse slowly enough to notice which shelves are practical, which are hopeful, and which things the shopkeeper expects everyone to need.",
                "newspaper":"You read the local pages over twice. Parish notices and small advertisements reveal more about the surrounding villages than the headlines do.",
                "churchyard_walk":"You walk between stones softened by weather and lichen. Familiar village surnames repeat across generations.",
                "sit_churchyard":"The yews keep the air still. Beyond the wall, Bellwether continues with errands, doors and distant engines.",
                "river_walk":"You follow the river beneath alder branches, learning where the bank is firm and where the meadow path disappears after rain.",
                "watch_water":"The river looks slow until you fix your attention on leaves and foam moving beneath the footbridge.",
                "watch_platform":"You wait without needing a train. The platform gathers distant sounds from fields, rails and the village beyond the meadow.",
                "read_timetable":"The timetable is sparse enough to memorize. Missing one train here can change the shape of an entire day.",
                "field_walk":"You follow the hedge line uphill. The village roofs vanish and reappear between gaps in the hawthorn.",
                "watch_fields":"You stop at a gate. Wind moves differently across each crop and pasture, making the working landscape legible in layers.",
                "farm_observe":"You keep clear of the work and watch the farm's practical rhythm: gates, feed, machinery, weather and unfinished jobs.",
                "orchard_walk":"The orchard is modest and uneven-aged. Fallen fruit, pruning cuts and old boundary stones tell different versions of its history.",
                "woods_walk":"The forestry track bends beneath beech and oak. Side paths are easy to miss until you have passed them.",
                "listen_woods":"You stop moving. Birds, branches and distant machinery separate slowly from the general sound of the wood.",
                "quarry_walk":"You keep to the stable terrace. Rust stains, drill marks and scrub show how quickly industry becomes landscape.",
                "study_stone":"The quarry face preserves bands, fractures and tool scars that reward patient attention.",
                "cave_listen":"Water ticks somewhere beyond the first chamber. Small sounds travel farther underground than you expect.",
                "study_passage":"Worked cuts interrupt the natural limestone. Some are practical; others are harder to place in any obvious sequence.",
            }
            self.add("Narrator", messages[activity_id])

        if activity_id in ("tea","tidy","garden","read","post"):
            self.branch_score("care",1)
        if activity_id in ("bench","noticeboard","errand","shop_browse","newspaper"):
            self.branch_score("community",1)
        if activity_id in ("watch_road","watch_water","read_timetable","churchyard_walk","watch_fields","listen_woods","study_stone","cave_listen","study_passage"):
            self.branch_score("inquiry",1)

        self.record_player_activity(activity_id, label, minutes, effects)
        HORROR_AFTERMATH_MODEL.note_recovery_activity(s, activity_id)
        self._social_consequences_from_life(activity_id)
        self.advance(minutes)
        self.propagate_world_consequences("player_activity")

        # Familiarity rewards sustained ordinary life without forcing story progress.
        if fam[loc] >= 8:
            familiar = {
                "ashcroft_cottage": ("cottage_familiar", "You are beginning to know which floorboards speak and which windows catch the afternoon light."),
                "village_green": ("green_familiar", "The green no longer feels like a landmark on a map. You are beginning to recognize its rhythms."),
                "village_road": ("road_familiar", "You can now place several houses by their gates, gardens, and the sounds that come from behind them."),
                "bakery": ("bakery_familiar", "You are learning the bakery's quieter intervals as well as its busy ones."),
                "bus_stop": ("stop_familiar", "The road beyond the bus stop has begun to feel less like the way out and more like one edge of Bellwether."),
            }
            if loc in familiar:
                self.add_discovery(*familiar[loc])

    def perform(self, action):
        s = self.state
        if action == "new_run": return self.new_game()
        if s.setdefault("danger",DANGER_MODEL.runtime_defaults()).get("status") == "dead" and action != "failure:recover": return self.view()

        if action == "animals:build:coop":
            rt=ANIMAL_MODEL.migrate(s); supplies=s.setdefault("economy",{}).setdefault("household",{}).get("repair_supplies",0)
            if s.get("money",0)>=60 and supplies>=2:
                s["money"]-=60;s["economy"]["household"]["repair_supplies"]-=2;rt["shelters"]["coop"]=True;self.add("Narrator","You finish a modest coop beside the cottage garden. It is small, dry, and ready for a few birds.");self.advance(120)
            else:self.add("Narrator","You need ฿60 and two repair supplies to build the coop.")
        elif action == "animals:build:goat_shed":
            rt=ANIMAL_MODEL.migrate(s); supplies=s.setdefault("economy",{}).setdefault("household",{}).get("repair_supplies",0)
            if s.get("money",0)>=140 and supplies>=4:
                s["money"]-=140;s["economy"]["household"]["repair_supplies"]-=4;rt["shelters"]["goat_shed"]=True;self.add("Narrator","You finish a compact goat shelter beyond the garden beds, sturdy enough for cottage-scale keeping.");self.advance(180)
            else:self.add("Narrator","You need ฿140 and four repair supplies to build the goat shelter.")
        elif action.startswith("animals:buy:"):
            species=action.rsplit(":",1)[1];cost={"chicken":35,"duck":45,"goat":120}[species]
            if s.get("money",0)>=cost:
                s["money"]-=cost;a=ANIMAL_MODEL.add(s,species);self.add("Narrator",f"You bring {a['name'].lower()} home to Ashcroft Cottage. The animal will need food, shelter, and time to trust you.");self.advance(45);self.queue_animal_intention_review(a['id'])
            else:self.add("Narrator",f"You do not have the ฿{cost} needed.")
        elif action == "animals:buy_feed":
            if s.get("money",0)>=12:s["money"]-=12;ANIMAL_MODEL.migrate(s)["feed"]+=10;self.add("Narrator","You buy a sack of feed, enough for several days of cottage-scale animal care.");self.advance(10)
            else:self.add("Narrator","You do not have ฿12 for feed.")
        elif action == "animals:feed":
            rt=ANIMAL_MODEL.migrate(s)
            if rt["feed"]>0:
                for a in rt["animals"].values(): a["hunger"]=max(0,a["hunger"]-20);a["trust"]=min(100,a["trust"]+1)
                self.add("Narrator","You measure out feed and check each animal in turn. The cottage yard settles into the small noises of eating.");self.advance(20)
            else:self.add("Narrator","There is no animal feed stored. The village shop sells small sacks.")
        elif action == "animals:collect":
            got=ANIMAL_MODEL.collect(s)
            if got:self.add("Narrator","You collect " + ", ".join(f"{n} {k.replace('_',' ')}" for k,n in got.items()) + " and carry the produce into the cottage.")
            else:self.add("Narrator","There is nothing ready to collect today.")
            self.advance(10)
        elif action == "animals:spend_time":
            rt=ANIMAL_MODEL.migrate(s)
            for a in rt["animals"].values(): a["trust"]=min(100,a["trust"]+4)
            self.add("Narrator","You spend an unhurried while among the animals, learning which movements startle them and which bring them closer.");self.advance(30)
            for aid in rt["animals"]: self.queue_animal_intention_review(aid)

        elif action == "look":
            self.add("Narrator", WORLD[s["location"]]["description"])
            if s["location"] == "ashcroft_cottage":
                self.add("Narrator", CONTENT_MODEL.seasonal_cottage_text(s))
            self.add("Bellwether", f"{s['ambient']['village']} {s['ambient']['traffic']} {s['ambient']['wildlife']}")
            environmental_note = WORLD_RUNTIME_MODEL.observation(s, s["location"])
            if environmental_note:
                self.add("Narrator", environmental_note)
            self.surface_location_consequence(s["location"])
            self.advance(5)

        elif action.startswith("move:"):
            target = action.split(":", 1)[1]
            if target in WORLD[s["location"]]["exits"].values():
                origin = s["location"]
                journey_plan = TRAVEL_MODEL.plan(s, origin, target, WORLD)
                transport_plan = TRANSPORT_MODEL.journey_modifier(s)
                journey_plan["minutes"] = max(3, round(journey_plan["minutes"] * transport_plan["multiplier"]))
                journey_plan["transport_mode"] = transport_plan["mode"]
                self.advance(journey_plan["minutes"])
                first_journey = TRAVEL_MODEL.complete(s, origin, target, journey_plan)
                TRANSPORT_MODEL.complete_journey(s, journey_plan["minutes"])
                s["location"] = target
                map_state = s.setdefault("map_exploration", deepcopy(INITIAL_STATE["map_exploration"]))
                discovered = map_state.setdefault("discovered_locations", [])
                if target not in discovered:
                    discovered.append(target)
                path_key = "::".join(sorted((origin, target)))
                paths = map_state.setdefault("discovered_paths", [])
                if path_key not in paths:
                    paths.append(path_key)
                self.add("Narrator", f"You make your way to {WORLD[target]['name']}. The journey takes about {journey_plan['minutes']} minutes.")
                if first_journey:
                    self.add("Narrator", TRAVEL_MODEL.first_observation(origin, target))
                journey_encounter = TRAVEL_MODEL.encounter(s, origin, target)
                if journey_encounter:
                    self.add("Narrator", journey_encounter["text"])
                    s.setdefault("encounters", []).append({**journey_encounter, "day":s.get("day"), "minute":s.get("minute"), "origin":origin, "target":target})
                    s["encounters"] = s["encounters"][-60:]
                self.surface_location_consequence(target)
                if target == "village_green" and s["day"] >= 2:
                    for q in s["quests"]["main"]:
                        if q["id"] == "first_morning" and not q["done"]:
                            self.complete("main", "first_morning")
                            self.add("Journal", "Main Story completed: The Morning After.")
                            self.add("Narrator", "The green looks ordinary in the new light. Still, you have the odd feeling that someone was expecting you.")
                if target == "ashcroft_cottage" and not s["flags"]["reached_cottage"]:
                    s["flags"]["reached_cottage"] = True
                    self.complete("main", "arrival")
                    self.reveal("main", "eleanor_letter")
                    self.add("Journal", "Main Story completed: A House Left Waiting.")
                    self.add("Journal", "Main Story added: In Eleanor's Hand.")

        elif action.startswith("talk:"):
            npc_id = action.split(":", 1)[1]
            npc = s.get("npcs", {}).get(npc_id)
            # Re-check co-location server-side because a stale UI must never allow
            # remote conversation after the living simulation has moved somebody.
            if npc and npc.get("visible", True) and npc.get("location") == s["location"]:
                self.advance(5)
                # Preserve authored quest introductions; ordinary/repeat meetings
                # are generated from current world context by the local model.
                if npc_id == "jonah" and not s["flags"]["met_jonah"]:
                    self.start_jonah_dialogue()
                elif npc_id == "mara" and not s["flags"]["met_mara"] and s["flags"].get("mara_intro_available"):
                    self.start_mara_dialogue()
                else:
                    self.start_ai_player_conversation(npc_id)

        elif action.startswith("choice:") and s.get("dialogue"):
            self.advance(5)
            self.resolve_choice(action.split(":", 1)[1])

        elif action.startswith("investigate:"):
            self.perform_investigation(action.split(":", 1)[1])

        elif action == "read_letter" and s["location"] == "ashcroft_cottage":
            self.advance(15)
            s["flags"]["read_letter"] = True
            self.complete("main", "eleanor_letter")
            self.reveal("side", "mara")
            s["flags"]["mara_intro_available"] = True
            s["npcs"]["mara"]["visible"] = True
            self.add("Eleanor's Letter", "If you are reading this, then you came. Put the kettle on before you decide anything important. The house is kinder when it is warm.")
            self.add("Narrator", "Below the signature, in different ink, is a final line: Do not worry if the bells wake you.")
            self.add("Journal", "Main Story completed: In Eleanor's Hand.")
            self.add("Journal", "Side Story added: The Cottage Garden.")
            s["quests"]["main"].append({
                "id": "first_morning",
                "title": "The Morning After",
                "objective": "Sleep, then return to the village green",
                "done": False
            })

        elif action.startswith("arc:help:"):
            arc_id=action.split(":",2)[2]
            eid=PROCEDURAL_ARC_MODEL.involve_player(s,arc_id,MEMORY_MODEL,COGNITION_MODEL)
            if eid:
                self.advance(20)
                self.add("Narrator","You offer practical help. The gesture becomes part of how the situation unfolds.")
                self.record_world_event("The player became involved in a developing village situation.","procedural_arc")

        elif action.startswith("arc:followup:"):
            arc_id=action.split(":",2)[2]
            ok,msg=PROCEDURAL_ARC_MODEL.player_followup(s,arc_id)
            if ok:
                self.advance(20); self.add("Narrator",msg)
                self.record_world_event("The player followed up on a developing village situation.","procedural_arc")

        elif action.startswith("arc:resolve:"):
            arc_id=action.split(":",2)[2]
            ok,msg=PROCEDURAL_ARC_MODEL.player_resolve(s,arc_id,MEMORY_MODEL,COGNITION_MODEL)
            if ok:
                self.advance(25); self.add("Narrator",msg or "The situation reaches a conclusion through your involvement.")
                self.add("Journal","A village side story has been completed.")
                self.record_world_event("The player helped resolve a developing village situation.","procedural_arc")

        elif action.startswith("job:"):
            self.perform_job_action(action)

        elif action.startswith("economy:"):
            self.perform_economy_action(action)

        elif action.startswith("content:"):
            self.perform_content_action(action)

        elif action.startswith("property:"):
            ok,msg,minutes=PROPERTY_MODEL.perform(s,action); self.add("Narrator",msg)
            if ok:
                self.record_player_activity("property",msg,minutes,{"property_action":action})
                self.advance(minutes); self.propagate_world_consequences("property_change")

        elif action.startswith("transport:"):
            ok,msg,minutes=TRANSPORT_MODEL.perform(s,action); self.add("Narrator",msg)
            if ok:
                self.record_player_activity("transport",msg,minutes,{"transport_action":action})
                self.advance(minutes)

        elif action.startswith("business:"):
            ok,msg,minutes=PLAYER_BUSINESS_MODEL.perform(s,action); self.add("Narrator",msg)
            if ok:
                self.record_player_activity("business",msg,minutes,{"business_action":action})
                self.advance(minutes); self.propagate_world_consequences("business_change")

        elif action.startswith("relationship:"):
            ok,msg,minutes=RELATIONSHIP_LIFE_MODEL.perform(s,action); self.add("Narrator",msg)
            if ok:
                self.record_player_activity("relationship",msg,minutes,{"relationship_action":action})
                self.advance(minutes); self.propagate_world_consequences("relationship_change")

        elif action.startswith("resist:"):
            ok,msg,minutes=RESISTANCE_MODEL.perform(s,action); self.add("Narrator",msg)
            if ok:
                self.record_player_activity("resistance",msg,minutes,{"resistance_action":action})
                self.advance(minutes); self.propagate_world_consequences("resistance_action")

        elif action.startswith("status:"):
            ok,msg,minutes=PLAYER_STATUS_MODEL.perform(s,action); self.add("Narrator",msg)
            if ok: self.advance(minutes)

        elif action.startswith("society:greet:"):
            rid=action.split(":",2)[2]; resident=POPULATION_MODEL.migrate(s)["residents"].get(rid)
            if resident and resident.get("location")==s.get("location"):
                self.advance(5); SOCIETY_MODEL.note_encounter(s,rid); LIFE_SIMULATION_MODEL.award(s,2,"ordinary resident contact")
                self.add("Narrator",f"You exchange a few ordinary words with {resident.get('name',rid)} about the day and the village around you.")

        elif action.startswith("lifesim:"):
            ok,msg,minutes=LIFE_SIMULATION_MODEL.perform(s,action)
            self.add("Narrator",msg)
            if ok:
                self.record_player_activity(action,msg,minutes,{"life_simulation":True})
                self.advance(minutes)
                self.propagate_world_consequences("player_activity")

        elif action.startswith("social:greet:"):
            npc_id=action.split(":",2)[2]; npc=s.get("npcs",{}).get(npc_id)
            if npc and npc.get("visible",True) and npc.get("location")==s.get("location"):
                self.advance(5); self._update_relationship(npc_id,"shared an ordinary greeting",1,2,1)
                s["relationships"][npc_id]["talks"]+=1; CONTENT_MODEL.note_activity(s,"social")
                LIFE_SIMULATION_MODEL.award(s,2,"ordinary social contact")
                greeting_lines={
                    "jonah":"Morning. If you need anything practical, ask before I pretend the bakery keeps me too busy.",
                    "mara":"Hello. The day's holding together so far; that's usually enough to work with.",
                    "mrs_ellis":"Good to see you. Ordinary days are worth noticing too, while they remain ordinary.",
                }
                self.add(npc.get("name",npc_id),greeting_lines.get(npc_id,"Hello. Good to see you about the village."))

        elif action.startswith("life:"):
            self.perform_life_activity(action.split(":", 1)[1])

        elif action.startswith("garden:"):
            self.perform_garden_activity(action)

        elif action.startswith("hobby:"):
            self.perform_hobby_activity(action)

        elif action == "ask_village":
            # Observation is read-only with respect to Director state. Time still passes,
            # so already-due simulation can advance naturally through the scheduler.
            self.add("Narrator", "You linger without a destination and watch Bellwether carry on around you.")
            self.describe_current_village_activity()
            self.advance(10)

        elif action == "failure:recover":
            row=FAILURE_RECOVERY_MODEL.recover_from_terminal_failure(s); self.add("Narrator",row["text"])
        elif action == "danger:treat":
            self.treat_injury()

        elif action.startswith("recover:"):
            self.recover_setback(action.split(":",1)[1])

        elif action.startswith("ending:"):
            self.resolve_ending(action.split(":",1)[1])

        elif action.startswith("postgame:"):
            kind=action.split(":",1)[1]
            POSTGAME_MODEL.record(s,kind)
            if kind=="community":
                self.advance(45); self.branch_score("community",1,"Continued contributing to Bellwether after resolution."); self.add("Narrator","You spend part of the day helping with the village's changed routines. Resolution did not make ordinary work disappear.")
            elif kind=="side_mystery":
                self.advance(35); self.add("Journal","A remaining loose end yields another small connection. Not every mystery belonged to the central crisis.")
            else:
                self.advance(40); s["player_life"]["cottage_care"]+=1; self.add("Narrator","You work on the cottage with no crisis forcing your hand. The difference matters.")

        elif action == "rest":
            self.advance(20)
            self.add("Narrator", "You stop for a while and listen. Bellwether is quiet, but never entirely still.")

        elif action == "sleep" and s["location"] == "ashcroft_cottage" and s["flags"]["read_letter"]:
            PLAYER_STATUS_MODEL.sleep(s)
            LIFE_SIMULATION_MODEL.close_day(s)
            day_summary=CONTENT_MODEL.close_day(s)
            if day_summary["variety"] >= 3:
                self.add("Narrator", "The day closes with the satisfying tiredness of a life made from several small things, each of them real.")
            elif day_summary["activities"] == 0:
                self.add("Narrator", "The cottage settles around an almost untouched day. Tomorrow is still open.")
            s["day"] += 1
            POSTGAME_MODEL.daily_tick(s)
            HORROR_AFTERMATH_MODEL.daily_recovery(s)
            for echo in RECURRENCE_MODEL.advance_day(s): self.add(echo["speaker"], echo["text"])
            s["minute"] = 450
            market_update=ECONOMY_MODEL.daily_tick(s)
            property_update=PROPERTY_MODEL.daily_tick(s)
            business_update=PLAYER_BUSINESS_MODEL.daily_tick(s)
            RESISTANCE_MODEL.daily_tick(s)
            pacing_update=PLAYSTYLE_PACING_MODEL.daily_tick(s)
            for emergence in EMERGENT_SITUATION_MODEL.execute(s):
                self.record_world_event("Several ordinary pressures have combined into a new village situation.", "emergent_situation", emergence.get("primitive"))
                CAUSAL_HISTORY_MODEL.link(s,"emergent_primitive",emergence.get("primitive"),[emergence.get("situation")],emergence.get("label","Emergent consequence"),"emergent_situation")
            self.queue_emergent_situation_review()
            # v3.5: Town Mind reviews broadly; one additional fallible observer reviews per day
            # to keep local-CPU demand bounded while allowing models to diverge over time.
            self.queue_interpretation_review("town_mind")
            observer_cycle=("mara","jonah","mrs_ellis","village","chorus")
            secondary=observer_cycle[(int(s["day"])-1)%len(observer_cycle)]
            self.queue_interpretation_review(secondary)
            # Execute yesterday's legal project attempts, then let one core NPC revise reasoning.
            NPC_PROJECT_MODEL.advance_day(s)
            for obligation_event in SOCIAL_OBLIGATION_MODEL.daily_tick(s):
                self.record_world_event("An unmet social obligation has begun to matter.", "social_obligation", obligation_event.get("id"))
            goal_cycle=("mara","jonah","mrs_ellis")
            self.queue_npc_goal_reasoning(goal_cycle[(int(s["day"])-1)%len(goal_cycle)])
            project_cycle=("mara","jonah","mrs_ellis")
            self.queue_npc_project_reasoning(project_cycle[(int(s["day"])-1)%len(project_cycle)])
            town_pressure=TOWN_MIND_MODEL.strategic_daily_tick(s)
            story_response=STORY_CONSCIOUSNESS_INTEGRATION_MODEL.daily_tick(s)
            horror_consequence=SYSTEMIC_HORROR_INTEGRATION_MODEL.daily_tick(s)
            if horror_consequence:
                self.record_world_event("The pressure found a consequence in the life being built here.", "systemic_horror_consequence", horror_consequence.get("target"))
            if story_response:
                self.record_world_event("The village changed how it answered the player’s relationship to the mystery.", "story_consciousness_response", story_response.get("posture"))
            if town_pressure:
                self.record_world_event("The village has begun to lean against the shape of your life.", "town_mind_pressure", town_pressure.get("strategy"))
            RELATIONSHIP_LIFE_MODEL.daily_tick(s)
            JOB_MODEL.daily_recovery(s)
            if market_update:
                fav=market_update.get("favoured_produce","").replace("_"," ")
                self.add("Village", f"The shop board mentions stronger local demand for {fav} today.")
            s["day_events"] = []
            s["village_brain"]["mood"] = "still"
            s["village_brain"]["focus"] = "waking"
            self.add("Narrator", "Night settles over Ashcroft Cottage. When you wake, pale morning light has found the curtains.")
            self.add("Bellwether", "Somewhere in the village, a bakery door opens. A bicycle bell rings once on the road.")
            self.village_pulse()
            healed=DANGER_MODEL.recover_day(s)
            for iid in healed: self.add("Journal",f"Recovered from {DANGER_MODEL.injuries[iid]['label']}.")

        self.evaluate_story_integration()
        self.maybe_apply_controlled_horror()
        PLAYER_IDENTITY_MODEL.refresh(self.state, "player_action")
        self.evaluate_danger()
        self.evaluate_failure_and_recovery()
        self.evaluate_endgame()
        return self.view()

    def acknowledge_messages(self):
        self.migrate_state()
        self.state["ui"]["message_cursor"] = len(self.state["history"])
        return {"ok": True}

    def save(self):
        """Atomic, recoverable save with provenance metadata and one last-good backup."""
        SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.compile_llm_overview()
        version=(ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.state.setdefault("save_meta", {}).update({"schema": 1, "game_version": version, "saved_day": self.state.get("day",1), "saved_minute": self.state.get("minute",0)})
        tmp=SAVE_PATH.with_suffix(SAVE_PATH.suffix+".tmp")
        backup=SAVE_PATH.with_suffix(SAVE_PATH.suffix+".bak")
        payload=json.dumps(self.state,indent=2)
        tmp.write_text(payload,encoding="utf-8")
        json.loads(tmp.read_text(encoding="utf-8"))
        if SAVE_PATH.exists():
            backup.write_bytes(SAVE_PATH.read_bytes())
        os.replace(tmp,SAVE_PATH)
        return {"ok": True, "message": "Game saved safely.", "view": self.view()}

    def load_payload(self, loaded):
        """Load a user-supplied portable JSON save after structural validation."""
        if not isinstance(loaded, dict):
            return {"ok": False, "message": "Save file is not a JSON object.", "view": self.view()}
        required = {"day", "minute", "location", "history"}
        missing = sorted(required - set(loaded))
        if missing:
            return {"ok": False, "message": "Save file is missing required game state: " + ", ".join(missing), "view": self.view()}
        self.state = deepcopy(loaded)
        self._overview_cache_key=None; self._overview_cache=None
        self.migrate_state()
        provider.recent_call_memory = deepcopy(self.state.get("llm_context",{}).get("session_summary",[]))[-12:]
        self.state["ui"]["message_cursor"] = max(0, len(self.state["history"]) - 3)
        self.compile_llm_overview()
        return {"ok": True, "message": "Portable save loaded.", "view": self.view()}

    def load(self):
        backup=SAVE_PATH.with_suffix(SAVE_PATH.suffix+".bak")
        source=SAVE_PATH
        if not source.exists():
            return {"ok": False, "message": "No save exists yet.", "view": self.view()}
        try:
            loaded=json.loads(source.read_text(encoding="utf-8"))
            recovered=False
        except (json.JSONDecodeError, OSError):
            if not backup.exists():
                return {"ok": False, "message": "The save is damaged and no backup is available.", "view": self.view()}
            loaded=json.loads(backup.read_text(encoding="utf-8")); recovered=True
        self.state = loaded
        self._overview_cache_key=None; self._overview_cache=None
        self.migrate_state()
        provider.recent_call_memory = deepcopy(self.state.get("llm_context",{}).get("session_summary",[]))[-12:]
        # Loaded games show their latest scene, not the entire lifetime transcript.
        self.state["ui"]["message_cursor"] = max(0, len(self.state["history"]) - 3)
        self.compile_llm_overview()
        return {"ok": True, "message": "Game loaded from backup." if recovered else "Game loaded.", "view": self.view()}

    def reset_fresh(self):
        """Start a genuinely fresh game without recurrence carry-over."""
        self.state=deepcopy(INITIAL_STATE)
        self._overview_cache_key=None; self._overview_cache=None
        provider.recent_call_memory=[]
        self.initialize_season()
        self.compile_llm_overview()
        return {"ok": True, "message": "Fresh game started.", "view": self.view()}

    def new_game(self):
        previous_state = deepcopy(self.state)
        recurrence = RECURRENCE_MODEL.carry_forward(previous_state)
        previous = deepcopy(previous_state.get("llm_context", {}))
        archive = deepcopy(previous.get("run_history", []))
        if previous.get("last_compiled"):
            archive.append({
                "ended_at": previous.get("last_compiled"),
                "story_summary": previous.get("story_summary"),
                "player_style": previous.get("player_style"),
                "notable_player_choices": previous.get("notable_player_choices", [])[-8:],
                "story_beats": previous.get("story_beats", [])[-6:],
            })
        self.state = deepcopy(INITIAL_STATE)
        RECURRENCE_MODEL.apply_to_new_run(self.state, recurrence)
        self._overview_cache_key=None; self._overview_cache=None
        self.state["llm_context"]["run_history"] = archive[-5:]
        provider.recent_call_memory = []
        self.initialize_season()
        for echo in RECURRENCE_MODEL.opening_echoes(recurrence):
            self.add("Narrator", echo)
        if recurrence.get("npc_echoes"):
            self.add("Bellwether", "Somewhere in the village, recognition has survived without a memory attached to it.")
        self.compile_llm_overview()
        return self.view()

game = Game()
