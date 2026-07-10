"""v0.5.0 durable event and NPC-memory substrate.

Authoritative events are structured and persistent. NPC memory stores references and
private impressions separately; prose summaries never become objective world truth.
"""
from copy import deepcopy

class MemoryModel:
    SCHEMA_VERSION=1
    EVENT_TYPES={"conversation","encounter","relationship","work","hobby","story","world","observation","commitment"}
    def runtime_defaults(self,npc_ids):
        return {
            "schema_version":self.SCHEMA_VERSION,
            "next_event_id":1,
            "events":[],
            "npc_memory":{nid:{"event_refs":[],"impressions":[],"unresolved":[]} for nid in npc_ids},
            "relationship_memory":{},
            "summary_periods":[],
        }
    def migrate(self,state,npc_ids):
        defaults=self.runtime_defaults(npc_ids)
        mem=state.setdefault("memory_system",deepcopy(defaults))
        for key,val in defaults.items(): mem.setdefault(key,deepcopy(val))
        for nid in npc_ids:
            slot=mem["npc_memory"].setdefault(nid,{"event_refs":[],"impressions":[],"unresolved":[]})
            slot.setdefault("event_refs",[]); slot.setdefault("impressions",[]); slot.setdefault("unresolved",[])
        return mem
    def record(self,state,event_type,summary,actors=None,location=None,witnesses=None,importance=1,tags=None,metadata=None):
        if event_type not in self.EVENT_TYPES: event_type="world"
        mem=self.migrate(state,list(state.get("npcs",{})))
        eid=f"evt_{int(mem['next_event_id']):06d}"; mem['next_event_id']+=1
        event={"id":eid,"type":event_type,"day":int(state.get("day",1)),"minute":int(state.get("minute",0)),
               "summary":str(summary)[:320],"actors":list(dict.fromkeys(actors or [])),"location":location,
               "witnesses":list(dict.fromkeys(witnesses or [])),"importance":max(0,min(5,int(importance))),
               "tags":list(dict.fromkeys(tags or [])),"metadata":deepcopy(metadata or {})}
        mem['events'].append(event); mem['events']=mem['events'][-500:]
        known=set(event['actors'])|set(event['witnesses'])
        for nid in known:
            if nid not in mem['npc_memory']: continue
            refs=mem['npc_memory'][nid]['event_refs']; refs.append(eid); mem['npc_memory'][nid]['event_refs']=refs[-120:]
        return eid
    def context(self,state,npc_id,limit=8):
        mem=self.migrate(state,list(state.get("npcs",{}))); slot=mem['npc_memory'].get(npc_id,{})
        refs=set(slot.get('event_refs',[])); rows=[e for e in mem['events'] if e['id'] in refs]
        rows.sort(key=lambda e:(e.get('importance',0),e.get('day',0),e.get('minute',0)),reverse=True)
        return {"events":deepcopy(rows[:limit]),"impressions":deepcopy(slot.get('impressions',[])[-6:]),"unresolved":deepcopy(slot.get('unresolved',[])[-4:])}
    def remember_impression(self,state,npc_id,text,source_event=None,confidence=.5):
        mem=self.migrate(state,list(state.get('npcs',{}))); slot=mem['npc_memory'].get(npc_id)
        if slot is None:return False
        row={"text":str(text)[:240],"source_event":source_event,"confidence":max(0,min(1,float(confidence))),"day":state.get('day',1)}
        slot['impressions'].append(row); slot['impressions']=slot['impressions'][-30:]; return True
MEMORY_MODEL=MemoryModel()
