from backend.ai.provider import provider
from backend.core.dialogue_expression_model import DIALOGUE_EXPRESSION_MODEL
from backend.core.npc_model import NPC_MODEL
from backend.ai.repair import LABEL
from backend.core.world_model import WORLD_MODEL
from backend.core.purpose_model import PURPOSE_MODEL
from backend.core.town_mind_model import TOWN_MIND_MODEL
import random

WEATHER_TRANSITIONS={
 "clear":["clear","soft_overcast","light_rain","mist","snow"],
 "soft_overcast":["soft_overcast","clear","light_rain","heavy_rain","mist"],
 "light_rain":["light_rain","soft_overcast","heavy_rain","mist","clear"],
 "heavy_rain":["heavy_rain","light_rain","storm","soft_overcast"],
 "storm":["storm","heavy_rain","light_rain","soft_overcast"],
 "snow":["snow","soft_overcast","mist","clear"],
 "mist":["mist","soft_overcast","light_rain","clear"],
}

def weather_round(s):
    cur=s["weather"]
    states=WEATHER_TRANSITIONS.get(cur["state"],list(LABEL))
    season_id=s.get("season",{}).get("id","")
    if "winter" not in season_id:
        states=[x for x in states if x != "snow"]
    if "summer" not in season_id:
        states=states
    candidates=[{"id":x,"label":LABEL[x],"value":x} for x in states]
    season=s.get("season",{})
    minute=s["minute"]
    hour=(minute % 1440)/60
    low,high=season.get("temperature_range_c",[5,18])
    if hour < 6: phase=.05
    elif hour < 15: phase=.05+.95*((hour-6)/9)
    else: phase=max(.05,1-.95*((hour-15)/9))
    ctx={
        "day":s["day"],"time_minute":minute,"hour_local":round(hour,2),
        "season":season,
        "season_temperature_range_c":[low,high],
        "diurnal_position":"warming toward afternoon" if 6 <= hour < 15 else "cooling toward night",
        "current_weather":cur,
        "village_mood":s["village_brain"]["mood"],
        "recent_events":s.get("world_events",[])[-1:],
        "town_mind_intentions":TOWN_MIND_MODEL.director_context(s),
        "catchup_changes":s.get("ai_catchup_context",{}).get("meaningful_changes",[])[-4:]
    }
    choice=provider.ask_choice(
        "weather",
        "Choose the next plausible UK-like weather state. Respect season, time of day, recent continuity and maritime changeability.",
        ctx,candidates
    )
    if not choice:return None
    state=choice["value"]
    offsets={"clear":1.5,"soft_overcast":0,"light_rain":-1.5,"heavy_rain":-2.5,"mist":-1,"snow":-3.5,"storm":-4}
    base=low+(high-low)*phase
    target=int(round(max(low-2,min(high+2,base+offsets[state]))))
    current=int(cur.get("temperature_c",target))
    temp=current + (1 if target>current else -1 if target<current else 0)
    wind={"clear":"light","soft_overcast":"light","light_rain":"gentle","heavy_rain":"brisk","mist":"still","snow":"light to brisk","storm":"strong and gusting"}[state]
    return {"choice":choice["id"],"label":choice["label"]},{"state":state,"label":LABEL[state],"temperature_c":temp,"wind":wind}

def _candidate(id,label,activity,destination,kind):
    return {"id":id,"label":label,"activity":activity,"destination":destination,"kind":kind}

def _dedupe(items):
    seen=set(); out=[]
    for x in items:
        key=(x["activity"].strip().lower(),x["destination"])
        if key not in seen:
            seen.add(key); out.append(x)
    return out

