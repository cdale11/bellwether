# Bellwether v3.13.0 evidence ledger

## Pre-edit findings
- Existing `AIPlayerRunner` already had 17 domain coverage goals, LLM-backed legal action selection, interrupt-safe JSONL checkpoints, live text report generation and a seven-day API start path.
- The existing overnight runner mutated the authoritative live game object, making unattended QA capable of changing the player's active state.
- The report was comprehensive at domain level but lacked an executive triage section, day-by-day campaign summaries, action-frequency evidence and player-visible semantic leakage checks.
- The web console could copy/export the report but did not provide a readable report viewer.
- README release identity/status text was contradictory and stale.
- `backend/core/social_obligation_model.py.tmp` was a stale duplicate temporary source artifact.

## Changes
- Preserved and extended the existing runner instead of creating a competing second playtester.
- Seven-day playtest now runs on an isolated deep-copied game state.
- Added day summaries, action counts, semantic findings and developer-priority report sections.
- Added live/final report viewing and copy workflow in the Developer Console.
- Updated report endpoint to serve the interrupt-safe live report while a run is active.
- Rewrote README and updated release identity.
- Removed stale temporary/generated artifacts.

## Evidence boundary
No live Ollama inference was available in the packaging environment. The runner architecture, report generation, isolated-state contract, syntax and deterministic diagnostics were tested; semantic model quality must be evaluated on the user's local Ollama runtime.
