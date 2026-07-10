"""v1.2.0 Life Simulation Expansion.

Deterministic authority for cooking progression, pantry preservation, hobby mastery,
community participation, and long-term ordinary-life progression. LLM systems may
interpret these facts but do not invent inventory, skill, money, or progression.
"""
from copy import deepcopy

COMMUNITY_ACTIVITIES = {
    "green_workday": {"label":"Join the Village Green Workday","location":"village_green","days":{6},"start":540,"end":900,"minutes":90,"community":2,"skill":"home_care"},
    "churchyard_volunteer": {"label":"Help with Churchyard Upkeep","location":"churchyard","days":{2,4,6},"start":600,"end":960,"minutes":75,"community":1,"skill":"local_history"},
    "river_litter_walk": {"label":"Join the Riverside Care Walk","location":"riverside_path","days":{7},"start":600,"end":1020,"minutes":70,"community":2,"skill":"foraging"},
}
PRESERVES = {
    "pickled_radish":{"label":"Pickle radishes","crop":"radish","qty":4,"groceries":1,"minutes":40},
    "carrot_pickle":{"label":"Make spiced carrot pickle","crop":"carrot","qty":4,"groceries":1,"minutes":50},
    "bean_preserve":{"label":"Bottle broad beans","crop":"broad_bean","qty":5,"groceries":1,"minutes":55},
    "potato_store":{"label":"Sort potatoes for cool storage","crop":"potato","qty":6,"groceries":0,"minutes":35},
    "kale_pickle":{"label":"Make peppered kale pickle","crop":"kale","qty":4,"groceries":1,"minutes":50},
    "pea_relish":{"label":"Bottle garden pea relish","crop":"pea","qty":5,"groceries":1,"minutes":55},
}
MILESTONES = {
    10:"settling_in", 30:"capable_routine", 60:"rooted_life", 100:"bellwether_hand"
}

