# Bellwether v2.3.0 Audit — Transport & Rural Mobility

## Pre-edit findings
- `travel_model.py` already owned deterministic route timing, familiarity, route condition, weather penalties, journey logs and encounters.
- `game.py` already routed all movement through `TRAVEL_MODEL.plan/complete`; this was the correct integration seam.
- Traffic vehicles (`bus_7`, delivery van, train) are world simulation entities, not player-owned transport.
- No authoritative player vehicle ownership, fuel, maintenance, cargo capacity, active travel mode or breakdown state existed.
- Therefore v2.3.0 extends travel rather than replacing route topology or traffic simulation.

## Implemented
- New authoritative `transport_model.py` with bicycle → motorbike → car → van progression.
- Purchase, selection, fuel, maintenance, condition wear, breakdown threshold, cargo capacity and journey history.
- Existing route/weather/familiarity calculation remains authoritative; transport applies a bounded multiplier after route planning.
- Fuel and maintenance costs integrate with the existing economy ledger.
- Public transport overview and save migration added.
- Actions are location-gated: purchases/fuel at the village shop; servicing at Workshop Yard; mode selection at sensible locations.

## Verification boundary
- Structurally verified: ownership schema, migration, public view, ledger integration.
- Deterministic-path verified: purchase, selection, speed advantage, fuel consumption, wear, service and cargo overview.
- Existing travel regression verified separately where available.
- Autonomous long-duration AI play: not run.
- Browser-level UI interaction: not run.
