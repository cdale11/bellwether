# Bellwether v2.0.1 — Foundation Certification and Public-Path Corrections

Bellwether is a local-first village life-sim and psychological-horror RPG. The deterministic engine owns saves, accounting, story gates, hazards and legal state transitions. Local LLMs make bounded choices for world interpretation, NPC behaviour, ecology, conversation, procedural situations and autonomous playtesting.

## This release

v2.0.1 is a focused evidence-first certification and correction release. It does not add a new major gameplay domain. It closes player-path gaps found while auditing v2.0.0: purchased bread is now actually exposed as a legal action at Ashcroft Cottage; cottage repairs enforce the intended inspect → prepare → work sequence and cannot be completed remotely; stale or fabricated action IDs are rejected at the public action API; and overnight AI report version metadata follows the packaged VERSION file.

The release also adds a focused v2.0.1 diagnostic for ordinary-life state transitions, fishing inventory, quest reward idempotence, portable save round-tripping, action legality and report metadata. Existing v2.0 systems remain additive and intact.

## Run

```bash
./run.sh
```

Open the local address printed by the server. Bellwether expects an Ollama-compatible local model service for AI-assisted systems. Deterministic fallbacks preserve playability when AI is unavailable.

## Saves and diagnostics

Portable game state is stored under `saves/`. Full diagnostics continuously checkpoint to `diagnostics/latest_live_diagnostic.json` and `diagnostics/latest_live_diagnostic.txt`. Per-run evidence is written under `diagnostics/runs/` so interrupted tests still leave useful traces.

Run the focused v2.0.1 foundation certification with:

```bash
PYTHONPATH=. python tools/v201_foundation_certification_diagnostic.py
```

## Development principle

Gameplay and autonomous certification evolve together. Each gameplay milestone should add both player-facing systems and the tests needed to exercise them naturally, adversarially and over long horizons. Deterministic tests certify invariants; LLM agents test exploration, strategy, semantic coherence, emergent interactions and behavioural quality. Diagnostic reports should expose enough evidence to diagnose problems without requiring spoiler-heavy manual inspection.

See `docs/V2.0.1_FOUNDATION_CERTIFICATION_AUDIT.txt` for the release audit and implementation notes.


## v2.0.0 testing notes
The Developer Console full diagnostic now certifies dynamic side-content lifecycle, exactly-once quest rewards, relationship serialization guards, and AI-player control-plane architecture. During autonomous play, Settings, Developer Console, status polling, and Stop AI Player remain independent of inference; completed choices arriving after a stop request are discarded. Quest lifecycle and reward transactions are exposed in developer diagnostics for copy/paste diagnosis.


## v2.0 action interface and overnight certification
Human and autonomous players now consume the same bounded action taxonomy. The human UI uses progressive disclosure by category and intent; the AI receives the same compact legal surface rather than the visual DOM. `Let the Village Play` writes an append-only checkpoint after every action and generates an extensive overnight soak report on completion or stop.

Currency uses the single crossed-B glyph `฿` in authored labels, action buttons, narration, diagnostics, and status surfaces. Purchased bread is stored and can be eaten as a real action; eating it reduces the hunger-pressure value substantially.

### v2.0.3 diagnostic AI player
The AI Player control now runs a coverage-driven diagnostic campaign. During a run it continuously writes `diagnostics/diagnostic_ai_player_live_report.txt` and `diagnostics/diagnostic_ai_player_live.jsonl`; if interrupted, the latest completed action evidence and coverage ledger remain available. A completed or stopped run writes `diagnostics/diagnostic_ai_player_report.txt`. The report is intended for engineering analysis and can contain detailed gameplay-system evidence.
