# Part 15 — Cross-Run Memory and Recurrence Architecture

Part 15 introduces a deliberately lossy recurrence layer. A finished run is archived as a compact summary, then selected experiences become bounded fragments, danger instincts, and asymmetric NPC echoes. The next run resets mutable world state; it does not copy relationships, inventory, money, crops, investigation progress, or anomaly state wholesale.

## Principles

- Recurrence deepens mystery rather than acting as stat-based New Game Plus.
- Authoritative prior-run summaries remain separate from what the new player character consciously remembers.
- Fragments are selected from authored categories and have bounded text.
- Learned danger can survive as instinct, represented by inherited warnings rather than immunity.
- At most a strongly connected NPC receives an initial familiarity-without-source echo from the immediately archived run.
- New runs remain playable from the ordinary beginning and preserve natural variation.
- LLM context may see bounded recurrence context and an NPC-specific echo, but cannot invent cross-run canon.

## Persistence boundary

Persistent: compact completed-run summaries, fragments, instincts, NPC echoes, transition history.

Reset: current money, inventory, crops, jobs, current relationships, active events, current injuries, current investigation evidence, current anomalies, current world overlays, current NPC positions and needs.