def npc_candidates(npc_id,npc,s):
    """Build a rich 15-20 action pool. Variation stays inside character, place and time constraints."""
    here=npc["location"]; activity=npc["activity"]
    c=[_candidate("continue",f"Continue {activity}",activity,here,"continuity")]
    if npc_id=="jonah":
        c += [
          _candidate("oven_check","Check the ovens and turn the next batch","checking the ovens and turning the next batch","bakery","work"),
          _candidate("serve_counter","Serve whoever is waiting at the counter","serving customers at the bakery counter","bakery","work"),
          _candidate("knead_batch","Start kneading the next bread batch","kneading the next batch of bread","bakery","work"),
          _candidate("cooling_racks","Move fresh loaves onto the cooling racks","arranging fresh loaves on the cooling racks","bakery","work"),
          _candidate("inventory","Check flour, yeast, and morning supplies","checking bakery supplies and making a short list","bakery","work"),
          _candidate("sweep_step","Sweep flour and crumbs from the bakery step","sweeping the bakery step between customers","bakery","chore"),
          _candidate("bread_green","Take a bread delivery toward the green","carrying a bread delivery across the village","village_green","delivery"),
          _candidate("bread_road","Make a bread delivery along the village road","making a bread delivery along the village road","village_road","delivery"),
          _candidate("supplier_errand","Collect a small bakery supply order","collecting supplies for the bakery","village_road","errand"),
          _candidate("tea_break","Take a brief tea break","taking a brief tea break before returning to work",here,"rest"),
          _candidate("door_chat","Step outside for a brief word with a passer-by","chatting briefly outside the bakery","bakery","social"),
          _candidate("green_break","Walk to the green for a short break","taking a short break on the village green","village_green","rest"),
          _candidate("return_bakery","Return to the bakery before the next batch","returning to the bakery to tend the next batch","bakery","work"),
          _candidate("window_display","Rearrange the bakery window display","rearranging loaves and pastries in the bakery window","bakery","work"),
          _candidate("order_book","Check the day's delivery orders","checking the bakery order book","bakery","work"),
          _candidate("ask_news","Ask a familiar villager how their morning is going","catching up briefly with a familiar villager",here,"social"),
          _candidate("fresh_air","Take five minutes of fresh air nearby","taking a few minutes of fresh air",here,"rest"),
        ]
    elif npc_id=="mara":
        c += [
          _candidate("weed_beds","Clear weeds from another garden bed","clearing weeds from an overgrown garden bed","ashcroft_cottage","work"),
          _candidate("inspect_wall","Inspect the ivy along the cottage wall","checking the ivy and old stonework","ashcroft_cottage","work"),
          _candidate("prune","Prune back an overgrown shrub","cutting back an overgrown garden shrub","ashcroft_cottage","work"),
          _candidate("water","Water the plants that still look healthy","watering the plants that have survived","ashcroft_cottage","work"),
          _candidate("tools","Clean and sort the garden tools","cleaning soil from the garden tools","ashcroft_cottage","chore"),
          _candidate("compost","Gather cuttings for a compost pile","gathering garden cuttings into a compost pile","ashcroft_cottage","work"),
          _candidate("garden_plan","Sit on the step and plan the next garden bed","making notes about restoring the cottage garden","ashcroft_cottage","planning"),
          _candidate("supplies","Walk to the village road for garden supplies","collecting a few garden supplies","village_road","errand"),
          _candidate("green_walk","Walk to the green to clear her head","taking a quiet walk across the village green","village_green","rest"),
          _candidate("ask_advice","Ask someone local about the neglected garden","asking a villager what they remember about the cottage garden","village_green","social"),
          _candidate("check_gate","Repair and test the sticking garden gate","working on the sticking garden gate","ashcroft_cottage","chore"),
          _candidate("sweep_path","Sweep soil and leaves from the cottage path","clearing leaves and soil from the cottage path","ashcroft_cottage","chore"),
          _candidate("tea_step","Take tea on the cottage step","resting on the cottage step with a cup of tea","ashcroft_cottage","rest"),
          _candidate("road_errand","Run a small household errand","running a small household errand","village_road","errand"),
          _candidate("look_boundary","Walk the garden boundary and inspect the hedges","checking the cottage garden boundary and hedges","ashcroft_cottage","work"),
          _candidate("seed_notes","Make a list of seeds and plants to find","writing a list of seeds and plants for the garden","ashcroft_cottage","planning"),
          _candidate("brief_chat","Stop for a brief ordinary chat with a neighbour","having a brief chat with a neighbour",here,"social"),
        ]
    elif npc_id=="mrs_ellis":
        c += [
          _candidate("shopping_list","Continue checking items from her shopping list","checking items from a folded shopping list","village_road","errand"),
          _candidate("groceries_home","Carry the shopping home by way of the green","walking homeward with her shopping","village_green","routine"),
          _candidate("window_shop","Pause to look in a shop window","pausing to look in one of the shop windows","village_road","routine"),
          _candidate("post_errand","Take care of a small postal errand","taking care of a small postal errand","village_road","errand"),
          _candidate("green_bench","Sit on the green for a short rest","resting for a few minutes on the village green","village_green","rest"),
          _candidate("greet_neighbor","Stop to greet a familiar neighbour","exchanging a few words with a familiar neighbour",here,"social"),
          _candidate("remember_item","Double back for something forgotten","doubling back along the road for a forgotten item","village_road","errand"),
          _candidate("bakery_stop","Stop by the bakery","calling briefly at the bakery","bakery","errand"),
          _candidate("weather_chat","Make small talk about the weather","chatting with someone about the morning weather",here,"social"),
          _candidate("check_notice","Read the village noticeboard","reading the notices posted near the green","village_green","routine"),
          _candidate("slow_walk","Take the longer way across the green","walking at an unhurried pace across the green","village_green","routine"),
          _candidate("carry_help","Offer a neighbour a hand with a small parcel","helping a neighbour carry a small parcel","village_road","social"),
          _candidate("rest_road","Pause for a moment before continuing errands","taking a short pause between errands","village_road","rest"),
          _candidate("homeward","Finish errands and start heading home","heading home after finishing the morning errands","village_green","routine"),
          _candidate("ask_news","Ask after someone she has not seen this morning","asking a neighbour after someone she knows",here,"social"),
          _candidate("tidy_bag","Repack her shopping bag before continuing","repacking her shopping bag and checking the list","village_road","chore"),
          _candidate("ordinary_round","Continue her ordinary round through the village","continuing her ordinary morning round","village_road","routine"),
        ]
    else:
        c += [_candidate(f"local_{i}",label,act,dest,kind) for i,(label,act,dest,kind) in enumerate([
          ("Take a short walk nearby","taking a short walk",here,"routine"),("Visit the village green","walking across the village green","village_green","social"),
          ("Run an errand on the village road","running a village errand","village_road","errand"),("Pause for a cup of tea","taking a short tea break",here,"rest"),
          ("Greet someone nearby","chatting briefly with someone nearby",here,"social"),("Check on a small household task","taking care of a household task",here,"chore"),
          ("Take the long way around","walking the longer route through the village","village_green","routine"),("Stop to read the noticeboard","reading the village noticeboard","village_green","routine"),
          ("Collect a small parcel","collecting a small parcel","village_road","errand"),("Rest for a few minutes","resting for a few minutes",here,"rest"),
          ("Look in at the bakery","calling briefly at the bakery","bakery","errand"),("Finish a delayed chore","finishing a small delayed chore",here,"chore"),
          ("Ask a neighbour about their morning","catching up with a neighbour",here,"social"),("Walk toward the shops","walking toward the shops","village_road","errand"),
          ("Spend a little time on the green","passing a little time on the village green","village_green","rest"),("Return to the current task","returning attention to the current task",here,"continuity")])]
    # Shared village-scale possibilities make expanded geography part of daily routines.
    c += [
      _candidate("visit_shop","Call at the village shop","calling at the village shop","village_shop","errand"),
      _candidate("churchyard_path","Take the path by the churchyard","walking quietly through the churchyard","churchyard","routine"),
      _candidate("river_walk_shared","Walk down toward the river","taking a walk along the riverside path","riverside_path","rest"),
      _candidate("station_errand","Go toward the railway halt","walking toward Bellwether Halt","railway_halt","errand"),
    ]
    return _dedupe(c)[:20]


