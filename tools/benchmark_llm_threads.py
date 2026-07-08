#!/usr/bin/env python3
"""Benchmark Bellwether's installed Ollama model at several thread counts."""
import json, os, time, urllib.request

base=os.getenv("BELLWETHER_AI_URL","http://127.0.0.1:11434").rstrip("/")
model=os.getenv("BELLWETHER_AI_MODEL","qwen3:1.7b")
available=os.cpu_count() or 1
requested=os.getenv("BELLWETHER_BENCH_THREADS","2,4,6,8")
thread_counts=sorted({max(1,min(available,int(x))) for x in requested.split(",") if x.strip()})
prompt=("You are making ONE bounded state decision for Bellwether. "
        "Choose one plausible option. Reply with exactly ONE letter.\n"
        "CONTEXT: early autumn, 10:20, soft overcast, quiet village morning.\n"
        "A: Continue current routine\nB: Take a short errand\nC: Pause briefly\nANSWER:")

print(f"Model: {model} | logical CPUs: {available} | tests: {thread_counts}")
results=[]
for n in thread_counts:
    payload=json.dumps({
        "model":model,"prompt":prompt,"stream":False,"think":False,"keep_alive":"10m",
        "options":{"temperature":0.0,"num_predict":8,"num_thread":n}
    }).encode()
    req=urllib.request.Request(base+"/api/generate",data=payload,
        headers={"Content-Type":"application/json"},method="POST")
    started=time.perf_counter()
    with urllib.request.urlopen(req,timeout=120) as r:
        data=json.loads(r.read().decode())
    elapsed=time.perf_counter()-started
    prompt_s=data.get("prompt_eval_duration",0)/1e9
    results.append((n,elapsed,prompt_s))
    print(f"{n:>2} threads: total {elapsed:6.2f}s | prompt eval {prompt_s:6.2f}s")
best=min(results,key=lambda x:x[1])
print(f"\nFastest tested setting: {best[0]} threads ({best[1]:.2f}s total)")
print(f"Use: BELLWETHER_AI_THREADS={best[0]} ./run.sh")
