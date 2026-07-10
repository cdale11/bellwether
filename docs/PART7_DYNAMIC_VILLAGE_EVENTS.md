# Part 7 — Dynamic Village Events and Consequences

Part 7 adds a bounded authored event substrate that changes existing simulation systems rather than creating a disconnected event minigame.

## Architecture

`backend/core/event_model.py` separates immutable event definitions from save-persistent runtime event state. Runtime state records scheduled, active, completed and historical event instances. The simulation clock activates and expires events, and event effects use existing world modifiers, economy stock, job availability and NPC activity state.

## Vertical slice events

- Late Village Delivery: temporarily makes selected Village Shop goods scarce, marks the shop and road through world modifiers, and restocks affected goods when the delivery resolves.
- Village Green Workday: creates a location-level community event and changes relevant NPC activities.
- Bakery Oven Repair: marks reduced bakery production and suspends the bakery helper shift, including server-side rejection of stale work actions.

## Scheduling

Daily event scheduling is bounded and deterministic from authoritative day, weather and season state. This preserves save/load stability while allowing natural variation because weather and seasonal openings vary between runs. Later Parts may allow Directors to select among validated eligible events without changing authored consequence definitions.

## Diagnostics

`tools/part7_dynamic_events_diagnostic.py` verifies runtime schema, activation, world overlays, economy consequences, location context, expiry and cleanup, restocking, job blocking, stale-action rejection, NPC response, old-save migration and authored-canon isolation.

The cumulative `tools/post_v010_diagnostic.py` now runs Parts 1 through 7.
