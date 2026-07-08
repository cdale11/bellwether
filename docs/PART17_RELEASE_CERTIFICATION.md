# Part 17 — Full-System Balancing and v0.2.0 Release Certification

Part 17 closes the v0.2.0 roadmap. It is a hardening and certification pass, not a new feature layer.

## Whole-codebase review and corrections

The final review compiled all project Python, parsed every authored JSON catalogue, checked frontend JavaScript syntax, exercised all focused Part diagnostics, ran structural simulation and player-perspective profiles, fuzzed visible actions, checked save-state JSON round trips, and re-tested the death-to-recurrence boundary.

Three concrete defects were corrected:

1. Injury treatment and terminal new-run actions omitted the required `kind` field. This could crash player-perspective clients and the blind-playtest harness when those states became visible. Both actions now satisfy the common action contract.
2. The real Part 12 horror runtime stores experienced anomaly IDs as strings, while the Part 15 recurrence handoff assumed mapping objects with a `domain` field. A player dying after real anomaly exposure could therefore crash while starting the next run. Recurrence now derives anomaly domains robustly from authoritative domain counters and corruption logs while tolerating migrated mapping-form rows.
3. The Part 9 diagnostic printed `11/10` despite eleven checks. The denominator is corrected to `11/11`.

The Part 14 diagnostic was updated to reflect the complete terminal-action schema, and the cumulative post-v0.1.0 diagnostic now includes Part 17.

## Certification evidence

- Part 17 focused final integration suite: 12/12 PASS.
- Reduced release-candidate diagnostic: PASS across compile/package integrity, 14/14 structural profiles, player-perspective profile execution, save/load and migration, conversation continuity/parser isolation, scheduler/weather invariants, and transition validation. Real Qwen was intentionally skipped in the environment-side certification and remains available for target-machine execution.
- Long blind profile run: six profiles at up to 700 actions. The balanced-reader profile reached systemic horror and a complete ending path; other profiles demonstrated freedom to remain focused on social, life-sim, investigative, or wandering play.
- Visible-action fuzz play: passed after the action-schema fixes.
- Content JSON parse and frontend JavaScript syntax checks: PASS.

## Known release-quality observations

The blind profiles reveal strong behavioural divergence. Some specialized automated profiles can spend hundreds of actions in narrow loops without advancing the main mystery. This is consistent with player freedom, but it also means v0.2.x balancing should continue to examine whether human players receive enough ambient invitations, social consequences, and changing world cues while pursuing narrow lifestyles.

The automated profile harness is intentionally imperfect as a model of human curiosity. Its results are useful for reachability and repetition detection, not as a substitute for human play.

## Release status

Version finalized as `0.2.0`.

The v0.2.0 architecture roadmap Parts 1–17 is complete. Future work should begin as a new roadmap rather than silently extending this release sequence.
