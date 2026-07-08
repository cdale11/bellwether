"""v0.8.3 bounded horror aftermath and recovery.

Consequences are derived from authoritative experienced anomalies and legal witnesses.
Recovery comes from ordinary player actions and time; this model never invents truth.
"""
from copy import deepcopy

class HorrorAftermathModel:
    SCHEMA_VERSION=1
    RECOVERY_ACTIONS={
        'tea':('domestic',4),'tidy':('domestic',3),'read':('quiet',2),'garden':('practical',3),
        'bench':('social_world',2),'walk_green':('movement',2),'river_walk':('nature',3),
        'woods_walk':('nature',2),'sketch':('creative',2),'birdwatch':('nature',2),'fish':('quiet',2),
    }
    def runtime_defaults(self):
        return {'schema_version':self.SCHEMA_VERSION,'player':{'strain':0,'recovery':0,'coping_log':[],'last_anomaly_id':None},
                'npc_aftermath':{},'place_avoidance':{},'aftermath_log':[]}
    def migrate(self,state):
        root=state.setdefault('horror_aftermath',self.runtime_defaults())
        for k,v in self.runtime_defaults().items(): root.setdefault(k,deepcopy(v))
        for k,v in self.runtime_defaults()['player'].items(): root['player'].setdefault(k,deepcopy(v))
        root['schema_version']=self.SCHEMA_VERSION
        return root
    def register_anomaly(self,state,anomaly,npc_ids,memory_model,cognition_model):
        root=self.migrate(state); loc=anomaly['location']; aid=anomaly['id']; day=state.get('day',1)
        witnesses=[nid for nid in npc_ids if state.get('npcs',{}).get(nid,{}).get('location')==loc]
        eid=memory_model.record(state,'world',anomaly['summary'],actors=['player'],location=loc,witnesses=witnesses,
                                importance=4,tags=['anomaly','horror',anomaly['domain']],metadata={'anomaly_id':aid,'domain':anomaly['domain']})
        for nid in witnesses:
            slot=root['npc_aftermath'].setdefault(nid,{'witnessed':[],'strain':0,'avoid_locations':{},'last_reaction_day':0})
            if aid not in slot['witnessed']: slot['witnessed'].append(aid)
            slot['strain']=min(100,int(slot.get('strain',0))+12)
            slot['avoid_locations'][loc]=max(int(slot['avoid_locations'].get(loc,0)),day+2)
            slot['last_reaction_day']=day
            cognition_model.ingest_event(state,nid,eid)
            cognition_model.add_concern(state,nid,f'Something at {loc.replace("_"," ")} did not behave as expected.',.62,eid)
        p=root['player']; p['strain']=min(100,int(p.get('strain',0))+15); p['last_anomaly_id']=aid
        root['aftermath_log'].append({'day':day,'anomaly_id':aid,'location':loc,'witnesses':witnesses,'event_id':eid})
        root['aftermath_log']=root['aftermath_log'][-40:]
        return {'event_id':eid,'witnesses':witnesses}
    def note_recovery_activity(self,state,activity_id):
        root=self.migrate(state); key=activity_id.replace('garden_','garden').replace('hobby:','')
        if key not in self.RECOVERY_ACTIONS:return False
        kind,amount=self.RECOVERY_ACTIONS[key]; p=root['player']
        if int(p.get('strain',0))<=0:return False
        p['strain']=max(0,int(p['strain'])-amount); p['recovery']=min(100,int(p.get('recovery',0))+amount)
        p['coping_log'].append({'day':state.get('day',1),'activity':activity_id,'kind':kind,'amount':amount})
        p['coping_log']=p['coping_log'][-40:]
        psych=state.setdefault('psychological_state',{})
        psych['unease']=max(0,int(psych.get('unease',0))-max(1,amount//2))
        return True
    def daily_recovery(self,state):
        root=self.migrate(state); day=int(state.get('day',1))
        for slot in root['npc_aftermath'].values():
            slot['strain']=max(0,int(slot.get('strain',0))-3)
            slot['avoid_locations']={loc:until for loc,until in slot.get('avoid_locations',{}).items() if int(until)>=day}
    def developer_context(self,state):
        root=self.migrate(state)
        return {'player':deepcopy(root['player']),'npc_aftermath':deepcopy(root['npc_aftermath']),
                'place_avoidance':deepcopy(root['place_avoidance']),'recent_aftermath':deepcopy(root['aftermath_log'][-8:])}

HORROR_AFTERMATH_MODEL=HorrorAftermathModel()
