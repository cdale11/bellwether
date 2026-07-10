# RC2 Stabilization Patch

RC2 is a narrow stabilization release based directly on the RC1 target-machine diagnostic.

## Changes

### Elapsed-time conversation chronology
Exact recent exchanges now store an absolute game minute. Before each free-text NPC call, Bellwether derives `elapsed_minutes` and a human-readable `when` value for the last three exchanges. Old RC1/Part 34 saves remain compatible; older exchange entries without absolute time are preserved without inventing elapsed time.

### Daypart grounding
Conversation context now contains an authoritative `daypart` derived from game time. The prompt forbids contradictions with that value.

### Narrow temporal contradiction retry
Only obvious explicit contradictions are rejected, such as sunset/nightfall language during morning. Bellwether makes one corrective retry. This is deliberately narrow to avoid rejecting creative but valid dialogue.

### Deterministic social calibration
A small acknowledgement-only message cannot receive more than +1 familiarity even if Qwen emits +2. Affinity and trust remain model-interpreted within the existing bounded ranges.

### QA semantics
`real_qwen_narrative_qa.py` now distinguishes:
- `first_contact`: no fabricated prior relationship context;
- `continuity`: begins with an actual prior exact exchange and tests immediate conversational memory.

## Recommended target-machine check

```bash
python3 tools/release_candidate_diagnostic.py
```

Then, if desired:

```bash
python3 tools/real_qwen_narrative_qa.py --npc mrs_ellis --scenario first_contact
python3 tools/real_qwen_narrative_qa.py --npc mrs_ellis --scenario continuity
```
