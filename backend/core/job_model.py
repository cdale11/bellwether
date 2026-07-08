"""Bellwether employment and work-shift model.

v0.4.1 adds progression, reliability, bounded wage growth, workplace pressure effects,
and voluntary resignation while preserving the existing scheduled-shift contract.
"""
JOBS={
 "bakery_helper":{"name":"Bakery Morning Helper","location":"bakery","start":420,"end":720,"shift_minutes":120,"wage":7,"days":[1,2,3,4,5,6],"task":"helping with trays, wrapping loaves and cleaning the morning counter"},
 "shop_assistant":{"name":"Village Shop Assistant","location":"village_shop","start":540,"end":1020,"shift_minutes":120,"wage":6,"days":[1,2,3,4,5,6],"task":"unpacking deliveries, facing shelves and helping with ordinary errands"},
 "cottage_repairs":{"name":"Local Repair Odd Jobs","location":"ashcroft_cottage","start":480,"end":1080,"shift_minutes":90,"wage":5,"days":[1,2,3,4,5,6,7],"task":"sorting small repairs and maintenance work around the cottage"},
 "green_grounds":{"name":"Village Green Grounds Work","location":"village_green","start":480,"end":960,"shift_minutes":120,"wage":6,"days":[1,3,5],"task":"clearing paths, tending borders and dealing with the small maintenance jobs that gather around the green"},
 "churchyard_care":{"name":"Churchyard Care Work","location":"churchyard","start":540,"end":900,"shift_minutes":90,"wage":5,"days":[2,4,6],"task":"clearing windfall, trimming path edges and tending the quieter corners of the churchyard"},
 "riverside_maintenance":{"name":"Riverside Path Maintenance","location":"riverside_path","start":480,"end":960,"shift_minutes":120,"wage":7,"days":[2,5],"task":"checking the path, clearing drainage channels and repairing small stretches damaged by weather"},
}
class JobModel:
 def runtime_defaults(self):
  return {"schema_version":2,"employment":{},"work_reputation":0,"fatigue":0,"shift_history":[],"applications":[],"total_shifts":0,"career_history":[]}
 def migrate(self,state):
  rt=state.setdefault("jobs",self.runtime_defaults()); rt.setdefault("schema_version",2); rt["schema_version"]=2
  for k,v in self.runtime_defaults().items(): rt.setdefault(k,v.copy() if isinstance(v,dict) else list(v) if isinstance(v,list) else v)
  for jid,emp in rt.get("employment",{}).items():
   emp.setdefault("active",True); emp.setdefault("accepted_day",state.get("day",1)); emp.setdefault("last_shift_day",None); emp.setdefault("shifts",0); emp.setdefault("earned",0); emp.setdefault("reliability",50); emp.setdefault("level",1)
  return rt
 def current_wage(self,state,jid):
  rt=self.migrate(state); emp=rt["employment"].get(jid,{})
  # Modest progression: +£1 after 5 shifts, another after 12; capped.
  shifts=int(emp.get("shifts",0)); bonus=2 if shifts>=12 else (1 if shifts>=5 else 0)
  return JOBS[jid]["wage"]+bonus
 def available_actions(self,state):
  from backend.core.event_model import EVENT_MODEL
  rt=self.migrate(state); out=[]; loc=state.get("location"); minute=int(state.get("minute",0)); dow=((int(state.get("day",1))-1)%7)+1
  for jid,j in JOBS.items():
   emp=rt["employment"].get(jid)
   if not emp:
    if loc==j["location"]: out.append((f"job:apply:{jid}",f"Ask About Work: {j['name']}"))
   elif emp.get("active"):
    if EVENT_MODEL.job_available(state,jid) and loc==j["location"] and dow in j["days"] and j["start"]<=minute<j["end"] and emp.get("last_shift_day")!=state.get("day"):
     wage=self.current_wage(state,jid); out.append((f"job:work:{jid}",f"Work Shift: {j['name']} ({j['shift_minutes']//60}h, £{wage})"))
    if loc==j["location"]: out.append((f"job:leave:{jid}",f"Leave Job: {j['name']}"))
  return out
 def apply(self,state,jid):
  if jid not in JOBS:return False,"That work does not exist."
  rt=self.migrate(state); j=JOBS[jid]
  if state.get("location")!=j["location"]:return False,"You need to ask about that work in person."
  existing=rt["employment"].get(jid)
  if existing and existing.get("active"):return False,"You already work there."
  if existing and not existing.get("active") and state.get("day",1)-existing.get("left_day",0)<3:return False,"It is too soon to ask for the same job back."
  rt["employment"][jid]={"active":True,"accepted_day":state.get("day",1),"last_shift_day":None,"shifts":existing.get("shifts",0) if existing else 0,"earned":existing.get("earned",0) if existing else 0,"reliability":50,"level":1}
  rt["applications"].append({"job_id":jid,"day":state.get("day",1),"accepted":True}); rt["career_history"].append({"job_id":jid,"day":state.get("day",1),"event":"started"})
  return True,f"You arrange regular work as {j['name'].lower()}. The hours are modest, but the pay will help."
 def leave(self,state,jid):
  rt=self.migrate(state); emp=rt["employment"].get(jid)
  if jid not in JOBS or not emp or not emp.get("active"):return False,"You are not employed there."
  if state.get("location")!=JOBS[jid]["location"]:return False,"You need to speak to the workplace in person."
  emp["active"]=False; emp["left_day"]=state.get("day",1); rt["career_history"].append({"job_id":jid,"day":state.get("day",1),"event":"left"})
  return True,f"You let them know you will not be taking further shifts as {JOBS[jid]['name'].lower()}."
 def work(self,state,jid):
  from backend.core.event_model import EVENT_MODEL
  if jid not in JOBS:return False,"That shift is unavailable.",0,0
  if not EVENT_MODEL.job_available(state,jid):return False,"The shift is suspended while a village event affects the workplace.",0,0
  rt=self.migrate(state); emp=rt["employment"].get(jid); j=JOBS[jid]; minute=int(state.get("minute",0)); dow=((int(state.get("day",1))-1)%7)+1
  if not emp or not emp.get("active"):return False,"You are not employed there.",0,0
  if state.get("location")!=j["location"] or dow not in j["days"] or not (j["start"]<=minute<j["end"]):return False,"This is not a valid time or place for the shift.",0,0
  if emp.get("last_shift_day")==state.get("day"):return False,"You have already worked this shift today.",0,0
  wage=self.current_wage(state,jid); emp["last_shift_day"]=state.get("day"); emp["shifts"]+=1; emp["earned"]+=wage; emp["reliability"]=min(100,emp.get("reliability",50)+3); emp["level"]=3 if emp["shifts"]>=12 else (2 if emp["shifts"]>=5 else 1)
  rt["total_shifts"]+=1; rt["work_reputation"]=min(100,rt["work_reputation"]+2); rt["fatigue"]=min(100,rt["fatigue"]+12)
  rt["shift_history"].append({"job_id":jid,"day":state.get("day"),"start_minute":minute,"minutes":j["shift_minutes"],"wage":wage});rt["shift_history"]=rt["shift_history"][-80:]
  return True,f"You spend the shift {j['task']}. At the end of it, you are paid £{wage}.",j["shift_minutes"],wage
 def daily_recovery(self,state):
  rt=self.migrate(state); rt["fatigue"]=max(0,rt.get("fatigue",0)-18)
JOB_MODEL=JobModel()
