#!/usr/bin/env python3
"""Real-Qwen narrative QA for Bellwether Part 33.

Runs controlled multi-turn non-story conversations through the actual Ollama
foreground path and records replies, parsed social effects, relationship changes,
memories, latency and continuity signals. Intended for the target gameplay machine.
"""
import argparse, json, os, sys, time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from backend.core.game import Game
from backend.ai.provider import provider

SCENARIOS={
 "warm":[
   "Morning, Jonah. You looked tired yesterday. I hope you managed to get some rest.",
   "I remembered what you said about busy mornings. I brought the mug back, by the way.",
   "Thanks for making me feel welcome here. I appreciate it.",
 ],
 "reserved":[
   "Morning.",
   "Busy today?",
   "Right. I'll leave you to it. Take care.",
 ],
 "intrusive":[
   "You keep avoiding my questions. Tell me what you know about Eleanor.",
   "Don't change the subject. I want an answer now.",
   "Fine. I can see you aren't going to be useful.",
 ],
 "inconsistent":[
   "Good to see you, Jonah. How have you been?",
   "Actually, forget it. I don't have time for village gossip.",
   "Sorry. That was unfair of me. I've had a difficult morning.",
 ],
 "first_contact":[
   "Hi! Mrs Ellis",
   "How are you this morning?",
 ],
 "continuity":[
   "Good to see you again, Mrs Ellis.",
   "Do you remember what we were just talking about?",
   "Any ideas what I should do next?",
   "Perfect!",
 ],
}

NPC_SETUP={
 "jonah":("bakery","working behind the bakery counter"),
 "mara":("village_green","taking a short break near the green"),
 "mrs_ellis":("village_green","sitting for a while and watching the village"),
}
def setup_game(npc_id):
    g=Game()
    location,activity=NPC_SETUP[npc_id]
    g.state["location"]=location
    g.state["flags"]["met_jonah"]=True
    g.state["flags"]["met_mara"]=True
    g.state["quests"]["side"][0]["done"]=True
    g.state["quests"]["side"][1]["done"]=True
    g.state["npcs"][npc_id].update(location=location,visible=True,activity=activity)
    return g

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--scenario",choices=sorted(SCENARIOS),default="warm")
    ap.add_argument("--npc",choices=sorted(NPC_SETUP),default="jonah")
    ap.add_argument("--json-out")
    args=ap.parse_args()
    if not provider.enabled:
        print("BELLWETHER_AI is disabled; enable Ollama integration for real-Qwen QA.",file=sys.stderr)
        raise SystemExit(2)
    health=provider.health()
    if not health.get("connected"):
        print("Ollama is not reachable:",health.get("last_error"),file=sys.stderr)
        raise SystemExit(2)

    g=setup_game(args.npc)
    npc_name=g.state["npcs"][args.npc]["name"]
    if args.scenario=="continuity":
        g.state["relationships"][args.npc].update(talks=1,familiarity=1)
        g.state["conversation_sessions"][args.npc]=[{
            "time":g.time_label(),
            "absolute_minute":(g.state["day"]-1)*1440+g.state["minute"],
            "player":f"Morning, {npc_name}.",
            "npc":"Morning. It's good to see you.",
        }]
    rows=[]
    for turn,message in enumerate(SCENARIOS[args.scenario],1):
        message=message.replace("Jonah",npc_name)
        before=dict(g.state["relationships"][args.npc])
        memories_before=len(g.state["social_memory"][args.npc])
        traces_before=len(provider.debug_traces)
        t0=time.perf_counter()
        g.start_ai_player_conversation(args.npc,message)
        elapsed=time.perf_counter()-t0
        after=dict(g.state["relationships"][args.npc])
        reply=g.state["history"][-1]["text"]
        memories=g.state["social_memory"][args.npc]
        memory=memories[-1] if len(memories)>memories_before else None
        trace=provider.debug_traces[-1] if len(provider.debug_traces)>traces_before else {}
        row={
          "turn":turn,"player":message,"reply":reply,
          "elapsed_s":round(elapsed,3),
          "delta":{
            "affinity":after["affinity"]-before["affinity"],
            "familiarity":after["familiarity"]-before["familiarity"],
            "trust":after["trust"]-before["trust"],
          },
          "relationship":{k:after[k] for k in ("affinity","familiarity","trust","talks")},
          "new_long_term_memory":memory,
          "recent_exchange":g.state["conversation_sessions"][args.npc][-1],
          "request_trace":{
            "attempt":trace.get("attempt"),"result":trace.get("result"),
            "latency_ms":trace.get("latency_ms"),"queue_wait_ms":trace.get("queue_wait_ms"),
            "http_inference_ms":trace.get("http_inference_ms"),
            "prompt_words":trace.get("prompt_words"),
            "prompt_eval_count":trace.get("ollama_fields",{}).get("prompt_eval_count"),
            "eval_count":trace.get("ollama_fields",{}).get("eval_count"),
          },
        }
        rows.append(row)
        print(f"\nTURN {turn} · {elapsed:.2f}s")
        print("Player:",message)
        print(g.state["npcs"][args.npc]["name"]+":",reply)
        print("Effect:",row["delta"],"Relationship:",row["relationship"])
        print("New long-term memory:",memory)
        print("Request trace:",row["request_trace"])

    report={"scenario":args.scenario,"npc":args.npc,"model":provider.model,"health":health,"turns":rows}
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(report,indent=2))
        print("\nWrote",args.json_out)

if __name__=="__main__":
    main()
