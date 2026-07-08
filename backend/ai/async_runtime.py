"""Single-worker asynchronous LLM runtime for low-memory CPU systems.

Only immutable prompt inputs cross into the worker. Results are applied by Game on a
later pulse after revision/signature validation; the worker never mutates game state.
"""
from concurrent.futures import ThreadPoolExecutor
from threading import RLock
import time

class AsyncAIRuntime:
    def __init__(self):
        self._executor=ThreadPoolExecutor(max_workers=1,thread_name_prefix="bellwether-ai-bg")
        self._lock=RLock(); self._jobs={}; self._completed={}; self._seq=0
    def submit(self,key,kind,revision,signature,fn):
        with self._lock:
            if key in self._jobs or key in self._completed:return False
            self._seq+=1; jid=self._seq
            future=self._executor.submit(fn)
            self._jobs[key]={"id":jid,"kind":kind,"revision":revision,"signature":signature,"submitted_at":time.time(),"future":future}
            return True
    def harvest(self):
        out=[]
        with self._lock:
            for key,row in list(self._jobs.items()):
                f=row["future"]
                if not f.done():continue
                item={k:v for k,v in row.items() if k!="future"}; item["key"]=key; item["finished_at"]=time.time()
                try:item["result"]=f.result(); item["error"]=None
                except Exception as exc:item["result"]=None; item["error"]=f"{type(exc).__name__}: {str(exc)[:160]}"
                out.append(item); self._jobs.pop(key,None)
        return out
    def status(self):
        with self._lock:
            return {"worker_threads":1,"queued_or_running":len(self._jobs),"jobs":[{"key":k,"kind":v["kind"],"revision":v["revision"],"age_s":round(time.time()-v["submitted_at"],2)} for k,v in self._jobs.items()]}
ASYNC_AI_RUNTIME=AsyncAIRuntime()
