# Bellwether v3.0.0 Final Certification Audit

## Method

Final work followed the evidence-first sequence: inspect the RC15 package; run existing integrated diagnostics; investigate failures before editing; make the smallest coherent correction; compile and run focused tests; run cross-system regressions; clean generated artifacts; package and verify the archive.

## Release-blocking defect found and fixed

The legacy final integration fuzz test exposed a real player-path crash. `Observe Carefully` is globally exposed at every world location, but `perform_investigation()` indexed bespoke prose dictionaries with `ordinary[loc]` and `deeper[loc]`. Expanded locations such as `east_hamlet` are valid world locations but had no bespoke entries, producing `KeyError: 'east_hamlet'` when a visible legal action was selected.

The correction preserves bespoke authored evidence where it exists and supplies bounded ordinary/deeper fallback observations for expanded locations. The action remains meaningful and legal everywhere it is exposed. A final diagnostic executes both observe and search paths across every authored world location.

## Final certification evidence

- Final certification diagnostic: 8/8 PASS.
- Complete story regression: 13/13 PASS.
- Ending-family/performance regression: 11/11 PASS.
- Postgame/async regression: 13/13 PASS.
- RC8 interaction and quest lifecycle regression: 13/13 PASS.
- Interface Horror regression: 14/14 PASS.
- Frontend JavaScript syntax: PASS.
- Full state JSON serialization round-trip and migration: PASS.
- Deterministic visible-action fuzz after the investigation fix: PASS.
- Investigation observe/search execution across the expanded world: PASS.

Historical diagnostics whose assertions encode superseded reply-length or old release-identity strings are retained as provenance and are not rewritten to manufacture green results. Their relevant replacement contracts are covered by later diagnostics.

## Repository and documentation cleanup

README and VERSION now identify v3.0.0 Final. Generated Python caches, bytecode, stale live reports, temporary diagnostic output and JSONL traces were removed. Historical audits and diagnostic sources were retained where they remain useful regression/provenance assets.

## Evidence boundaries

This package does not claim semantic certification of long live Ollama conversations or physical target-device/browser certification without those runtimes. Deterministic dialogue contracts, frontend syntax, UI structural diagnostics and fallback behaviour are covered; experiential quality still benefits from real local-model and device sessions.
