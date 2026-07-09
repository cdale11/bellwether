"""Single-worker, priority-aware asynchronous LLM runtime.

The worker remains deliberately single-threaded for low-memory machines, while
queued jobs are ordered by domain priority and coalesced by key. Runtime status
is designed for the Developer Console and diagnostics rather than raw log spam.
"""
from queue import PriorityQueue
from threading import RLock, Thread
from collections import Counter, deque
import time


class AsyncAIRuntime:
    MAX_EVENTS = 200
    DEFAULT_PRIORITIES = {
        "director_batch": 20,
        "procedural_arc": 40,
        "town_mind": 50,
    }

    def __init__(self):
        self._lock = RLock()
        self._queue = PriorityQueue()
        self._jobs = {}
        self._events = deque(maxlen=self.MAX_EVENTS)
        self._seq = 0
        self._metrics = Counter()
        self._duration_by_kind = {}
        self._worker = Thread(target=self._run, name="bellwether-ai-bg", daemon=True)
        self._worker.start()

    def _event(self, event, **data):
        self._events.append({"ts": round(time.time(), 3), "event": event, **data})
        self._metrics[event] += 1

    def _run(self):
        while True:
            priority, sequence, key, fn = self._queue.get()
            with self._lock:
                row = self._jobs.get(key)
                if row:
                    row["started_at"] = time.time()
                    row["state"] = "running"
                    row["queue_wait_s"] = round(row["started_at"] - row["submitted_at"], 3)
                    self._event("job_started", job_id=row["id"], key=key, kind=row["kind"],
                                domain=row["domain"], priority=priority, revision=row["revision"],
                                queue_wait_s=row["queue_wait_s"])
            try:
                result, error = fn(), None
            except Exception as exc:
                result, error = None, f"{type(exc).__name__}: {str(exc)[:240]}"
            with self._lock:
                row = self._jobs.get(key)
                if row:
                    row["result"] = result
                    row["error"] = error
                    row["finished_at"] = time.time()
                    row["state"] = "done"
                    duration = round(row["finished_at"] - row["started_at"], 3)
                    row["duration_s"] = duration
                    bucket = self._duration_by_kind.setdefault(row["kind"], deque(maxlen=24))
                    bucket.append(duration)
                    self._event("job_finished" if error is None else "job_failed",
                                job_id=row["id"], key=key, kind=row["kind"], domain=row["domain"],
                                duration_s=duration, error=error)
            self._queue.task_done()

    def submit(self, key, kind, revision, signature, fn, *, domain=None, priority=None):
        """Submit one coalesced job. Lower priority numbers run first.

        Existing callers remain source-compatible; domain and priority are optional.
        """
        with self._lock:
            if key in self._jobs:
                self._event("job_coalesced", key=key, kind=kind, domain=domain or kind, revision=revision)
                return False
            self._seq += 1
            domain = domain or kind
            priority = int(self.DEFAULT_PRIORITIES.get(kind, 30) if priority is None else priority)
            self._jobs[key] = {
                "id": self._seq, "kind": kind, "domain": domain, "priority": priority,
                "revision": revision, "signature": signature, "submitted_at": time.time(), "state": "queued"
            }
            self._event("job_queued", job_id=self._seq, key=key, kind=kind, domain=domain,
                        priority=priority, revision=revision,
                        signature=list(signature) if isinstance(signature, (tuple, list)) else str(signature))
            self._queue.put((priority, self._seq, key, fn))
            return True

    def harvest(self):
        out = []
        with self._lock:
            for key, row in list(self._jobs.items()):
                if row.get("state") != "done":
                    continue
                item = dict(row)
                item["key"] = key
                out.append(item)
                self._jobs.pop(key, None)
                self._event("job_harvested", job_id=row["id"], key=key, kind=row["kind"],
                            domain=row["domain"], had_error=bool(row.get("error")))
        return out

    def record_application(self, job, disposition):
        with self._lock:
            self._event("job_result_" + disposition, job_id=job.get("id"), key=job.get("key"),
                        kind=job.get("kind"), domain=job.get("domain"), revision=job.get("revision"))

    def status(self):
        with self._lock:
            now = time.time()
            jobs = []
            for key, value in self._jobs.items():
                jobs.append({
                    "id": value["id"], "key": key, "kind": value["kind"], "domain": value["domain"],
                    "priority": value["priority"], "revision": value["revision"],
                    "signature": value.get("signature"), "state": value.get("state"),
                    "age_s": round(now - value["submitted_at"], 2),
                    "queue_wait_s": value.get("queue_wait_s"),
                    "run_s": round(now - value["started_at"], 2)
                    if value.get("started_at") and not value.get("finished_at") else None,
                })
            queued_by_domain = Counter(v["domain"] for v in self._jobs.values() if v.get("state") == "queued")
            timing = {}
            for kind, samples in self._duration_by_kind.items():
                vals = list(samples)
                timing[kind] = {"samples": len(vals), "last_s": vals[-1], "avg_s": round(sum(vals)/len(vals), 3)}
            return {
                "worker_threads": 1,
                "policy": "single_worker_priority_queue",
                "queued": sum(v.get("state") == "queued" for v in self._jobs.values()),
                "running": sum(v.get("state") == "running" for v in self._jobs.values()),
                "queued_or_running": sum(v.get("state") in {"queued", "running"} for v in self._jobs.values()),
                "completed_waiting": sum(v.get("state") == "done" for v in self._jobs.values()),
                "queued_by_domain": dict(queued_by_domain),
                "event_counts": dict(self._metrics),
                "timing_by_kind": timing,
                "jobs": sorted(jobs, key=lambda x: (x["state"] != "running", x["priority"], x["id"])),
                "recent_events": list(self._events)[-80:],
            }


ASYNC_AI_RUNTIME = AsyncAIRuntime()