def _history_ids(history):
    return [x.get("choice") for x in history if isinstance(x,dict) and x.get("choice")]

def _shortlist_candidates(candidates, history, current_activity, current_location, minimum=5, maximum=8):
    """Filter repetition and semantic no-op choices before spending an LLM call.

    The larger 15–20 option libraries remain as world-authoring pools. Qwen sees a
    smaller varied shortlist selected from currently plausible non-repetitive choices.
    """
    candidates=_dedupe(candidates)
    recent=_history_ids(history)
    recent2=set(recent[-2:])
    current_noops=[
        c for c in candidates
        if c.get("activity")==current_activity and c.get("destination")==current_location
    ]
    fresh=[
        c for c in candidates
        if c.get("id") not in recent2
        and not (c.get("activity")==current_activity and c.get("destination")==current_location)
    ]
    # Prefer distinct kinds and destinations before filling remaining slots.
    rng=random.SystemRandom()
    rng.shuffle(fresh)
    selected=[]; seen_kinds=set(); seen_destinations=set()
    for c in fresh:
        kind=c.get("kind","routine"); dest=c.get("destination")
        if kind not in seen_kinds or dest not in seen_destinations:
            selected.append(c); seen_kinds.add(kind); seen_destinations.add(dest)
        if len(selected)>=maximum: break
    for c in fresh:
        if c not in selected:
            selected.append(c)
        if len(selected)>=maximum: break

    # If filtering was too aggressive, restore older (not immediately repeated) options.
    if len(selected)<minimum:
        refill=[c for c in candidates if c not in selected and c.get("id") not in recent2]
        rng.shuffle(refill)
        selected.extend(refill[:minimum-len(selected)])
    # Continuity is allowed as one fallback choice, but no longer dominates every menu.
    if len(selected)<minimum and current_noops:
        selected.append(current_noops[0])
    return selected[:maximum]

