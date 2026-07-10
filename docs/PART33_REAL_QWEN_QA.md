# Part 33 — Real-Qwen Narrative QA and Conversation Continuity

## Purpose
Part 33 makes player-authored, non-story conversation socially consequential while keeping authored story dialogue canonical. One foreground Qwen inference now produces both the visible NPC reply and hidden bounded social metadata.

The player never sees raw affinity/trust/familiarity deltas. Consequences surface through future relationship context, social memories, impressions, and later dialogue.

## Social interpretation
Each free-text turn is interpreted against:
- NPC-specific social personality
- current affinity, familiarity, trust, and talk history
- recent relevant NPC memories
- current activity, place, time, weather, and village mood
- evolving player-style summary and recent notable player choices
- compact story position and psychological stage

Allowed per-turn changes are strictly bounded:
- affinity: -2 to +2
- trust: -2 to +2
- familiarity: 0 to +2

Malformed metadata never discards a valid NPC reply. The game applies a neutral fallback consequence of +1 familiarity only.

## Real-Qwen QA runner
Run controlled multi-turn continuity scenarios against the actual local Ollama model:

```bash
python3 tools/real_qwen_narrative_qa.py --npc jonah --scenario warm --json-out jonah_warm.json
python3 tools/real_qwen_narrative_qa.py --npc mara --scenario intrusive --json-out mara_intrusive.json
python3 tools/real_qwen_narrative_qa.py --npc mrs_ellis --scenario inconsistent --json-out ellis_inconsistent.json
```

Available scenarios: `warm`, `reserved`, `intrusive`, `inconsistent`.

The runner records every player message, Qwen reply, latency, relationship delta, cumulative relationship state, and stored social memory. This makes continuity drift, personality collapse, excessive positivity, failure to respond to apology, and memory quality directly inspectable.

## Acceptance questions for target-machine QA
1. Does each NPC retain a distinct voice over three turns?
2. Does a warm sequence tend toward small positive effects without rewarding every neutral line?
3. Does intrusive pressure reduce affinity or trust where personality context supports it?
4. Does an apology after rudeness produce a plausible partial recovery rather than instant reset?
5. Do stored memories describe social meaning without inventing events or hidden motives?
6. Does turn 2/3 visibly reflect relevant relationship and memory accumulated in earlier turns?
7. Are response times acceptable on the i3-4160 with normal BOINC suspension behavior?
8. Are retries/timeouts rare enough that free conversation feels dependable?

## Automated regression evidence
Part 33 parser/integration tests verify positive and negative bounded changes, malformed-metadata isolation, meaningful social memory storage, and compact single-inference prompting. Post-change regressions passed 7/7 structural profiles and a balanced player-visible run reached anomaly escalation and a complete ending.

Real-model prose quality must still be assessed on the target machine because this build environment does not provide the user's local Ollama runtime.
