# Bellwether v3.0.0-rc2 Audit — Ordinary-Life Content Density

## Method
Inspected the RC1 ordinary-life content paths before editing: garden catalogue and growth state, seed economy and produce sale contracts, cooking requirements and consumption, hobby collections, fishing/foraging rewards, preservation, public action exposure, save migration behavior, and representative economy/life-simulation regressions.

## Evidence found
- Gardening was mechanically complete but had only four crops.
- Cooking was mechanically complete but had only four recipes and consumed only garden harvest plus household goods.
- Foraging and fishing had persistent collection state, but those collections did not feed cooking.
- Preservation was mechanically complete but had only three preserve recipes.
- Fish and seasonal forage catalogues were small; deep winter foraging had no discoverable item.
- The existing economy already provided the correct deterministic purchase/sale/ledger contracts, so no parallel shop or currency system was warranted.

## Changes
- Added potato, kale, and garden pea crops with season/growth/water/yield profiles.
- Added corresponding seed items to the existing village-shop economy and produce values to the existing sale/demand system.
- Expanded cooking from 4 to 11 recipes.
- Added deterministic forage-to-cooking and fish-to-cooking ingredient paths using the authoritative hobby collection stores.
- Expanded seasonal forage discoveries and fish catalogue.
- Expanded preservation from 3 to 6 recipes.

## Deliberately unchanged
No new foundational model was introduced. Story authority, Town Consciousness, horror, property, business, transport, NPC life, relationships, and endings were not modified. The release is a density/integration pass over existing ordinary-life systems.

## Verification
- v3 RC2 content-density diagnostic: 11/11 PASS
- Part 16 content integration: 12/12 PASS
- Part 5 economy: 11/11 PASS
- v1.1 economy/village change: 8/8 PASS
- v1.2 life simulation expansion: 10/10 PASS
- Python compilation: PASS
- JavaScript syntax: PASS
- JSON parsing: PASS

## Boundaries
No long autonomous Village Play campaign and no browser-level interaction session were run for this release. The evidence is deterministic path and regression evidence, not long-form experiential certification.
