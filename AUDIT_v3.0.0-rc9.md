# Bellwether v3.0.0-rc9 audit

## Evidence-first findings

The blank AI Runtime tab was caused by a concrete frontend/backend contract mismatch. `AsyncAIRuntime.status()` returns `queued` and `running` as integer counters and exposes detailed work through `jobs`. The frontend renderer treated `queued` as an array and `running` as a job object, including array spread and `.length` operations on numeric values. This throws during rendering and leaves the tab empty.

RC9 makes the renderer consume the authoritative status shape, adds explicit running/queued/completed counters, job rows, inference accounting, lifecycle counters, and fallback recent runtime events. The Developer Console summary queue pill was corrected for the same numeric contract.

The story-tempo audit also found that the RC4 observer covered investigator, homesteader, entrepreneur, social and wanderer profiles but not the roadmap's romance-focused and avoidant archetypes. RC9 adds those classifications and bounded Town Consciousness responses without changing authored story gates.

## Verification boundary

Deterministic contracts and source/runtime shape are tested. No long Ollama campaign or physical-device browser session is claimed.
