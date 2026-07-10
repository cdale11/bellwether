# Bellwether v3.0.0-rc6 Audit

## Pre-edit findings
- RC5 already had controlled Full Diagnosis and long Village Play, but no fast/targeted tier orchestration and no single QA evidence export.
- Diagnostics remain historically distributed across `tools/`, `diagnostics/`, and one root legacy script. RC6 does not riskily relocate historical regression assets; it adds a stable orchestration layer over selected current diagnostics.
- RC2 crops are `potato`, `kale`, and `pea`. All three seed items are present in `ITEMS` and all three are stocked by `village_shop`, so they are buyable.
- Foraging discovery pools contain edible wild discoveries, not crop seed packets. Therefore the new crop seeds are not forageable. This is coherent with the existing authority model: foraging rewards enter hobby collections while seeds enter garden seed stock through economy purchase actions.

## RC6 implementation
- Added `backend/core/qa_runner.py` with independent Fast Smoke and Targeted Regression tiers.
- Added QA API start/status endpoints and a unified QA Bundle export.
- Added Developer Console controls for Fast QA, Targeted QA, and QA Bundle export.
- Long Village Play remains separate and milestone-only.
- Updated VERSION and README.

## Evidence boundaries
- Tier runner executes diagnostics in subprocesses so certification scripts cannot mutate the live authoritative game.
- Historical diagnostics with explicit old-version assertions may still fail by design; runner reports failures rather than rewriting them.
- No claim of long Ollama soak or target-device browser certification is made here.
