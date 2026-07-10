# RC2.1 Conversation Semantic Grounding

This patch responds directly to the RC2 real-Qwen trace.

## Observed RC2 issues
1. Qwen attributed Mrs Ellis's own statement about watching the village to the player.
2. A practical-advice question was answered by changing the subject to weather.
3. The generated long-term memory incorrectly said the player asked about weather.
4. Mrs Ellis repeated a recent line nearly verbatim.

## RC2.1 changes
- Exact exchanges label speakers as `PLAYER_SAID` and `YOU_SAID`.
- `CURRENT_PLAYER_MESSAGE` appears after context immediately before generation.
- The model is instructed to answer the current message first.
- The two most recent NPC replies are supplied as repetition-avoidance context.
- Long-term memory uses a conservative grounding guard against clear topic substitution.

The patch intentionally does not alter simulation pacing, story gates, Directors, weather,
save structure, horror escalation, branches, or endings.

## Target-machine test

Run:

```bash
python3 tools/release_candidate_diagnostic.py
```

For additional conversation-specific checks:

```bash
python3 tools/real_qwen_narrative_qa.py --npc mrs_ellis --scenario continuity
python3 tools/real_qwen_narrative_qa.py --npc mrs_ellis --scenario first_contact
```
