# Part 1 — World Expansion Architecture

## Scope

Part 1 introduces a data-driven world substrate without replacing the frozen v0.1.0 gameplay loop. Existing location identifiers, player exits, travel timing, NPC transition behavior, story staging, and save behavior remain compatible.

## Architecture

- `content/world/locations.json` is the authored world catalog.
- `backend/core/world_model.py` validates and queries that catalog.
- `WORLD` remains a compatibility view for established game code.
- Runtime mutations live in save state under `world_model`; authored catalog data is never mutated.
- Player travel topology and NPC movement topology remain distinct because v0.1.0 already used different bounded movement semantics.

Each location now carries district, place kind, interior/exterior status, ownership, access policy, weather exposure, seasonal accessibility, services, activity tags, NPC suitability, story tags, investigation tags, ecology hooks, future job hooks, and future economy hooks.

## Part 1 vertical slice

The existing nine-location village is used as the vertical slice. No arbitrary location expansion is included in this first architecture build. The purpose is to prove that the current world can be represented by one validated substrate before adding districts and places.

Queries currently support:

- player neighbors;
- NPC neighbors and transition validation;
- shortest player routes;
- opening-hours/ownership access checks;
- bounded purpose and role suitability scoring;
- public location context for the UI/API;
- detached runtime modifiers, closures, access overrides, and supernatural overlays.

## Compatibility rules

1. Existing IDs are unchanged.
2. Existing player exit labels and targets are unchanged.
3. Existing travel-minute semantics are unchanged.
4. Existing NPC adjacency is preserved exactly and merely moved into authored world data.
5. Old saves receive default Part 1 runtime world state during migration.
6. Supernatural overlays are state, not edits to canonical location definitions.

## Future consumers

Later Parts can consume the substrate for purpose-driven NPC destination selection, opening hours, jobs, services, economy, ecology, seasonal access, investigation affordances, and controlled supernatural corruption. Those systems are intentionally not implemented prematurely in Part 1.
