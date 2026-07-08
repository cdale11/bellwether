"""v0.9.1 bounded injury, setback, preparation and authored recovery routes."""
from copy import deepcopy
class FailureRecoveryModel:
    SCHEMA_VERSION=1
    ROUTES={
      "night_road_collision":{"id":"clinic_waking","label":"Clinic recovery","location":"clinic","days_lost":2,"money_loss":12,"text":"You wake at the clinic with missing hours and the village already moving beyond the window."},
      "platform_pull":{"id":"halt_rescue","label":"Halt rescue","location":"clinic","days_lost":1,"money_loss":6,"text":"You wake under a clinic blanket. Someone found you near the halt, though accounts differ about who."},
      "cave_disorientation":{"id":"cave_search","label":"Search-party recovery","location":"ashcroft_cottage","days_lost":2,"money_loss":8,"text":"You wake at the cottage after a search party brought you back from the quarry road."},
      "default":{"id":"ordinary_recovery","label":"Ordinary recovery","location":"ashcroft_cottage","days_lost":1,"money_loss":4,"text":"You wake sore and exhausted at the cottage, with practical consequences still to deal with."}}
    PREPARATION={"riverbank_slip":{"items":["walking boots","sturdy boots"],"health":45},"quarry_loose_stone":{"items":["walking boots","sturdy boots"],"health":55},"cave_disorientation":{"items":["torch","flashlight","lantern"],"health":60},"platform_pull":{"items":[],"health":70},"night_road_collision":{"items":[],"health":75}}
    def runtime_defaults(self):return {"schema_version":1,"setbacks":[],"recovery_history":[],"preparation_checks":[],"active_recovery":None}
    def migrate(self,state):
        rt=state.setdefault("failure_recovery",self.runtime_defaults())
        for k,v in self.runtime_defaults().items():rt.setdefault(k,deepcopy(v))
        return rt
    def preparation_check(self,state,hazard_id):
        rt=self.migrate(state); rule=self.PREPARATION.get(hazard_id,{"items":[],"health":50}); inv=[str(x).lower() for x in state.get("inventory",[])]
        health=int(state.get("health",state.get("player",{}).get("health",100)) or 100)
        item_ok=any(any(token in row for token in rule["items"]) for row in inv) if rule["items"] else False
        health_ok=health>=rule["health"]; warned=hazard_id in state.get("danger",{}).get("warnings_seen",[])
        score=int(item_ok)+int(health_ok)+int(warned); result={"hazard_id":hazard_id,"item_ready":item_ok,"health_ready":health_ok,"warning_heeded":warned,"score":score,"day":state.get("day",1)}
        rt["preparation_checks"].append(result); rt["preparation_checks"]=rt["preparation_checks"][-30:]; return result
    def mitigate(self,state,hazard_id,severity):
        check=self.preparation_check(state,hazard_id); reduction=1 if check["score"]>=2 else 0
        return max(1,int(severity)-reduction),check
    def record_setback(self,state,event):
        rt=self.migrate(state); row=deepcopy(event); row["recorded_day"]=state.get("day",1); rt["setbacks"].append(row); rt["setbacks"]=rt["setbacks"][-30:]
    def recover_from_terminal_failure(self,state):
        rt=self.migrate(state); danger=state.get("danger",{}); death=danger.get("death") or {}; hid=death.get("hazard_id","default"); route=deepcopy(self.ROUTES.get(hid,self.ROUTES["default"]))
        state["day"]=int(state.get("day",1))+route["days_lost"]; state["money"]=max(0,int(state.get("money",0))-route["money_loss"]); state["location"]=route["location"]
        danger["status"]="alive"; danger["terminal_reason"]=None; danger["death"]=None; danger["risk"]=max(1,int(danger.get("risk",0))//2)
        state.setdefault("branch_state",{})["run_complete"]=False
        row={**route,"hazard_id":hid,"day":state["day"]}; rt["recovery_history"].append(row); rt["active_recovery"]={"until_day":state["day"]+1,"route_id":route["id"]}; return row
    def developer_context(self,state):return deepcopy(self.migrate(state))
FAILURE_RECOVERY_MODEL=FailureRecoveryModel()
