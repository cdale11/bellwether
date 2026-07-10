"""v0.7.2 bounded procedural social arcs.

Arcs are persistent causal chains composed from legal authored templates. The LLM may
select a suitable template; it cannot invent actors, facts, stages, or effects.
"""
from copy import deepcopy

ARC_TEMPLATES = [
    {"id":"shop_delivery_strain","label":"Delayed shop delivery","domain":"economy","actors":["asha","mrs_ellis"],"location":"village_shop","stages":[
        {"id":"pressure","after_days":0,"text":"A delayed delivery leaves Asha reorganising the shop's morning priorities.","concerns":{"asha":"The shop delivery delay may inconvenience regular customers."}},
        {"id":"social_ripple","after_days":1,"text":"Regular customers begin adjusting errands around the shop's unsettled stock routine.","concerns":{"mrs_ellis":"The shop's altered routine is becoming noticeable."}},
        {"id":"resolution","after_days":2,"text":"The shop settles into a revised delivery rhythm, though the disruption is remembered."}
    ]},
    {"id":"garden_help_chain","label":"The neglected cottage garden","domain":"social","actors":["mara","ruth"],"location":"ashcroft_cottage","stages":[
        {"id":"notice","after_days":0,"text":"Mara's attention to the neglected cottage garden becomes a small point of local concern.","concerns":{"mara":"The cottage garden needs patient work rather than a hurried fix."}},
        {"id":"shared_interest","after_days":1,"text":"A conversation about old planting habits connects the cottage garden to village memory.","concerns":{"ruth":"Old accounts of the cottage garden may be worth comparing with what grows there now."}},
        {"id":"resolution","after_days":3,"text":"The cottage garden has become a quiet shared reference point between practical work and local memory."}
    ]},
    {"id":"railway_clock_dispute","label":"Conflicting railway timetables","domain":"social","actors":["tom","mrs_ellis"],"location":"railway_halt","stages":[
        {"id":"disagreement","after_days":0,"text":"A minor disagreement about the railway halt timetable begins circulating among regular travellers.","concerns":{"tom":"People are relying on conflicting ideas about the halt timetable."}},
        {"id":"clarification","after_days":1,"text":"Different recollections of the timetable are compared rather than immediately resolved.","concerns":{"mrs_ellis":"Familiar travel routines feel less certain when people remember the timetable differently."}},
        {"id":"resolution","after_days":2,"text":"The timetable disagreement subsides after the practical routine becomes clear again."}
    ]},
    {"id":"bakery_workload","label":"Bakery under pressure","domain":"economy","actors":["jonah","asha"],"location":"bakery","stages":[
        {"id":"pressure","after_days":0,"text":"A busy stretch at the bakery leaves Jonah balancing orders against the ordinary morning rhythm.","concerns":{"jonah":"The bakery workload is becoming difficult to absorb without changing the routine."}},
        {"id":"coordination","after_days":1,"text":"The bakery and shop quietly coordinate around what can be supplied and when.","concerns":{"asha":"Shop expectations need to stay realistic while the bakery is under pressure."}},
        {"id":"resolution","after_days":3,"text":"The bakery workload eases into a more workable pattern after several days of adjustment."}
    ]},
    {"id":"churchyard_record_question","label":"The churchyard record discrepancy","domain":"mystery","actors":["ruth","mrs_ellis"],"location":"churchyard","stages":[
        {"id":"question","after_days":0,"text":"Ruth notices a small inconsistency between a weathered inscription and a remembered local account.","concerns":{"ruth":"A churchyard record and a familiar local account do not quite agree."}},
        {"id":"comparison","after_days":2,"text":"The record question persists as recollections are compared without forcing a conclusion.","concerns":{"mrs_ellis":"People can remember the same old village detail differently."}},
        {"id":"resolution","after_days":4,"text":"The record discrepancy remains documented as an unresolved local-history question rather than becoming a new fact."}
    ]},
]

