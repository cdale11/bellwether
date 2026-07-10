"""v2.7.0 player resistance, recovery and counterplay against bounded town pressure."""
from copy import deepcopy

class ResistanceModel:
    SCHEMA_VERSION=1
    def runtime_defaults(self):
        return {"schema_version":1,"readiness":0,"resilience":0,"active_stance":"balanced","last_action_day":0,"counterplay_log":[],"recovery_log":[],"protected_domains":{},"pressure_absorbed":0}
    def migrate(self,state):
        rt=state.setdefault("resistance",self.runtime_defaults())
        for k,v in self.runtime_defaults().items(): rt.setdefault(k,deepcopy(v))
        rt["schema_version"]=1; return rt
    def public(self,state): return deepcopy(self.migrate(state))
    def actions(self,state):
        rt=self.migrate(state); day=int(state.get("day",1)); out=[]
        if day>=2:
            out += [("resist:prepare_home","Secure the cottage and review practical weak points"),("resist:diversify","Diversify supplies and routines"),("resist:document","Document contradictions and compare records"),("resist:seek_support","Ask trusted people to help you stay grounded")]
        if int(rt.get("readiness",0))>=12: out.append(("resist:counter","Act against the town's current pressure strategy"))
        if int(state.get("horror_aftermath",{}).get("player",{}).get("strain",0))>0: out.append(("resist:recover","Take a deliberate recovery day"))
        return out
    def perform(self,state,action):
        rt=self.migrate(state); day=int(state.get("day",1)); tm=state.get("town_mind",{}).get("strategy",{}); strategy=tm.get("active_strategy")
        if action=="resist:prepare_home":
            rt["readiness"]=min(100,rt["readiness"]+8); rt["protected_domains"]["property_pressure"]=day+3; msg="You check locks, roof, stores and repair supplies, making the house harder to pressure through neglect."; minutes=75
        elif action=="resist:diversify":
            rt["readiness"]=min(100,rt["readiness"]+7); rt["protected_domains"]["routine_pressure"]=day+3; rt["protected_domains"]["enterprise_pressure"]=day+2; msg="You spread risk across supplies, routes and routines instead of depending on one fragile pattern."; minutes=60
        elif action=="resist:document":
            rt["readiness"]=min(100,rt["readiness"]+10); rt["protected_domains"]["mystery_pressure"]=day+4; state.setdefault("psychological_state",{})["unease"]=max(0,int(state.get("psychological_state",{}).get("unease",0))-2); msg="You write down dates, prices, weather and contradictions before memory can soften them."; minutes=50
        elif action=="resist:seek_support":
            rt["readiness"]=min(100,rt["readiness"]+8); rt["protected_domains"]["social_pressure"]=day+3; msg="You make deliberate contact with people you trust and compare what each of you remembers."; minutes=65
        elif action=="resist:recover":
            aft=state.setdefault("horror_aftermath",{}).setdefault("player",{}); before=int(aft.get("strain",0)); aft["strain"]=max(0,before-12); aft["recovery"]=min(100,int(aft.get("recovery",0))+8); rt["resilience"]=min(100,rt["resilience"]+5); rt["recovery_log"].append({"day":day,"strain_before":before,"strain_after":aft["strain"]}); msg="You deliberately step away from pressure and rebuild a workable rhythm."; minutes=180
        elif action=="resist:counter":
            if rt["readiness"]<12: return False,"You are not prepared enough to act deliberately against the pressure.",0
            rt["readiness"]-=12; rt["resilience"]=min(100,rt["resilience"]+4); rt["protected_domains"][strategy or "routine_pressure"]=day+4; tm["resistance_score"]=int(tm.get("resistance_score",0))+10; msg="You act on the pattern you have observed, reducing the leverage of the town's current strategy without pretending the deeper problem is solved."; minutes=90
        else: return False,"Unknown resistance action.",0
        rt["last_action_day"]=day; rt["counterplay_log"].append({"day":day,"action":action,"strategy":strategy,"readiness":rt["readiness"],"resilience":rt["resilience"]}); rt["counterplay_log"]=rt["counterplay_log"][-80:]
        return True,msg,minutes
    def pressure_modifier(self,state,strategy):
        rt=self.migrate(state); day=int(state.get("day",1)); until=int(rt.get("protected_domains",{}).get(strategy,0) or 0)
        if until>=day:
            rt["pressure_absorbed"]+=1; rt["resilience"]=min(100,rt["resilience"]+1); return 0.35
        return max(.55,1.0-int(rt.get("resilience",0))/250.0)
    def daily_tick(self,state):
        rt=self.migrate(state); day=int(state.get("day",1)); rt["protected_domains"]={k:v for k,v in rt.get("protected_domains",{}).items() if int(v)>=day}
        if int(rt.get("last_action_day",0))<day-2: rt["readiness"]=max(0,int(rt.get("readiness",0))-1)

RESISTANCE_MODEL=ResistanceModel()
