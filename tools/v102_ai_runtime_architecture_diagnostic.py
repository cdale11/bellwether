#!/usr/bin/env python3
"""Focused v1.0.2 AI runtime architecture and observability diagnostic."""
import json, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from backend.ai.async_runtime import AsyncAIRuntime

checks=[]
def check(name, ok, detail=""):
    checks.append({"name":name,"passed":bool(ok),"detail":detail})

rt=AsyncAIRuntime()
check("priority runtime policy exposed", rt.status().get("policy") in {"single_worker_priority_queue","single_worker_priority_queue_lossless_running_results"})
check("domain queue observability exposed", "queued_by_domain" in rt.status())
check("event counters exposed", "event_counts" in rt.status())
check("timing summaries exposed", "timing_by_kind" in rt.status())

# Coalescing must prevent duplicate expensive work for the same logical key.
rt.submit("same","director_batch",1,("npc",),lambda: (time.sleep(.05),"first")[1],domain="npc",priority=20)
second=rt.submit("same","director_batch",1,("npc",),lambda:"duplicate",domain="npc",priority=20)
check("duplicate job coalescing retained", second is False)

time.sleep(.12)
rows=rt.harvest()
check("completed job harvestable", len(rows)==1 and rows[0].get("result")=="first")
status=rt.status()
check("runtime records duration telemetry", status.get("timing_by_kind",{}).get("director_batch",{}).get("samples",0)>=1)
check("runtime records lifecycle counts", status.get("event_counts",{}).get("job_finished",0)>=1)

source=(ROOT/"backend/core/game.py").read_text(encoding="utf-8")
check("game queues domain-aware director work", 'domain="+".join(domains)' in source)
check("strategic work has lower urgency", 'domain="strategy", priority=50' in source)
provider_source=(ROOT/"backend/ai/provider.py").read_text(encoding="utf-8")
app_source=(ROOT/"backend/app.py").read_text(encoding="utf-8")
frontend_source=(ROOT/"frontend/static/js/game.js").read_text(encoding="utf-8")
check("strategic overview projection is compact", 'director in {"town_mind", "procedural_arc"}' in provider_source and 'recent_world_history' in provider_source)
check("portable save export route exists", '/api/save-file' in app_source)
check("portable save import route exists", '/api/load-file' in app_source)
check("portable save controls exposed", 'exportSaveFile' in frontend_source and 'importSaveFile' in frontend_source)

passed=all(x["passed"] for x in checks)
print(json.dumps({"version":(ROOT/"VERSION").read_text().strip(),"passed":passed,"checks":checks},indent=2))
raise SystemExit(0 if passed else 1)
