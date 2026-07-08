"""Part 6 employment and work-shift substrate.

Authored job definitions are immutable; applications, shifts, attendance, fatigue,
reputation and earnings live in save state. Work uses real locations, hours and
Part 5 economy transactions.
"""
JOBS={
 "bakery_helper":{"name":"Bakery Morning Helper","location":"bakery","start":420,"end":720,"shift_minutes":120,"wage":7,"days":[1,2,3,4,5,6],"task":"helping with trays, wrapping loaves and cleaning the morning counter"},
 "shop_assistant":{"name":"Village Shop Assistant","location":"village_shop","start":540,"end":1020,"shift_minutes":120,"wage":6,"days":[1,2,3,4,5,6],"task":"unpacking deliveries, facing shelves and helping with ordinary errands"},
 "cottage_repairs":{"name":"Local Repair Odd Jobs","location":"ashcroft_cottage","start":480,"end":1080,"shift_minutes":90,"wage":5,"days":[1,2,3,4,5,6,7],"task":"sorting small repairs and maintenance work around the cottage"},
}
class JobModel:
 def runtime_defaults(self):
  return {"schema_version":1,"employment":{},"work_reputation":0,"fatigue":0,"shift_history":[],"applications":[],"total_shifts":0}
 def available_actions(self,state):
  from backend.core.event_model import EVENT_MODEL
  rt=state.setdefault("jobs",self.runtime_defaults()); out=[]; loc=state.get("location"); minute=int(state.get("minute",0)); dow=((int(state.get("day",1))-1)%7)+1
  for jid,j in JOBS.items():
   emp=rt["employment"].get(jid)
   if not emp:
    if loc==j["location"]: out.append((f"job:apply:{jid}",f"Ask About Work: {j['name']}"))
   elif emp.get("active") and EVENT_MODEL.job_available(state,jid) and loc==j["location"] and dow in j["days"] and j["start"]<=minute<j["end"] and emp.get("last_shift_day")!=state.get("day"):
    out.append((f"job:work:{jid}",f"Work Shift: {j['name']} ({j['shift_minutes']//60}h, £{j['wage']})"))
  return out
 def apply(self,state,jid):
  if jid not in JOBS:return False,"That work does not exist."
  rt=state.setdefault("jobs",self.runtime_defaults()); j=JOBS[jid]
  if state.get("location")!=j["location"]:return False,"You need to ask about that work in person."
  if jid in rt["employment"]:return False,"You have already discussed that work."
  rt["employment"][jid]={"active":True,"accepted_day":state.get("day",1),"last_shift_day":None,"shifts":0,"earned":0}
  rt["applications"].append({"job_id":jid,"day":state.get("day",1),"accepted":True})
  return True,f"You arrange regular work as {j['name'].lower()}. The hours are modest, but the pay will help."
 def work(self,state,jid):
  from backend.core.event_model import EVENT_MODEL
  if not EVENT_MODEL.job_available(state,jid):return False,"The shift is suspended while a village event affects the workplace.",0
  if jid not in JOBS:return False,"That shift is unavailable.",0
  rt=state.setdefault("jobs",self.runtime_defaults()); emp=rt["employment"].get(jid); j=JOBS[jid]; minute=int(state.get("minute",0)); dow=((int(state.get("day",1))-1)%7)+1
  if not emp or not emp.get("active"):return False,"You are not employed there.",0
  if state.get("location")!=j["location"] or dow not in j["days"] or not (j["start"]<=minute<j["end"]):return False,"This is not a valid time or place for the shift.",0
  if emp.get("last_shift_day")==state.get("day"):return False,"You have already worked this shift today.",0
  emp["last_shift_day"]=state.get("day"); emp["shifts"]+=1; emp["earned"]+=j["wage"]; rt["total_shifts"]+=1; rt["work_reputation"]=min(100,rt["work_reputation"]+2); rt["fatigue"]=min(100,rt["fatigue"]+12)
  rt["shift_history"].append({"job_id":jid,"day":state.get("day"),"start_minute":minute,"minutes":j["shift_minutes"],"wage":j["wage"]});rt["shift_history"]=rt["shift_history"][-60:]
  return True,f"You spend the shift {j['task']}. At the end of it, you are paid £{j['wage']}.",j["shift_minutes"]
JOB_MODEL=JobModel()
