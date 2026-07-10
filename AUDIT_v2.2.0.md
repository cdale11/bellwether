# Bellwether v2.2.0 audit — Business Ownership & Enterprise

## Evidence-first pre-edit findings

The v2.1.0 source was inspected before modification. The existing economy already owned authoritative village-shop stock, dynamic pricing, supply routes, business health, cash reserves, strain, closure/trade availability, produce sales and economy ledger accounting. The job model already provided applications, shifts, wages, reliability, reputation and progression. The property model already provided owned/leased land and a Workshop Yard lease, plus cottage expansion stages.

No authoritative player-owned enterprise model was present. There was no player business startup state, owner-operated versus manager-operated mode, player enterprise staffing, daily business accounts, enterprise failure state, or business-specific public overview. Therefore v2.2.0 adds those missing mechanics without duplicating the village economy, job or property systems.

## Implementation

Added `backend/core/player_business_model.py`. Three small rural enterprises are available through existing world/property/resource loops: a produce stall consuming garden harvest, a preserve kitchen consuming pantry preserves and requiring the cottage work room, and a repair workshop consuming repair supplies and requiring control of the Workshop Yard bay. Enterprises support startup costs, manual operation, manager mode, manager hiring, wages/overheads, daily results, business cash, health, reputation, losses, closure pressure, personal reinvestment, economy-ledger entries and save migration/public view exposure.

## Integration boundaries

The model uses existing authoritative money, economy ledger, garden harvest store, pantry preserves, repair supplies and property state. It does not replace village businesses or the employment model. NPC managers are currently represented as local staffing state rather than named persistent residents; named NPC employment integration remains future NPC-autonomy work.

## Verification

- Python compileall: PASS
- v2.2.0 focused business diagnostic: 11/11 PASS
- v2.1.0 property diagnostic: 11/11 PASS
- v1.1.0 economy/village-change diagnostic: 8/8 PASS
- v1.2.0 life-simulation diagnostic: 10/10 PASS
- v0.8.4 interface-horror diagnostic: 14/14 PASS
- ZIP integrity: performed during packaging

No long autonomous Ollama campaign was run for this release. Browser interaction was not exercised, so UI behavior is structurally integrated through the existing action/view contracts but not browser-certified.

## Cleanup

Removed Python bytecode/cache directories and stale generated diagnostic live reports from the release package. Historical source diagnostics and documentation were retained because they are regression assets, not generated clutter.
