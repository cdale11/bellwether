"""Single daemon-worker asynchronous LLM runtime for low-memory CPU systems.

The worker is deliberately daemonized so diagnostics and clean process shutdown do not
wait for an in-flight local model request. Only immutable inputs enter jobs; game state
is mutated only when Game harvests and validates completed results.
"""
from queue import Queue, Empty
from threading import RLock, Thread
import time

class AsyncAIRuntime:
    def __init__(self):
        self._lock=RLock(); self._queue=Queue(); self._jobs={}; self._seq=0
        self._worker=Thread(target=self._run,name="bellwether-ai-bg",daemon=True)
        self._worker.start()
    def _run(self):
        while True:
            key, fn = self._queue.get()
            with self._lock:
                row=self._jobs.get(key)
                if row: row["started_at"]=time.time(); row["state"]="running"
            try: result=fn(); error=None
            except Exception as exc: result=None; error=f"{type(exc).__name__}: {str(exc)[:160]}"
            with self._lock:
                row=self._jobs.get(key)
                if row:
                    row["result"]=result; row["error"]=error; row["finished_at"]=time.time(); row["state"]="done"
            self._queue.task_done()
    def submit(self,key,kind,revision,signature,fn):
        with self._lock:
            if key in self._jobs:return False
            self._seq+=1
            self._jobs[key]={"id":self._seq,"kind":kind,"revision":revision,"signature":signature,"submitted_at":time.time(),"state":"queued"}
            self._queue.put((key,fn)); return True
    def harvest(self):
        out=[]
        with self._lock:
            for key,row in list(self._jobs.items()):
                if row.get("state")!="done": continue
                item=dict(row); item["key"]=key; out.append(item); self._jobs.pop(key,None)
        return out
    def status(self):
        with self._lock:
            return {"worker_threads":1,"queued_or_running":sum(1 for v in self._jobs.values() if v.get("state")!="done"),"completed_waiting":sum(1 for v in self._jobs.values() if v.get("state")=="done"),"jobs":[{"key":k,"kind":v["kind"],"revision":v["revision"],"state":v.get("state"),"age_s":round(time.time()-v["submitted_at"],2)} for k,v in self._jobs.items()]}
ASYNC_AI_RUNTIME=AsyncAIRuntime()
