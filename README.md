# Bellwether v3.5.0 — Interpretive Intelligence Foundation

Bellwether is a state-driven village-life RPG whose local LLM is now used not only for dialogue and bounded choices, but for fallible interpretation of validated play history. Objective simulation truth remains deterministic; interpretive agents may form revisable theories grounded in event IDs and later use them as strategic context.


**Release status:** v3.3.0 narration-surface correction on the v3.2 cottage-animal foundation. The v3 RC line integrated and certified ordinary-life depth, dialogue expression, strategic Town Consciousness behaviour, UI/UX resilience, diagnostics, interaction contracts, story tempo, content language, and release integrity. See `AUDIT_v3.0.0_FINAL.md` for final evidence and remaining runtime boundaries.

Bellwether is a local-first, state-driven rural village life simulation and psychological/supernatural horror RPG. Ordinary life is intentionally substantial: gardening, cooking, preservation, fishing, foraging, cottage repair and expansion, work, economy, property, enterprise, transport, relationships and autonomous village change coexist with an authored mystery, recurrence, adaptive horror and a bounded Town Consciousness.

## Run

Requirements: Python 3.11+ and the packages in `requirements.txt`. An Ollama-compatible local model service is recommended for AI-assisted systems; deterministic fallbacks preserve core playability when inference is unavailable.

```bash
./run.sh
```

Open the local address printed by the server. The game is local-first and stores saves under `saves/`.

## Architecture and authority

The deterministic engine owns saves, accounting, legal actions, story gates, clues, endings, hazards and authoritative state transitions. Local LLM systems are bounded advisers/selectors for conversation, NPC interpretation, ecology, weather, procedural situations, Town Mind intentions and autonomous playtesting. LLM output is not allowed to invent story canon, bypass authored gates or mutate arbitrary state.

The public human UI and diagnostic AI player consume the bounded legal action surface. Long-running AI diagnostics checkpoint live evidence so interrupted runs remain useful.

## Major gameplay systems

The current release includes ordinary-life activities and skills; gardening, cooking, pantry and preservation; fishing and seasonal foraging; survival status and cottage condition/repair; jobs and career progression; dynamic village economy and shortages; property ownership, leases and cottage expansion; player enterprises; bicycle-to-van transport progression; autonomous NPC lives and village evolution; authored relationship routes and household progression; investigation, authored story, narrative connective scenes, quests and endings; Town Consciousness strategy; resistance and recovery counterplay; recurrence; systemic horror; and bounded interface corruption.

## Developer Console and diagnostics

Open the gear button in the top bar. The Developer Console exposes Living World, NPC, Event, Horror, Investigation, Economy, AI Runtime and Raw State diagnostics. The RC line includes a dedicated **v2.x Systems** tab exposing read-only snapshots for property, enterprises, transport, NPC lives, relationship life, Town Consciousness strategy, resistance, village evolution, narrative expansion, story-consciousness integration and systemic-horror integration.

The console provides **Run Fast QA**, **Run Targeted QA**, **Run Full Game Diagnosis**, **Let the Village Play**, and **Export QA Bundle**. Fast QA is the normal per-build tier; Targeted QA runs broader subsystem regressions; Full Diagnosis is controlled integrated certification; Village Play is reserved for milestone/soak testing.

Diagnostic output is written under `diagnostics/` during runs. Export filenames now follow the packaged `VERSION` instead of a stale hard-coded release name.

## Testing

Focused deterministic diagnostics live in `tools/` and `diagnostics/`. Historical diagnostics are retained when they still provide regression value; some old release-identity assertions are expected to fail against newer versions and must not be rewritten merely to inflate PASS counts.

For RC work, use layered evidence: syntax/JSON validation → focused subsystem diagnostics → cross-system regressions → public gameplay paths → autonomous milestone soak testing → browser interaction verification.

## Release status

This package is the v3.0.0 final certification release. Final certification includes deterministic story and ending regressions, save-state JSON round-trip and migration checks, action-surface fuzz testing, UI/JavaScript syntax checks, economy and long-term simulation checks, and focused regressions from the RC line. Long live Ollama dialogue quality and target-device browser behaviour remain runtime evidence boundaries rather than claims made from static certification.

## RC3 dialogue and character expression
Foreground and ambient conversations now receive bounded authored voice constraints plus relevant autonomous-life, social-web, and knowledge context. This improves character distinctiveness and continuity without giving the LLM authority over canon or simulation state.