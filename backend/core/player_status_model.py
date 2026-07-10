"""v1.6.0 player survival/status and cottage condition continuity."""
from copy import deepcopy

class PlayerStatusModel:
    def defaults(self):
        return {"schema_version":1,"health":100.0,"hunger":18.0,"energy":88.0,"warmth":82.0,"last_causes":[],"cottage":{"condition":78.0,"weatherproofing":55.0,"repair_stage":"sound","active_repair":None,"repair_history":[]}}
    def migrate(self,state):
        rt=state.setdefault("player_status",self.defaults()); d=self.defaults()
        for k,v in d.items(): rt.setdefault(k,deepcopy(v))
        for k,v in d["cottage"].items(): rt.setdefault("cottage",{}).setdefault(k,deepcopy(v))
        state["health"]=round(float(rt.get("health",100)),1)
        return rt
    def advance(self,state,minutes):
        rt=self.migrate(state); m=float(minutes); weather=state.get("weather",{}); temp=float(weather.get("temperature_c",12)); exposed=not bool(state.get("world_model",{}).get("interior",False))
        rt["hunger"]=min(100,rt["hunger"]+m*.012); rt["energy"]=max(0,rt["energy"]-m*.009)
        if temp<5 and state.get("location") not in {"ashcroft_cottage","bakery","village_shop"}: rt["warmth"]=max(0,rt["warmth"]-m*(.018+(5-temp)*.002))
        else: rt["warmth"]=min(100,rt["warmth"]+m*.012)
        strain=max(0,rt["hunger"]-82)*.002*m + max(0,18-rt["warmth"])*.003*m + max(0,8-rt["energy"])*.002*m
        if strain: rt["health"]=max(0,rt["health"]-strain)
        cottage=rt["cottage"]; season=state.get("season",{}).get("id",""); ws=weather.get("state","")
        seasonal=1.35 if "winter" in season else 1.15 if "autumn" in season else .8
        weather_factor={"storm":3.0,"heavy_rain":2.0,"light_rain":1.25,"snow":1.5}.get(ws,.55)
        cottage["condition"]=max(0,cottage["condition"]-m/1440*.11*seasonal*weather_factor*(1.25-cottage["weatherproofing"]/200))
        cottage["repair_stage"]="critical" if cottage["condition"]<25 else "poor" if cottage["condition"]<50 else "worn" if cottage["condition"]<72 else "sound"
        state["health"]=round(rt["health"],1)
    def eat(self,state,amount=22):
        rt=self.migrate(state);rt["hunger"]=max(0,rt["hunger"]-amount);rt["energy"]=min(100,rt["energy"]+5)
    def sleep(self,state):
        rt=self.migrate(state);rt["energy"]=min(100,rt["energy"]+72);rt["warmth"]=min(100,rt["warmth"]+35);rt["health"]=min(100,rt["health"]+4);rt["hunger"]=min(100,rt["hunger"]+8);state["health"]=round(rt["health"],1)
    def actions(self,state):
        rt=self.migrate(state); c=rt["cottage"]; out=[]
        if state.get("location")!="ashcroft_cottage": return out
        household=state.get("economy",{}).get("household",{})
        if int(household.get("bread_loaf",0) or 0)>0: out.append(("status:eat:bread","Eat Fresh Bread"))
        if c["condition"]<72 and not c.get("active_repair"): out.append(("status:repair:inspect","Inspect Cottage Damage"))
        elif c.get("active_repair")=="inspected": out.append(("status:repair:prepare","Prepare Repair Materials"))
        elif c.get("active_repair")=="prepared": out.append(("status:repair:work","Carry Out Cottage Repairs"))
        return out
    def perform(self,state,action):
        rt=self.migrate(state); c=rt["cottage"]
        if action=="status:eat:bread":
            household=state.setdefault("economy",{}).setdefault("household",{})
            if int(household.get("bread_loaf",0) or 0)<1:return False,"There is no fresh bread left to eat.",0
            household["bread_loaf"]-=1; self.eat(state,26)
            return True,"You cut a generous piece of fresh bread and eat it properly. The meal takes the edge off your hunger.",15
        if action.startswith("status:repair:") and state.get("location")!="ashcroft_cottage":
            return False,"Cottage repairs can only be carried out at Ashcroft Cottage.",0
        if action=="status:repair:inspect":
            if c["condition"]>=72 or c.get("active_repair"):
                return False,"There is no new cottage damage ready for inspection.",0
            c["active_repair"]="inspected"; return True,"You inspect damp joints, slipped pointing and weathered frames, making a practical repair list.",35
        if action=="status:repair:prepare":
            if c.get("active_repair")!="inspected":return False,"Inspect the cottage damage before preparing materials.",0
            supplies=state.get("economy",{}).get("household",{}).get("repair_supplies",0)
            if supplies<1:return False,"You need repair supplies before the work can continue.",0
            state["economy"]["household"]["repair_supplies"]-=1;c["active_repair"]="prepared";return True,"You sort tools and materials and prepare the damaged sections for repair.",45
        if action=="status:repair:work":
            if c.get("active_repair")!="prepared":return False,"Prepare the repair materials before beginning the work.",0
            before=c["condition"];c["condition"]=min(100,before+24);c["weatherproofing"]=min(100,c["weatherproofing"]+8);c["active_repair"]=None;c["repair_history"].append({"day":state.get("day"),"before":round(before,1),"after":round(c["condition"],1)});return True,"You complete a real section of repair work. The cottage is more weather-tight than it was.",150
        return False,"Nothing happens.",0
PLAYER_STATUS_MODEL=PlayerStatusModel()