def _bounded_choice(director, question, ctx, candidates):
    """Avoid an LLM round trip when filtering leaves no genuine decision."""
    if not candidates:
        return None
    if len(candidates)==1:
        choice=candidates[0]
        provider.remember_call(director,{
            "type":"deterministic_choice","choice":choice.get("id"),"label":choice.get("label")
        })
        return choice
    return provider.ask_choice(director,question,ctx,candidates)


NPC_ADJACENCY = WORLD_MODEL.npc_adjacency


def _npc_transition_candidates(npc, candidates):
    """Keep NPC movement local: remain here or move across one world edge per decision."""
    current=npc.get("location")
    allowed={current} | NPC_ADJACENCY.get(current,set())
    valid=[c for c in candidates if c.get("destination") in allowed]
    return valid if valid else [c for c in candidates if c.get("destination")==current] or candidates

def _traffic_transition_candidates(vid, v, candidates):
    """Constrain vehicle choices to a plausible next route phase, not any class-valid state."""
    loc=v.get("location")
    activity=v.get("activity","").lower()
    if vid=="train":
        if loc=="railway_halt":
            allowed={"rail_stop","rail_board","rail_platform_wait","rail_depart","rail_whistle_depart"}
        elif any(x in activity for x in ("approach","resum","signal")):
            allowed={"rail_approach","rail_signal_wait","rail_slow","rail_arrive","rail_minor_delay","rail_resume"}
        else:
            allowed={"rail_approach","rail_signal_wait","rail_pass","rail_distant","rail_return_window","rail_schedule"}
    elif vid=="delivery_van":
        if loc=="away":
            allowed={"van_approach","van_outward","van_return"}
        elif loc=="village_green":
            allowed={"van_green","van_green_leave","van_break"}
        elif loc=="village_shop":
            allowed={"van_shop","van_resume","van_depart"}
        else:
            allowed={"van_road","van_unload","van_shop","van_green","van_wait","van_slow",
                     "van_pull_in","van_repack","van_depart","van_delay","van_break"}
    else:
        if loc=="away":
            allowed={"bus_approach","bus_return","bus_outward","bus_next","bus_steady"}
        elif loc=="village_green":
            allowed={"bus_green_edge","bus_yield","bus_road","bus_outward","bus_turn"}
        else:
            allowed={"bus_road","bus_slow","bus_stop","bus_board","bus_wait","bus_depart",
                     "bus_green_edge","bus_delay","bus_resume","bus_outward","bus_turn","bus_steady"}
    valid=[c for c in candidates if c.get("id") in allowed]
    return valid if valid else candidates


