# Bellwether v1.6.0 — Adaptive Horror and Failure Depth

Bellwether is a local-first village life-sim and psychological-horror RPG. The deterministic engine owns saves, accounting, story gates, hazards and legal state transitions. Local LLMs make bounded choices for world interpretation, NPC behaviour, ecology, conversation, procedural situations and autonomous playtesting.

## This release

v1.6.0 deepens failure without turning Bellwether into a random punishment simulator. Existing authored hazards, injuries and recovery routes remain intact. A new inspectable adaptive failure profile tracks pressure from poverty, injury, psychological strain, village decline and social isolation, with bounded mitigation from preparation, recovery and financial stability. Horror remains authored-only and still requires learned normality before escalation.

The AI tester now uses prerequisite stages for multi-step goals, receives a smaller goal-relevant action surface, defers stalled goals instead of spending the whole run on them, and reports per-goal attempts, deferrals, passive-action share, location diversity and procedural pipeline counters. The diagnostic suite also includes adversarial failure/recovery checks and a deterministic 90-day society soak.

## Run

```bash
./run.sh
```

Open the local address printed by the server. Bellwether expects an Ollama-compatible local model service for AI-assisted systems. Deterministic fallbacks preserve playability when AI is unavailable.

## Saves and diagnostics

Portable game state is stored under `saves/`. Full diagnostics continuously checkpoint to `diagnostics/latest_live_diagnostic.json` and `diagnostics/latest_live_diagnostic.txt`. Per-run evidence is written under `diagnostics/runs/` so interrupted tests still leave useful traces.

Run the focused v1.6.0 certification with:

```bash
PYTHONPATH=. python tools/v140_adaptive_horror_failure_diagnostic.py
```

## Development principle

Gameplay and autonomous certification evolve together. Each gameplay milestone should add both player-facing systems and the tests needed to exercise them naturally, adversarially and over long horizons. Deterministic tests certify invariants; LLM agents test exploration, strategy, semantic coherence, emergent interactions and behavioural quality. Diagnostic reports should expose enough evidence to diagnose problems without requiring spoiler-heavy manual inspection.

See `docs/V1.4.0_ADAPTIVE_HORROR_FAILURE_DEPTH_AUDIT.txt` for the release audit and implementation notes.


## v1.6.0 testing notes
The Developer Console full diagnostic now certifies dynamic side-content lifecycle, exactly-once quest rewards, relationship serialization guards, and AI-player control-plane architecture. During autonomous play, Settings, Developer Console, status polling, and Stop AI Player remain independent of inference; completed choices arriving after a stop request are discarded. Quest lifecycle and reward transactions are exposed in developer diagnostics for copy/paste diagnosis.
