# Bellwether v1.2.0 — Life Simulation Expansion

Bellwether is a local-first narrative village life-sim and psychological-horror RPG. The deterministic game engine remains authoritative over state, persistence, accounting, story gates and safety constraints; local LLM systems influence bounded world interpretation, NPC behaviour, ecology, conversation, procedural situations and automated playtesting.

## v1.2.0 milestone

This release expands ordinary life without replacing the existing story or simulation systems. It adds persistent pantry preservation, shared meals, scheduled community participation, long-term life progression, hobby mastery summaries, ordinary non-story social contact, and stronger integration between farming, cooking, hobbies, relationships, community standing and the economy.

The release also folds the v1.1.0 diagnostic findings into the AI testing architecture: goal stagnation is measured semantically rather than by any state change, ordinary NPC interaction is now directly testable without advancing authored story, volatile numeric action maps no longer reuse stale Ollama context, compact-choice parser failures are recorded with richer evidence, the autonomous-player timeout is restored to a generous configurable default, and diagnostic reports expose separate quality dimensions.

## Run

```bash
./run.sh
```

Then open the local address printed by the server. Bellwether expects a local Ollama-compatible model service for AI-assisted features; deterministic fallbacks preserve playability when AI is unavailable.

## Saves and diagnostics

The game save is stored as a local JSON file under `saves/`. Full diagnostic runs continuously checkpoint to `diagnostics/latest_live_diagnostic.json` and `diagnostics/latest_live_diagnostic.txt`, while append-only run evidence is written under `diagnostics/runs/`.

## Development principle

Gameplay and automated certification evolve together. New systems should ship with deterministic invariants plus AI-player coverage, naturalistic play, adversarial play and long-horizon testing where appropriate. Diagnostic reports should expose enough evidence to diagnose failures without requiring spoiler-heavy manual inspection.

### v1.3.0: Society and Generational Time
Bellwether now tracks slow village continuity across the lightweight resident population: households, employment composition, social connectivity, isolation, migration pressure, weekly society snapshots and long-horizon elapsed time. Background residents can be met through inexpensive ordinary social contact without turning every resident into a full LLM-driven core character.

The autonomous tester now certifies society and employment-change surfaces and reports more diagnostic dimensions, including invalid-response, timeout, no-effect, behavioural diversity, goal completion and society continuity metrics.