def npc_transition_is_valid(current_location, destination):
    return destination in ({current_location} | NPC_ADJACENCY.get(current_location,set()))

def traffic_transition_is_valid(vid, vehicle, choice_id, destination, state):
    candidates=traffic_candidates(vid,vehicle,state)
    allowed=_traffic_transition_candidates(vid,vehicle,candidates)
    return any(c.get("id")==choice_id and c.get("destination")==destination for c in allowed)

def npc_round(s):
    ids=list(s["npcs"]); npc_id=ids[s["village_brain"]["pulse_count"]%len(ids)]
    npc=s["npcs"][npc_id]
    history=s.get("npc_action_history",{}).get(npc_id,[])
    plausible=_npc_transition_candidates(npc, npc_candidates(npc_id,npc,s))
    # v0.8.3: witnessed anomalies can cause short-lived, bounded place avoidance.
    aftermath=s.get("horror_aftermath",{}).get("npc_aftermath",{}).get(npc_id,{})
    avoid=aftermath.get("avoid_locations",{}); day=int(s.get("day",1))
    filtered=[c for c in plausible if int(avoid.get(c.get("destination"),0)) < day or c.get("destination")==npc.get("location")]
    if filtered: plausible=filtered
    purpose_ranked=PURPOSE_MODEL.shortlist(npc_id, plausible, s, limit=12) if npc_id in NPC_MODEL.npcs else plausible
    candidates=_shortlist_candidates(
        purpose_ranked, history, npc["activity"], npc["location"]
    )
    nearby_npcs=[
        {"id":other_id,"name":other["name"],"activity":other["activity"]}
        for other_id,other in s["npcs"].items()
        if other_id!=npc_id and other.get("location")==npc.get("location")
    ][:3]
    ctx={"npc_id":npc_id,"name":npc["name"],"current_location":npc["location"],"current_activity":npc["activity"],
         "time_minute":s["minute"],"weather":s["weather"],"village_mood":s["village_brain"]["mood"],
         "village_focus":s["village_brain"].get("focus"),"memories":s.get("social_memory",{}).get(npc_id,[])[-4:],
         "recent_actions":history[-4:],
         "nearby_npc_activity":nearby_npcs,
         "recent_world_events":s.get("world_events",[])[-3:],
         "recent_encounters":[e for e in s.get("encounters",[])[-10:] if npc_id in e.get("participants",[])][-4:],
         "place_state":s.get("location_state",{}).get(npc["location"],{}),
         "authored_identity":NPC_MODEL.dialogue_identity(npc_id) if npc_id in NPC_MODEL.npcs else {},
         "personal_life":s.get("npc_lives",{}).get(npc_id,{}),
         "purpose_constraints":NPC_MODEL.purpose_context(npc_id,s["minute"],s["weather"]["state"]) if npc_id in NPC_MODEL.npcs else {},
         "purpose_plan":PURPOSE_MODEL.context(npc_id,s,plausible) if npc_id in NPC_MODEL.npcs else {},
         "town_mind_intentions":TOWN_MIND_MODEL.director_context(s),
         "horror_aftermath":{"strain":aftermath.get("strain",0),"temporary_avoidance":avoid},
         "catchup_changes":s.get("ai_catchup_context",{}).get("meaningful_changes",[])[-5:]}
    instruction=(f"Choose what {npc['name']} should do next. Pick one plausible action that makes the village feel alive. "
                 "Respect authored identity, personal needs, obligations, occupation, location, time, memories and continuity, but introduce grounded variety. "
                 "Strongly avoid repeating recent action IDs or generic loops unless circumstances clearly demand it.")
    choice=_bounded_choice("npc",instruction,ctx,candidates)
    if not choice:return None
    raw={"npc":npc_id,"choice":choice["id"],"label":choice["label"]}
    repaired={"changes":[{"npc":npc_id,"choice":choice["id"],"label":choice["label"],"kind":choice.get("kind","routine"),
                           "activity":choice["activity"],"destination":choice["destination"]}]}
    return raw,repaired

