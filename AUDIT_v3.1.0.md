# Bellwether v3.1.0 — Player Information Architecture & Diagnostic Comprehension

## Evidence-first inspection

Inspected v3.0.0 Final before editing: `frontend/templates/index.html`, `frontend/static/js/game.js`, `frontend/static/css/game.css`, `backend/app.py`, `backend/ai/provider.py`, and `backend/core/town_mind_model.py`, plus the supplied runtime screenshots.

Confirmed findings:
- Status exposed raw values and skill levels without player interpretation.
- The main screen permanently duplicated side stories and recent history already available in persistent panels.
- `Life & Work` mixed employment, maintenance, and ordinary-life actions.
- Journal rendered completed and active quests at equal prominence.
- Inventory mixed carried items, household stores, produce, and hobby counters.
- Relationship impressions could repeat verbatim.
- Home header exposed internal progression counters rather than household condition.
- Developer Console defaulted to subsystem telemetry and raw v2.x snapshots.
- Town Consciousness state was exposed as JSON but did not answer whether opposition was adaptive, effective, or bounded.
- The foreground reply parser could promote format-instruction boilerplate such as `SOCIAL metadata on its own line.` into visible dialogue when model formatting degraded.

## Surgical changes

- Main scene now keeps only the current thread in the right rail; side stories live in Today/Journal and history remains available through Menu.
- Persistent navigation is reframed as a Life Book: Today, People, Home, World, Mystery, Things.
- Action categories are reframed as Talk, Care, Work, Explore, Travel.
- Status is now Player & Household: interpreted survival bands, cottage condition/weatherproofing meaning, progression explanation, and skill proficiency labels.
- Journal separates Now, Also available, and collapsed Completed content.
- Inventory consolidates pantry and harvest stores and collapses collection counters.
- Relationship impressions are deduplicated before display.
- Home header reports cottage condition and active garden use instead of raw progression counters.
- Developer Console opens on a human-readable Overview and adds an Adversary Inspector summarizing inferred player values, confidence, strategy, reason, recent action, outcome, adaptation evidence, fairness signal, and pressure history.
- Raw technical diagnostics remain available; no authoritative simulation state was moved into the frontend.
- Foreground dialogue parser rejects known SOCIAL-format boilerplate instead of displaying it as NPC speech.

## Evidence boundary

The Adversary Inspector reports evidence already present in deterministic Town Mind state. It does not claim semantic intelligence that has not been observed. Long campaign effectiveness still requires autonomous comparative campaigns; this release makes the existing evidence human-readable and exposes where evidence is absent.
