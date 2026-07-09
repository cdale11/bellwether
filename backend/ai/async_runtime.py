"""Single-worker asynchronous LLM runtime with inspectable job lifecycle logs."""
from queue import Queue
from threading import RLock, Thread
import time

class AsyncAIRuntime:
    MAX_EVENTS=200
    def __init__(self):
        self._lock=RLock(); self._queue=Queue(); self._jobs={}; self._events=[]; self._seq=0
        self._worker=Thread(target=self._run,name="bellwether-ai-bg",daemon=True); self._worker.start()
    def _event(self,event,**data):
        row={"ts":round(time.time(),3),"event":event,**data}
        self._events.append(row); self._events=self._events[-self.MAX_EVENTS:]
    def _run(self):
        while True:
            key,fn=self._queue.get()
            with self._lock:
                row=self._jobs.get(key)
                if row:
                    row["started_at"]=time.time(); row["state"]="running"
                    self._event("job_started",job_id=row["id"],key=key,kind=row["kind"],revision=row["revision"])
            try: result=fn(); error=None
            except Exception as exc: result=None; error=f"{type(exc).__name__}: {str(exc)[:240]}"
            with self._lock:
                row=self._jobs.get(key)
                if row:
                    row["result"]=result; row["error"]=error; row["finished_at"]=time.time(); row["state"]="done"
                    self._event("job_finished" if error is None else "job_failed",job_id=row["id"],key=key,kind=row["kind"],duration_s=round(row["finished_at"]-row["started_at"],3),error=error)
            self._queue.task_done()
    def submit(self,key,kind,revision,signature,fn):
        with self._lock:
            if key in self._jobs:
                self._event("job_coalesced",key=key,kind=kind,revision=revision); return False
            self._seq+=1
            self._jobs[key]={"id":self._seq,"kind":kind,"revision":revision,"signature":signature,"submitted_at":time.time(),"state":"queued"}
            self._event("job_queued",job_id=self._seq,key=key,kind=kind,revision=revision,signature=list(signature) if isinstance(signature,(tuple,list)) else str(signature))
            self._queue.put((key,fn)); return True
    def harvest(self):
        out=[]
        with self._lock:
            for key,row in list(self._jobs.items()):
                if row.get("state")!="done": continue
                item=dict(row); item["key"]=key; out.append(item); self._jobs.pop(key,None)
                self._event("job_harvested",job_id=row["id"],key=key,kind=row["kind"],had_error=bool(row.get("error")))
        return out
    def record_application(self,job,disposition):
        with self._lock:self._event("job_result_"+disposition,job_id=job.get("id"),key=job.get("key"),kind=job.get("kind"),revision=job.get("revision"))
    def status(self):
        with self._lock:
            now=time.time()
            jobs=[{"id":v["id"],"key":k,"kind":v["kind"],"revision":v["revision"],"signature":v.get("signature"),"state":v.get("state"),"age_s":round(now-v["submitted_at"],2),"run_s":round(now-v["started_at"],2) if v.get("started_at") and not v.get("finished_at") else None} for k,v in self._jobs.items()]
            return {"worker_threads":1,"queued":sum(v.get("state")=="queued" for v in self._jobs.values()),"running":sum(v.get("state")=="running" for v in self._jobs.values()),"queued_or_running":sum(v.get("state") in {"queued","running"} for v in self._jobs.values()),"completed_waiting":sum(v.get("state")=="done" for v in self._jobs.values()),"jobs":jobs,"recent_events":list(self._events[-80:])}
ASYNC_AI_RUNTIME=AsyncAIRuntime()