def traffic_candidates(vid,v,s):
    """Vehicle-class-specific state libraries.

    Buses and vans use roads/green/away. Trains use only railway_halt/away,
    preventing physically impossible road and village-green train states.
    """
    loc=v["location"]
    if vid=="train":
        return [
          {"id":"rail_approach","label":"Approach Bellwether along the line","activity":"approaching Bellwether along the railway","destination":"away"},
          {"id":"rail_signal_wait","label":"Wait briefly for a clear signal","activity":"waiting briefly for a clear signal","destination":"away"},
          {"id":"rail_slow","label":"Slow on the approach to the halt","activity":"slowing on the approach to Bellwether halt","destination":"railway_halt"},
          {"id":"rail_arrive","label":"Draw into Bellwether halt","activity":"drawing into Bellwether railway halt","destination":"railway_halt"},
          {"id":"rail_stop","label":"Make the scheduled halt","activity":"standing briefly at Bellwether halt","destination":"railway_halt"},
          {"id":"rail_board","label":"Wait while passengers board","activity":"waiting while passengers board at the halt","destination":"railway_halt"},
          {"id":"rail_depart","label":"Depart Bellwether halt","activity":"departing Bellwether railway halt","destination":"away"},
          {"id":"rail_pass","label":"Pass Bellwether without stopping","activity":"passing Bellwether on the railway","destination":"away"},
          {"id":"rail_clear","label":"Clear the village and continue onward","activity":"continuing onward beyond Bellwether","destination":"away"},
          {"id":"rail_schedule","label":"Keep to the working timetable","activity":"running steadily to the timetable","destination":loc if loc in ("away","railway_halt") else "away"},
          {"id":"rail_minor_delay","label":"Lose a minute to an ordinary signal delay","activity":"delayed briefly by railway signalling","destination":"away"},
          {"id":"rail_resume","label":"Resume after a brief signal check","activity":"resuming the run toward Bellwether","destination":"away"},
          {"id":"rail_platform_wait","label":"Remain at the platform a little longer","activity":"waiting an extra moment at Bellwether halt","destination":"railway_halt"},
          {"id":"rail_whistle_depart","label":"Sound the whistle and depart","activity":"departing the halt after a short whistle","destination":"away"},
          {"id":"rail_distant","label":"Continue along the distant line","activity":"running along the line beyond the village","destination":"away"},
          {"id":"rail_return_window","label":"Move into the return-service window","activity":"preparing for the later return service","destination":"away"},
        ]
    if vid=="delivery_van":
        return [
          {"id":"van_approach","label":"Approach Bellwether from the outer road","activity":"approaching Bellwether along the outer road","destination":"village_road"},
          {"id":"van_road","label":"Continue the delivery round along Village Road","activity":"making deliveries along Village Road","destination":"village_road"},
          {"id":"van_unload","label":"Unload a small delivery","activity":"unloading a small village delivery","destination":"village_road"},
          {"id":"van_shop","label":"Deliver a parcel to the village shop","activity":"making a delivery at the village shop","destination":"village_shop"},
          {"id":"van_green","label":"Make a delivery near the green","activity":"making a delivery near the village green","destination":"village_green"},
          {"id":"van_wait","label":"Wait briefly for the road to clear","activity":"waiting briefly for the road ahead to clear","destination":"village_road"},
          {"id":"van_slow","label":"Slow for pedestrians","activity":"moving slowly through pedestrian traffic","destination":"village_road"},
          {"id":"van_pull_in","label":"Pull in safely while checking the delivery list","activity":"checking the delivery list while safely pulled in","destination":"village_road"},
          {"id":"van_repack","label":"Rearrange parcels before the next stop","activity":"rearranging parcels for the next delivery","destination":"village_road"},
          {"id":"van_depart","label":"Finish the village deliveries and head outward","activity":"leaving Bellwether after the delivery round","destination":"away"},
          {"id":"van_return","label":"Return from an outer-road delivery","activity":"returning toward Bellwether from an outer delivery","destination":"village_road"},
          {"id":"van_delay","label":"Lose a few minutes to ordinary village traffic","activity":"delayed briefly by ordinary village traffic","destination":"village_road"},
          {"id":"van_resume","label":"Resume the delivery round","activity":"resuming the morning delivery round","destination":"village_road"},
          {"id":"van_green_leave","label":"Leave the green after completing a delivery","activity":"leaving the green after a delivery","destination":"village_road"},
          {"id":"van_break","label":"Pause briefly between deliveries","activity":"taking a brief pause between deliveries","destination":"village_road"},
          {"id":"van_outward","label":"Continue to the next village delivery","activity":"en route to the next village delivery","destination":"away"},
        ]
    # Route 7 bus
    return [
      {"id":"bus_approach","label":"Approach Bellwether from the outer road","activity":"approaching Bellwether along the outer road","destination":"village_road"},
      {"id":"bus_road","label":"Pass steadily through Village Road","activity":"passing steadily through Bellwether","destination":"village_road"},
      {"id":"bus_slow","label":"Slow for pedestrians on Village Road","activity":"moving slowly through pedestrian traffic","destination":"village_road"},
      {"id":"bus_stop","label":"Pull in at the village stop","activity":"pulling in at the village bus stop","destination":"village_road"},
      {"id":"bus_board","label":"Stop to let passengers board","activity":"letting passengers board and alight","destination":"village_road"},
      {"id":"bus_wait","label":"Wait briefly to keep the timetable","activity":"waiting briefly to keep to the timetable","destination":"village_road"},
      {"id":"bus_depart","label":"Depart the village stop","activity":"departing the village stop","destination":"village_road"},
      {"id":"bus_green_edge","label":"Pass the road beside the green","activity":"passing the road beside the village green","destination":"village_green"},
      {"id":"bus_yield","label":"Yield to activity near the green","activity":"yielding to activity near the village green","destination":"village_green"},
      {"id":"bus_delay","label":"Lose a few minutes to ordinary road traffic","activity":"delayed briefly by ordinary village traffic","destination":"village_road"},
      {"id":"bus_resume","label":"Resume the route after a short pause","activity":"resuming the route through Bellwether","destination":"village_road"},
      {"id":"bus_outward","label":"Continue toward the next village","activity":"en route to the next village","destination":"away"},
      {"id":"bus_turn","label":"Complete the village leg and turn outward","activity":"finishing the village leg and heading outward","destination":"away"},
      {"id":"bus_return","label":"Approach on the return service","activity":"approaching Bellwether on the return service","destination":"village_road"},
      {"id":"bus_steady","label":"Keep to a steady timetable pace","activity":"keeping to a steady timetable pace","destination":loc if loc in ("away","village_road","village_green") else "village_road"},
      {"id":"bus_next","label":"Clear Bellwether and continue onward","activity":"continuing onward beyond Bellwether","destination":"away"},
    ]

