# Bellwether v2.8.0 Audit — Village Evolution and Long-Term Change

## Evidence-first audit
The v2.7.0 source was inspected before editing. Existing systems already provided: persistent lightweight residents and schedules; household labels and social links; society summaries for employment, migration pressure and aging time; sparse NPC employment changes and household-change considerations; village-business health, supply, prices and temporary inability to trade; player property, enterprise ownership, transport, relationships, Town Consciousness and resistance.

## Confirmed gap
Those systems changed individual state and reported pressure, but there was no authoritative cross-system ledger of structural village evolution. Migration pressure did not materialise into persistent departures/returns; household considerations did not become household moves; business distress had no long-term closure/reopening history; resident self-employment could not create new village ventures; and land use did not evolve.

## Implementation
Added `backend/core/village_evolution_model.py`, migration-safe state, weekly sparse deterministic evolution, reversible resident departures/returns, household moves from prior considerations, business closure/reopening records, resident venture creation, land-use evolution, world-event integration and a public overview. Authored story and map canon are not rewritten.

## Boundaries
No births, deaths, marriages, mystery facts or authored revelations are generated. Population entities are preserved even when away. New resident ventures are simulation records, not fabricated fully-authored shops with unsupported inventories or dialogue.