class ProceduralArcModel:
    SCHEMA_VERSION=1
    MAX_ACTIVE=2
    def runtime_defaults(self):
        return {"schema_version":self.SCHEMA_VERSION,"next_arc_id":1,"active":[],"history":[],"last_proposal_pulse":-999,"proposal_count":0,"accepted_count":0,"rejected_count":0}
    def migrate(self,state):
        root=state.setdefault("procedural_arcs",self.runtime_defaults())
        for k,v in self.runtime_defaults().items(): root.setdefault(k,deepcopy(v))
        return root
    def candidates(self,state):
        root=self.migrate(state); active_templates={a.get("template_id") for a in root["active"]}
        return [{"id":t["id"],"label":t["label"]} for t in ARC_TEMPLATES if t["id"] not in active_templates]
    def compact_context(self,state):
        root=self.migrate(state)
        return {"day":state.get("day",1),"village_mood":state.get("village_brain",{}).get("mood"),"village_focus":state.get("village_brain",{}).get("focus"),"business_pressure":state.get("economy",{}).get("business_pressure",{}),"town_mind_intentions":state.get("town_mind",{}).get("active_intentions",[])[:3],"active_arcs":[{"template_id":a.get("template_id"),"stage":a.get("stage_index")} for a in root["active"]],"recent_world_events":state.get("world_events",[])[-3:]}
    def start(self,state,template_id,source_model="deterministic_fallback"):
        root=self.migrate(state); templates={t["id"]:t for t in ARC_TEMPLATES}
        t=templates.get(template_id)
        if not t or len(root["active"])>=self.MAX_ACTIVE or any(a.get("template_id")==template_id for a in root["active"]):
            root["rejected_count"]+=1; return None
        aid=f"arc_{root['next_arc_id']:04d}"; root["next_arc_id"]+=1
        row={"id":aid,"template_id":template_id,"label":t["label"],"domain":t["domain"],"actors":deepcopy(t["actors"]),"location":t["location"],"started_day":int(state.get("day",1)),"stage_index":-1,"stage_history":[],"status":"active","source_model":source_model}
        root["active"].append(row); root["accepted_count"]+=1
        return row
    def available_player_actions(self,state):
        location=state.get("location"); out=[]
        for arc in self.migrate(state).get("active",[]):
            if arc.get("location")==location and not arc.get("player_involved"):
                
                help_labels={
                    "shop_delivery_strain":"Help Asha reorganise the delayed delivery",
                    "garden_help_chain":"Help Mara with the neglected garden",
                    "railway_clock_dispute":"Help compare the conflicting timetables",
                    "bakery_workload":"Help Jonah with the bakery backlog",
                    "churchyard_record_question":"Help compare the churchyard records",
                }
                out.append((f"arc:help:{arc['id']}", help_labels.get(arc.get("template_id"), f"Offer practical help: {arc['label']}")))
        return out[:2]
    def involve_player(self,state,arc_id,memory_model,cognition_model):
        root=self.migrate(state); arc=next((a for a in root["active"] if a.get("id")==arc_id),None)
        if not arc or arc.get("player_involved") or state.get("location")!=arc.get("location"): return None
        arc["player_involved"]=True; arc["status"]="in_progress"; arc["player_involved_day"]=state.get("day",1)
        text=f"The player offered practical help with {arc['label'].lower()}."
        eid=memory_model.record(state,"commitment",text,actors=arc.get("actors",[]),location=arc.get("location"),witnesses=arc.get("actors",[]),importance=3,tags=["procedural_arc","player_involved"],metadata={"arc_id":arc_id})
        for nid in arc.get("actors",[]): cognition_model.ingest_event(state,nid,eid)
        return eid

    def due_stages(self,state):
        day=int(state.get("day",1)); templates={t["id"]:t for t in ARC_TEMPLATES}; due=[]
        for arc in list(self.migrate(state)["active"]):
            t=templates.get(arc.get("template_id")); nxt=int(arc.get("stage_index",-1))+1
            if t and nxt<len(t["stages"]) and day-int(arc.get("started_day",day))>=int(t["stages"][nxt].get("after_days",0)):
                due.append((arc,t,t["stages"][nxt]))
        return due
    def apply_stage(self,state,arc,template,stage,memory_model,cognition_model):
        root=self.migrate(state)
        if arc not in root["active"]: return False
        idx=int(arc.get("stage_index",-1))+1
        if idx>=len(template["stages"]) or template["stages"][idx]["id"]!=stage["id"]: return False
        eid=memory_model.record(state,"world",stage["text"],actors=template["actors"],location=template["location"],witnesses=template["actors"],importance=2,tags=["procedural_arc",template["id"],stage["id"]],metadata={"arc_id":arc["id"],"stage":stage["id"]})
        for nid,text in stage.get("concerns",{}).items(): cognition_model.add_concern(state,nid,text,.55,eid)
        arc["stage_index"]=idx; arc["stage_history"].append({"stage":stage["id"],"day":state.get("day",1),"event_id":eid})
        if idx==len(template["stages"])-1:
            arc["status"]="resolved"; arc["resolved_day"]=state.get("day",1)
            
            # v1.5.0: resolved player-involved arcs are completed quests with exactly-once rewards.
            if arc.get("player_involved"):
                from backend.core.quest_model import QUEST_MODEL
                QUEST_MODEL.complete_arc(state,arc)
            root["history"].append(deepcopy(arc)); root["history"]=root["history"][-40:]; root["active"].remove(arc)
        return eid

PROCEDURAL_ARC_MODEL=ProceduralArcModel()