def traffic_round(s):
    ids=list(s["traffic"]); vid=ids[s["village_brain"]["pulse_count"]%len(ids)]; v=s["traffic"][vid]
    history=s.get("traffic_action_history",{}).get(vid,[])
    plausible=_traffic_transition_candidates(vid, v, traffic_candidates(vid,v,s))
    candidates=_shortlist_candidates(
        plausible, history, v["activity"], v["location"]
    )
    ctx={"vehicle_id":vid,"name":v["name"],"current_location":v["location"],"current_activity":v["activity"],"time_minute":s["minute"],
         "weather":s["weather"],"recent_route_states":history[-4:],
         "recent_world_events":s.get("world_events",[])[-2:],"road_state":s.get("location_state",{}).get("village_road",{}),
         "catchup_changes":s.get("ai_catchup_context",{}).get("meaningful_changes",[])[-3:]}
    choice=_bounded_choice("traffic",f"Choose the next plausible route state for {v['name']}. Keep route continuity but avoid repetitive loops; choose grounded variation when several states are plausible.",ctx,candidates)
    if not choice:return None
    return {"vehicle":vid,"choice":choice["id"],"label":choice["label"]},{"changes":[{"vehicle":vid,"choice":choice["id"],"label":choice["label"],"activity":choice["activity"],"destination":choice["destination"]}]}

