"""v2.11.0 systemic horror integration and narrative consequences.

Turns already-authoritative horror, town strategy, story posture, recurrence and player
attachments into bounded, auditable consequences. It cannot create clues, facts, chapters,
endings, relationship canon, deaths, or irreversible asset destruction.
"""
from copy import deepcopy

DOMAIN_TARGETS={
    'property_pressure':'home','enterprise_pressure':'enterprise','mobility_pressure':'mobility',
    'social_pressure':'relationships','routine_pressure':'routine','mystery_pressure':'investigation'
}

class SystemicHorrorIntegrationModel:
    SCHEMA_VERSION=1
    def runtime_defaults(self):
        return {'schema_version':1,'last_day':0,'severity':0,'target':'none','phase':'dormant',
                'consequence_history':[],'recovery_windows':{},'attachment_snapshot':{},
                'narrative_context':{},'recurrence_sensitivity':0,'absorbed_count':0}
    def migrate(self,state):
        rt=state.setdefault('systemic_horror_integration',self.runtime_defaults())
        for k,v in self.runtime_defaults().items(): rt.setdefault(k,deepcopy(v))
        rt['schema_version']=self.SCHEMA_VERSION
        return rt
    def attachments(self,state):
        prop=state.get('property',{}); businesses=state.get('player_businesses',{}).get('enterprises',{})
        transport=state.get('transport',{}).get('owned',{}); rel=state.get('relationship_life',{}).get('routes',{})
        partnered=sum(1 for x in rel.values() if isinstance(x,dict) and x.get('stage') in ('partnership','cohabiting','family_intent'))
        return {'home':len(prop.get('owned',{}))+len(prop.get('leases',{}))+len(prop.get('cottage_expansions',[])),
                'enterprise':len(businesses),'mobility':len(transport),'relationships':partnered,
                'routine':len(state.get('player_life',{}).get('activity_history',[])),
                'investigation':len(state.get('investigation',{}).get('evidence',[]))+len(state.get('mystery_investigation',{}).get('evidence_log',[]))}
    def _severity(self,state):
        experienced=len(state.get('systemic_horror',{}).get('experienced',[]))
        pressure=int(state.get('village_brain',{}).get('supernatural_pressure',0))
        story=int(state.get('story_consciousness_integration',{}).get('story_progress',0))
        recurrence=int(state.get('recurrence',{}).get('run_index',1) or 1)-1
        return max(0,min(5,(experienced//2)+(pressure//25)+(story//3)+(1 if recurrence>0 else 0)))
    def daily_tick(self,state):
        rt=self.migrate(state); day=int(state.get('day',1))
        if day<2 or int(rt.get('last_day',0))>=day:return None
        rt['last_day']=day; severity=self._severity(state); rt['severity']=severity
        strategy=state.get('town_mind',{}).get('strategy',{}).get('active_strategy')
        target=DOMAIN_TARGETS.get(strategy,'routine'); rt['target']=target
        rt['attachment_snapshot']=self.attachments(state)
        posture=state.get('story_consciousness_integration',{}).get('posture','observe')
        chapter=state.get('authored_story',{}).get('chapter','arrival')
        rt['narrative_context']={'chapter':chapter,'posture':posture}
        recurrence=max(0,int(state.get('recurrence',{}).get('run_index',1) or 1)-1); rt['recurrence_sensitivity']=min(3,recurrence)
        if severity<=0: rt['phase']='dormant'; return None
        rt['phase']='encroaching' if severity<=2 else ('personalized' if severity<=4 else 'acute')
        # Respect active resistance protection: consequences remain visible but may be absorbed.
        protected=state.get('resistance',{}).get('protected_domains',{})
        if strategy and int(protected.get(strategy,0) or 0)>=day:
            rt['absorbed_count']+=1; row={'day':day,'target':target,'severity':severity,'effect':'pressure_absorbed','chapter':chapter,'posture':posture}
            rt['consequence_history'].append(row); rt['consequence_history']=rt['consequence_history'][-80:]; return row
        effect='unease_echo'
        if target=='home' and rt['attachment_snapshot']['home']>0:
            c=state.get('player_status',{}).get('cottage',{}); c['condition']=max(0,float(c.get('condition',100))-min(1.5,.25*severity)); effect='home_wear_echo'
        elif target=='enterprise' and rt['attachment_snapshot']['enterprise']>0:
            ents=state.get('player_businesses',{}).get('enterprises',{}); bid=sorted(ents)[0]; ents[bid]['health']=max(0,int(ents[bid].get('health',70))-1); effect='enterprise_friction_echo'
        elif target=='mobility' and rt['attachment_snapshot']['mobility']>0:
            tr=state.get('transport',{}); active=tr.get('active'); vehicle=tr.get('owned',{}).get(active)
            if vehicle: vehicle['condition']=max(0,float(vehicle.get('condition',100))-.5); effect='mobility_wear_echo'
        elif target=='relationships' and rt['attachment_snapshot']['relationships']>0:
            state.setdefault('psychological_state',{})['unease']=min(100,int(state.get('psychological_state',{}).get('unease',0))+1); effect='social_doubt_echo'
        elif target=='investigation':
            state.setdefault('psychological_state',{})['familiarity_disruptions']=int(state.get('psychological_state',{}).get('familiarity_disruptions',0))+1; effect='evidence_context_dislocation'
        else:
            state.setdefault('psychological_state',{})['unease']=min(100,int(state.get('psychological_state',{}).get('unease',0))+1)
        rt['recovery_windows'][target]=day+2
        row={'day':day,'target':target,'severity':severity,'phase':rt['phase'],'effect':effect,'chapter':chapter,'posture':posture,'recurrence':recurrence}
        rt['consequence_history'].append(row); rt['consequence_history']=rt['consequence_history'][-80:]
        return row
    def public(self,state):
        rt=self.migrate(state)
        return {'phase':rt['phase'],'severity':rt['severity'],'target':rt['target'],'recent_consequences':deepcopy(rt['consequence_history'][-8:]),
                'recovery_windows':deepcopy(rt['recovery_windows']),'authority':'bounded consequences only; authored truth and relationship canon remain authoritative'}

SYSTEMIC_HORROR_INTEGRATION_MODEL=SystemicHorrorIntegrationModel()