class LifeSimulationModel:
    def runtime_defaults(self):
        return {
            "schema_version":1,
            "pantry":{"preserves":{},"meals_shared":0,"preservation_history":[]},
            "community":{"participation":0,"history":[],"last_activity_day":{},"standing":"newcomer"},
            "progression":{"life_xp":0,"level":0,"milestones":[],"days_active":0,"last_day_scored":0,"weekly_summaries":[]},
            "hobby_mastery":{},
        }

    def migrate(self,state):
        rt=state.setdefault("life_simulation",self.runtime_defaults()); d=self.runtime_defaults()
        for k,v in d.items(): rt.setdefault(k,deepcopy(v))
        for k,v in d["pantry"].items(): rt["pantry"].setdefault(k,deepcopy(v))
        for k,v in d["community"].items(): rt["community"].setdefault(k,deepcopy(v))
        for k,v in d["progression"].items(): rt["progression"].setdefault(k,deepcopy(v))
        return rt

    def actions(self,state):
        rt=self.migrate(state); out=[]; loc=state.get("location"); day=((int(state.get("day",1))-1)%7)+1; minute=int(state.get("minute",0))
        if loc=="ashcroft_cottage":
            garden=state.get("player_activities",{}).get("garden",{}); store=garden.get("harvest_store",{}); groceries=state.get("economy",{}).get("household",{}).get("groceries",0)
            for pid,p in PRESERVES.items():
                if store.get(p["crop"],0)>=p["qty"] and groceries>=p["groceries"]: out.append((f"lifesim:preserve:{pid}",p["label"]))
            if sum(rt["pantry"]["preserves"].values())>0: out.append(("lifesim:share_meal","Invite Someone to Share a Simple Meal"))
        for aid,spec in COMMUNITY_ACTIVITIES.items():
            if loc==spec["location"] and day in spec["days"] and spec["start"]<=minute<=spec["end"] and rt["community"]["last_activity_day"].get(aid)!=state.get("day"):
                out.append((f"lifesim:community:{aid}",spec["label"]))
        return out

    def perform(self,state,action):
        rt=self.migrate(state); parts=action.split(":")
        if len(parts)>=3 and parts[1]=="preserve":
            pid=parts[2]; p=PRESERVES.get(pid)
            if not p or state.get("location")!="ashcroft_cottage": return False,"You cannot do that here.",0
            store=state["player_activities"]["garden"]["harvest_store"]; house=state["economy"]["household"]
            if store.get(p["crop"],0)<p["qty"] or house.get("groceries",0)<p["groceries"]: return False,"You no longer have what you need.",0
            store[p["crop"]]-=p["qty"]; house["groceries"]-=p["groceries"]; rt["pantry"]["preserves"][pid]=rt["pantry"]["preserves"].get(pid,0)+2
            rt["pantry"]["preservation_history"].append({"day":state["day"],"item":pid}); self.award(state,5,"preserving harvest")
            return True,f"You {p['label'].lower()}. Part of the garden will keep beyond its season.",p["minutes"]
        if action=="lifesim:share_meal":
            pantry=rt["pantry"]["preserves"]; available=next((k for k,v in pantry.items() if v>0),None)
            if not available:return False,"There is nothing prepared to share.",0
            pantry[available]-=1; rt["pantry"]["meals_shared"]+=1; rt["community"]["participation"]+=1; state.setdefault("branch_state",{} )["community"]=state.get("branch_state",{}).get("community",0)+1; self.award(state,6,"sharing food")
            return True,"You put together a simple meal and share it without ceremony. Ordinary hospitality changes the shape of an evening.",75
        if len(parts)>=3 and parts[1]=="community":
            aid=parts[2]; spec=COMMUNITY_ACTIVITIES.get(aid)
            if not spec:return False,"That activity is unavailable.",0
            legal={x for x,_ in self.actions(state)}
            if action not in legal:return False,"That gathering is not happening now.",0
            c=rt["community"]; c["participation"]+=spec["community"]; c["last_activity_day"][aid]=state["day"]; c["history"].append({"day":state["day"],"activity":aid,"location":state["location"]}); c["history"]=c["history"][-40:]
            state.setdefault("branch_state",{})["community"]=state.get("branch_state",{}).get("community",0)+spec["community"]
            skills=state["player_activities"]["skills"]; skills[spec["skill"]]=min(100,skills.get(spec["skill"],0)+2); self.award(state,8,"community participation"); self.refresh_standing(state)
            return True,"You join in with work that belongs to no single person. By the end, people speak to you as part of the effort rather than as a visitor.",spec["minutes"]
        return False,"Nothing happens.",0

    def award(self,state,amount,reason):
        p=self.migrate(state)["progression"]; p["life_xp"]+=int(amount); p["level"]=p["life_xp"]//20
        for threshold,mid in MILESTONES.items():
            if p["life_xp"]>=threshold and mid not in p["milestones"]: p["milestones"].append(mid)
        return p

    def refresh_hobby_mastery(self,state):
        rt=self.migrate(state); skills=state.get("player_activities",{}).get("skills",{}); sessions=state.get("player_activities",{}).get("hobbies",{}).get("sessions",{})
        for hobby,count in sessions.items():
            skill=skills.get(hobby,0); rank="novice" if skill<10 else "practised" if skill<30 else "skilled" if skill<60 else "expert"
            rt["hobby_mastery"][hobby]={"sessions":count,"skill":skill,"rank":rank}
        return rt["hobby_mastery"]

    def close_day(self,state):
        rt=self.migrate(state); p=rt["progression"]; day=int(state.get("day",1))
        if p["last_day_scored"]==day:return
        daily=state.get("content_progression",{}).get("daily_life",{}).get("today",{}); variety=sum(1 for k in ("home","garden","cooked","social","work") if daily.get(k,0)>0)
        if variety: p["days_active"]+=1; self.award(state,2+variety,"active day")
        p["last_day_scored"]=day; self.refresh_hobby_mastery(state); self.refresh_standing(state)
        if day%7==0:p["weekly_summaries"].append({"day":day,"life_xp":p["life_xp"],"community":rt["community"]["participation"],"active_days":p["days_active"]});p["weekly_summaries"]=p["weekly_summaries"][-12:]

    def refresh_standing(self,state):
        c=self.migrate(state)["community"]; n=c["participation"]; c["standing"]="newcomer" if n<3 else "familiar_face" if n<8 else "contributor" if n<16 else "local_fixture"

    def public(self,state):
        rt=self.migrate(state); self.refresh_hobby_mastery(state); self.refresh_standing(state)
        return deepcopy(rt)

LIFE_SIMULATION_MODEL=LifeSimulationModel()
