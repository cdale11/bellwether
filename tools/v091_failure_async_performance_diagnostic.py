from backend.core.game import Game
from backend.ai.async_runtime import ASYNC_AI_RUNTIME
from backend.core.failure_recovery_model import FAILURE_RECOVERY_MODEL
import time

def main():
 g=Game(); s=g.state; checks=[]
 def ck(n,x): checks.append((n,bool(x))); print(("PASS" if x else "FAIL"),n)
 ck("failure runtime", "failure_recovery" in s)
 ck("async worker single", ASYNC_AI_RUNTIME.status()["worker_threads"]==1)
 ck("preparation bounded", 0<=FAILURE_RECOVERY_MODEL.preparation_check(s,"quarry_loose_stone")["score"]<=3)
 s["danger"]["status"]="dead"; s["danger"]["death"]={"hazard_id":"night_road_collision"}; s["danger"]["terminal_reason"]="death"; s["branch_state"]["run_complete"]=True
 row=FAILURE_RECOVERY_MODEL.recover_from_terminal_failure(s)
 ck("authored recovery route",row["id"]=="clinic_waking")
 ck("recovery restores play",s["danger"]["status"]=="alive" and not s["branch_state"]["run_complete"])
 ck("recovery consequence persists",bool(s["failure_recovery"]["recovery_history"]))
 ck("developer async status", isinstance(ASYNC_AI_RUNTIME.status()["jobs"],list))
 ASYNC_AI_RUNTIME.submit("diagnostic_job","diagnostic",1,("x",),lambda: "done")
 time.sleep(.05); rows=ASYNC_AI_RUNTIME.harvest(); ck("background result harvest", any(x.get("result")=="done" for x in rows))
 assert all(x for _,x in checks); print(f"v0.9.1 diagnostic: {len(checks)}/{len(checks)} PASS")
if __name__=="__main__":main()