def conversation_round(s):
    by_loc={}
    for i,n in s["npcs"].items():by_loc.setdefault(n["location"],[]).append(i)
    pairs=[v[:2] for v in by_loc.values() if len(v)>=2]
    if not pairs:return None
    a,b=pairs[0]; na=s["npcs"][a]; nb=s["npcs"][b]
    ctx={"participants":[{"id":a,"name":na["name"],"activity":na["activity"],"memories":s.get("social_memory",{}).get(a,[])[-3:]},
                         {"id":b,"name":nb["name"],"activity":nb["activity"],"memories":s.get("social_memory",{}).get(b,[])[-3:]}],
         "location":na["location"],"time_minute":s["minute"],"weather":s["weather"],"village_mood":s["village_brain"]["mood"],
         "supernatural_pressure":s["village_brain"]["supernatural_pressure"],"recent_village_events":s.get("world_events",[])[-4:],
         "catchup_changes":s.get("ai_catchup_context",{}).get("meaningful_changes",[])[-4:],
         "character_context":{a:{"identity":NPC_MODEL.dialogue_identity(a),"expression":DIALOGUE_EXPRESSION_MODEL.context(s,a)},b:{"identity":NPC_MODEL.dialogue_identity(b),"expression":DIALOGUE_EXPRESSION_MODEL.context(s,b)}}}
    instruction=(f"Write exactly 4 dialogue lines between {na['name']} and {nb['name']}. Alternate speakers. "
                 "Format every line exactly as Name: dialogue. Keep the exchange ordinary, concise, and free of exposition dumps. Make each speaker recognizably distinct from CHARACTER_CONTEXT without caricature, repeated catchphrases, or forced biography.")
    dialogue=provider.ask_text("conversation",instruction,ctx,max_tokens=120)
    if not dialogue:
        # Fast authored fallback keeps the living-village tick moving if local generation fails.
        dialogue=(f"{na['name']}: Morning. You're out early.\n{nb['name']}: So are you. I thought I'd take the air while it's quiet.\n"
                  f"{na['name']}: It won't stay quiet for long.\n{nb['name']}: No. It never seems to, once everyone gets moving.")
    lines=[x.strip() for x in dialogue.splitlines() if x.strip()][:4]; summary=" / ".join(lines)[:500]
    return {"generated_dialogue":dialogue},{"interactions":[{"participants":[a,b],"topic":"an ordinary village conversation","summary":summary,"dialogue_lines":lines}]}

ROUNDS={"weather":weather_round,"npc":npc_round,"traffic":traffic_round,"conversation":conversation_round}
def run_specific_round(s,domains):
    proposals={}
    for domain in domains:
        result=ROUNDS[domain](s)
        if result is None:continue
        raw,repaired=result; repaired["_ai_trace"]={"director":domain,"raw":raw,"repaired":{k:v for k,v in repaired.items()}}
        proposals[domain]=repaired
    return proposals
