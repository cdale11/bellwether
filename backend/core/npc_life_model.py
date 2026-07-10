"""v2.4.0 autonomous NPC lives and bounded village change.
Deterministic, save-persistent life goals and consequential changes. Canon/story
truth remains owned by authored narrative systems; this model cannot mutate it.
"""
from copy import deepcopy

class NPCLifeModel:
    SCHEMA_VERSION=1
    GOAL_KINDS=('security','work','social','home','craft')
    def runtime_defaults(self):
        return {'schema_version':1,'last_day':0,'core_goals':{},'resident_lives':{},'life_events':[],'player_influence':[]}
    def migrate(self,state):
        rt=state.setdefault('npc_autonomous_lives',self.runtime_defaults())
        for k,v in self.runtime_defaults().items(): rt.setdefault(k,deepcopy(v))
        for nid,npc in state.get('npc_lives',{}).items():
            rt['core_goals'].setdefault(nid,{'goal':self.GOAL_KINDS[sum(map(ord,nid))%len(self.GOAL_KINDS)],'progress':0,'pressure':0,'status':'active','history':[]})
        for rid,r in state.get('population',{}).get('residents',{}).items():
            rt['resident_lives'].setdefault(rid,{'occupation':r.get('occupation',''),'household':r.get('household','unknown'),'stability':60,'social_momentum':0,'life_stage_events':[]})
        return rt
    def _event(self,rt,state,kind,actor,text,details=None):
        row={'day':int(state.get('day',1)),'kind':kind,'actor':actor,'text':text,'details':details or {}}
        rt['life_events'].append(row); rt['life_events']=rt['life_events'][-160:]; return row
    def advance_day(self,state):
        rt=self.migrate(state); day=int(state.get('day',1))
        if rt['last_day']==day:return []
        rt['last_day']=day; events=[]
        # Core-cast goals progress from lived needs and social state, without inventing canon.
        web=state.get('npc_social_web',{})
        for nid,g in rt['core_goals'].items():
            needs=state.get('npc_lives',{}).get(nid,{}).get('needs',{})
            dominant=max(needs,key=needs.get) if needs else 'purpose'; pressure=float(needs.get(dominant,0))
            delta=1 + (1 if pressure<55 else 0)
            g['progress']=min(100,int(g.get('progress',0))+delta); g['pressure']=round(pressure,1)
            if day%7==0:
                g['history'].append({'day':day,'progress':g['progress'],'dominant_need':dominant});g['history']=g['history'][-24:]
            if g['progress']>=25 and g.get('status')=='active':
                g['status']='developing'; events.append(self._event(rt,state,'goal_progress',nid,f'{nid} made quiet progress on a personal {g["goal"]} goal.'))
        # Lightweight residents can change employment and social circumstances slowly.
        pop=state.get('population',{}).get('residents',{})
        businesses=state.get('economy',{}).get('market',{}).get('businesses',{})
        stressed=any(float(b.get('pressure',0))>=70 or float(b.get('health',100))<=25 for b in businesses.values())
        for rid,r in pop.items():
            life=rt['resident_lives'].setdefault(rid,{'occupation':r.get('occupation',''),'household':r.get('household','unknown'),'stability':60,'social_momentum':0,'life_stage_events':[]})
            links=len(r.get('social_links',[])); life['social_momentum']=min(100,links*8)
            life['stability']=max(0,min(100,int(life.get('stability',60)) + (1 if links>=2 else -1) + (-2 if stressed else 0)))
            # Sparse deterministic changes: observable, reversible, and never story-canon mutation.
            if day%28==0 and (sum(map(ord,rid))+day)%5==0:
                old=r.get('occupation',''); new='between jobs' if stressed else ('self-employed odd jobs' if old!='self-employed odd jobs' else old)
                if new!=old:
                    r['occupation']=new; life['occupation']=new
                    ev=self._event(rt,state,'employment_change',rid,f'{r.get("name",rid)} changed their working situation.',{'from':old,'to':new});events.append(ev);life['life_stage_events'].append(ev)
            if day%35==0 and links>=3 and (sum(map(ord,rid))+day)%7==0:
                ev=self._event(rt,state,'household_consideration',rid,f'{r.get("name",rid)} is considering a change in household arrangements.')
                events.append(ev);life['life_stage_events'].append(ev)
            life['life_stage_events']=life['life_stage_events'][-20:]
        return events
    def influence(self,state,npc_id,kind,amount=1):
        rt=self.migrate(state); g=rt['core_goals'].get(npc_id)
        if not g:return False
        amount=max(-5,min(5,int(amount)));g['progress']=max(0,min(100,g['progress']+amount))
        rt['player_influence'].append({'day':state.get('day',1),'npc':npc_id,'kind':str(kind)[:40],'amount':amount});rt['player_influence']=rt['player_influence'][-80:]
        return True
    def public(self,state):
        rt=self.migrate(state)
        return {'core_goals':deepcopy(rt['core_goals']),'recent_life_events':deepcopy(rt['life_events'][-20:]),'resident_life_count':len(rt['resident_lives'])}
NPC_LIFE_MODEL=NPCLifeModel()
