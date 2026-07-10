# Part 35 and v0.1.0 Release Candidate Certification

This build combines Part 35 persistence/failure-recovery certification with the first v0.1.0 release candidate.

## Player-facing privacy
The Relationships panel now shows only NPCs the player has actually met or spoken with. Internal simulation state may still track all NPCs so the village can live independently of the player.

## Conclusive diagnostic
Run from the extracted Bellwether folder:

```bash
python3 tools/release_candidate_diagnostic.py
```

For engineering-only tests without local Qwen:

```bash
python3 tools/release_candidate_diagnostic.py --skip-qwen
```

The full run covers:
1. Python compilation and executable permission integrity.
2. Multi-profile structural simulation stress testing.
3. Player-perspective profile runs and pacing variance.
4. Atomic save/load round-trip, relationship/social-memory/conversation-session/evidence persistence, and old-save migration.
5. Conversation continuity, quote cleanup, social parser behavior, malformed-metadata isolation, neutral fallback, and selective memory.
6. Director scheduler unlock state, exact time advancement, seasonal temperature movement/bounds, and invalid NPC/traffic transition rejection.
7. Real local-Qwen health plus the four-turn Mrs Ellis continuity scenario, including per-turn latency, social deltas, exact recent exchange, new long-term memory, attempts, queue wait, inference time, prompt-eval tokens, and generation tokens.
8. A final verdict plus `rc_diagnostic_report.json`.

When reporting a problem, paste the complete terminal output and attach `rc_diagnostic_report.json`.

## Release-candidate acceptance
A release candidate is engineering-clean when all non-Qwen checks pass. Real-Qwen prose remains qualitative and should additionally be inspected for:
- continuity with the immediately previous turn;
- no false claims of long absence;
- grounded advice based on current context;
- no conversational restart after acknowledgements;
- sensible bounded relationship effects;
- no permanent memory spam from trivial acknowledgements;
- acceptable latency and rare retries on the target i3-4160 machine.

The diagnostic is intentionally verbose so a single pasted run can expose transport failures, parser behavior, pacing outcomes, persistence problems, scheduler lock state, and target-machine inference performance.
