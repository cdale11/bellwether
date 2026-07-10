# Bellwether v3.9.0 Audit

Evidence-first scope: inspected the v3.8.0 package before modification. Reviewed the shared action surface, all action construction in `Game.actions`, action-producing model families, emergent situation execution, presentation ledger integration, AI runtime hooks, frontend action grouping, developer diagnostics, Python sources, JavaScript syntax, JSON assets, shell launcher, and distributable stale artifacts.

## Confirmed defects

1. Action subcategory inference still relied on broad keyword fallback for many families. This could classify mechanically distinct actions as generic ordinary life and made future label changes capable of silently moving actions between subcategories. Fixed with structural family precedence for social interactions, animals, procedural community help, property, enterprise, transport, food status actions, repairs, recovery, story, sleep and rest.
2. v3.7 emergence resolved consequences but did not preserve a general causal provenance chain. Added bounded causal history links.
3. Emergent social tension and opportunities were transient mutations/opportunity rows, not persistent derived social facts that could become future evidence. Added provenance-backed social facts.

## Whole-code checks

- Python source compilation: PASS.
- Frontend JavaScript syntax: PASS.
- JSON asset parsing: PASS.
- `run.sh` shell syntax: PASS.
- Focused v3.9 diagnostics: 12/12 PASS.
- v3.8 backlog/quest reachability regression: 6/6 PASS.
- v3.7 emergence regression: 8/8 PASS.
- v3.6 NPC epistemic projects regression: 9/9 PASS.
- Abstract director `NotImplementedError` methods were inspected as intentional interface contracts, not stale defects.
- Provider exception-swallowing `pass` was inspected in context as bounded cleanup/error tolerance, not an empty feature path.

## Evidence boundary

This release establishes causal provenance and persistent social facts, but does not claim unrestricted artificial-life emergence. Social facts are currently created from a bounded subset of emergent consequences. Later releases should let validated beliefs, obligations, promises, debts and suspicions become inputs to self-generated NPC goals and general capabilities.
