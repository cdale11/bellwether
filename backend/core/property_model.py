"""v2.1.0 property, land and cottage progression.

Authoritative ownership, leases and cottage expansion live here. Existing garden,
economy and cottage-condition models remain authoritative for crops, money and wear.
"""
from copy import deepcopy

PARCELS = {
    "meadow_lease": {"name":"Lower Meadow allotment", "location":"field_lane", "mode":"lease", "upfront":12, "daily_rent":1, "garden_plots":2},
    "orchard_strip": {"name":"Old Orchard strip", "location":"orchard_lane", "mode":"buy", "upfront":55, "daily_rent":0, "garden_plots":2},
    "workshop_lease": {"name":"Workshop Yard bay", "location":"workshop_yard", "mode":"lease", "upfront":18, "daily_rent":2, "garden_plots":0},
}

EXPANSIONS = {
    "pantry_room": {"name":"restore the pantry room", "cost":24, "supplies":2, "minutes":240, "requires":[], "condition":60, "benefit":"pantry_capacity"},
    "work_room": {"name":"fit out a practical work room", "cost":38, "supplies":3, "minutes":360, "requires":["pantry_room"], "condition":68, "benefit":"work_space"},
    "upper_room": {"name":"make the upper room habitable", "cost":65, "supplies":4, "minutes":540, "requires":["work_room"], "condition":75, "benefit":"household_capacity"},
}

class PropertyModel:
    schema_version=1
    def runtime_defaults(self):
        return {"schema_version":1,"owned":{"ashcroft_cottage":{"acquired_day":1,"kind":"home"}},"leases":{},"expansions":[],"history":[],"rent_paid":0,"rent_arrears":0,"last_rent_day":0}
    def migrate(self,state):
        rt=state.setdefault("property",self.runtime_defaults()); d=self.runtime_defaults()
        for k,v in d.items(): rt.setdefault(k,deepcopy(v))
        rt["schema_version"]=self.schema_version
        return rt
    def _record(self,state,kind,asset,amount=0):
        rt=self.migrate(state); rt["history"].append({"day":state.get("day",1),"minute":state.get("minute",0),"kind":kind,"asset":asset,"amount":amount}); rt["history"]=rt["history"][-80:]
    def actions(self,state):
        rt=self.migrate(state); loc=state.get("location"); out=[]
        for pid,p in PARCELS.items():
            if p["location"]!=loc or pid in rt["owned"] or pid in rt["leases"]: continue
            verb="Lease" if p["mode"]=="lease" else "Buy"
            suffix=f" + ฿{p['daily_rent']}/day" if p["daily_rent"] else ""
            out.append((f"property:acquire:{pid}",f"{verb} {p['name']} (฿{p['upfront']}{suffix})"))
        if loc=="ashcroft_cottage":
            status=state.get("player_status",{}).get("cottage",{}); done=set(rt["expansions"])
            for eid,e in EXPANSIONS.items():
                if eid in done or not all(x in done for x in e["requires"]): continue
                if float(status.get("condition",0))>=e["condition"]:
                    out.append((f"property:expand:{eid}",f"Cottage expansion: {e['name'].title()} (฿{e['cost']}, {e['supplies']} supplies)"))
        return out
    def perform(self,state,action):
        parts=action.split(":")
        if len(parts)!=3 or parts[0]!="property": return False,"Nothing happens.",0
        rt=self.migrate(state); kind,asset=parts[1],parts[2]
        if kind=="acquire" and asset in PARCELS:
            p=PARCELS[asset]
            if state.get("location")!=p["location"]: return False,"You need to be at the property to arrange that.",0
            if asset in rt["owned"] or asset in rt["leases"]: return False,"You already control that property.",0
            if state.get("money",0)<p["upfront"]: return False,"You cannot afford the agreement yet.",0
            state["money"]-=p["upfront"]
            target=rt["leases"] if p["mode"]=="lease" else rt["owned"]
            target[asset]={"acquired_day":state.get("day",1),"kind":"land" if p["garden_plots"] else "workspace","daily_rent":p["daily_rent"]}
            if p["garden_plots"]:
                garden=state["player_activities"]["garden"]; garden["plots"].extend([None]*p["garden_plots"])
            state.setdefault("economy",{}).setdefault("ledger",[]).append({"day":state.get("day",1),"minute":state.get("minute",0),"kind":"property_acquisition","amount":-p["upfront"],"reason":asset,"business":None})
            self._record(state,"lease_started" if p["mode"]=="lease" else "purchase",asset,-p["upfront"])
            return True,f"The agreement is made. You now control {p['name']}.",45
        if kind=="expand" and asset in EXPANSIONS:
            if state.get("location")!="ashcroft_cottage": return False,"Cottage expansion work must begin at home.",0
            e=EXPANSIONS[asset]; done=set(rt["expansions"])
            if asset in done: return False,"That cottage expansion is already complete.",0
            if not all(x in done for x in e["requires"]): return False,"Earlier cottage work must be completed first.",0
            condition=float(state.get("player_status",{}).get("cottage",{}).get("condition",0))
            if condition<e["condition"]: return False,"The cottage must be repaired to a sounder condition before expansion.",0
            house=state.get("economy",{}).get("household",{})
            if state.get("money",0)<e["cost"] or int(house.get("repair_supplies",0))<e["supplies"]: return False,"You need more money and repair supplies for that work.",0
            state["money"]-=e["cost"]; house["repair_supplies"]-=e["supplies"]; rt["expansions"].append(asset)
            state["player_life"]["cottage_care"]=min(100,state["player_life"].get("cottage_care",0)+8)
            state.setdefault("economy",{}).setdefault("ledger",[]).append({"day":state.get("day",1),"minute":state.get("minute",0),"kind":"cottage_expansion","amount":-e["cost"],"reason":asset,"business":None})
            self._record(state,"cottage_expansion",asset,-e["cost"])
            return True,f"You complete the work to {e['name']}. The cottage has permanently changed shape around your life.",e["minutes"]
        return False,"Nothing happens.",0
    def daily_tick(self,state):
        rt=self.migrate(state); day=int(state.get("day",1))
        if rt["last_rent_day"]>=day: return None
        rt["last_rent_day"]=day; due=sum(int(x.get("daily_rent",0)) for x in rt["leases"].values())
        if due<=0:return {"due":0,"paid":0,"arrears":rt["rent_arrears"]}
        paid=min(int(state.get("money",0)),due); state["money"]-=paid; short=due-paid; rt["rent_paid"]+=paid; rt["rent_arrears"]+=short
        state.setdefault("economy",{}).setdefault("ledger",[]).append({"day":day,"minute":state.get("minute",0),"kind":"property_rent","amount":-paid,"reason":"daily leases","business":None})
        self._record(state,"rent", "leases", -paid)
        return {"due":due,"paid":paid,"arrears":rt["rent_arrears"]}
    def public(self,state):
        rt=self.migrate(state)
        return {"owned":deepcopy(rt["owned"]),"leases":deepcopy(rt["leases"]),"expansions":list(rt["expansions"]),"rent_arrears":rt["rent_arrears"],"garden_plot_capacity":len(state.get("player_activities",{}).get("garden",{}).get("plots",[]))}

PROPERTY_MODEL=PropertyModel()
