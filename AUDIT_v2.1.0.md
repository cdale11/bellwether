# Bellwether v2.1.0 Evidence-First Code Audit

Baseline inspected: v2.0.5 Diagnostic Path Repair. Release identity was independently confirmed from `VERSION` before edits.

## Audit conclusion

Bellwether already has broad systemic foundations. The main roadmap risk is duplication, not absence. New releases should extend authoritative owners instead of creating parallel counters.

## Existing systems confirmed in code

- Gardening: 4 crops, seed stock, 3 baseline plots, soil preparation/condition, moisture, weeds, weather/ecology-sensitive growth, harvest storage and produce sale.
- Food: 4 cooking recipes, shop food/produce, player meals, hunger response, 3 preserve recipes, pantry preserves, preservation history and shared-meal action.
- Cottage: authored one-off repairs, daily domestic actions, persistent condition/weatherproofing, weather/season wear, thresholded multi-step repair.
- Economy: deterministic money ledger, stock, dynamic prices, produce demand, supply routes, business health/cash/staffing/demand/pressure/trends, closures and job coupling.
- Jobs: applications, current job state, shifts, wages, reputation/reliability and level progression.
- Hobbies: foraging, fishing, birdwatching, local history and sketching with collections, sessions, skill progression and milestones.
- NPC simulation: schedules/lives, social web, memory, knowledge/gossip, cognition, population tiers, society and social consequences.
- Narrative: authored story model, quest lifecycle, investigation, procedural arcs, endings, postgame and recurrence.
- Horror: systemic horror overlays, aftermath, danger/failure/recovery and bounded interface-horror instructions.
- Town mind: bounded LLM-selected intentions exist, but current intentions are mostly gentle pacing/social/economy/environment/curiosity strategies. The desired adversarial playstyle-responsive consciousness is not yet implemented at the requested depth.
- UI corruption: confirmed end-to-end plumbing exists. Backend derives presentation-only effects from authoritative horror overlays; public state exposes them; frontend applies theme mismatch, text dislocation/repetition, portrait tonal shift, map contradiction and journal inconsistency renderers. Existing diagnostic passes 14/14. This is a real implementation, not only a design document.

## Important depth gaps confirmed

- No prior authoritative player property ownership/lease system was present.
- No prior player land purchase system was present.
- No prior recurring player rent/lease obligation system was present.
- No prior cottage expansion/room progression existed beyond repair/restoration.
- No convincing player vehicle ownership progression exists; traffic simulation is separate.
- Existing relationship systems are broad, but deep authored player romance/marriage/family simulation remains a future gap.
- Economy supports business simulation and failure, but true player business ownership/management and new-business creation need a dedicated later release.
- Town mind needs a later strategic observation/adaptation layer tied to player tendencies and valued assets.

## v2.1.0 Part 1 implemented after audit

A new `property_model.py` is the sole authority for ownership, leases, rent and cottage expansion. It integrates with, rather than duplicates, existing systems:

- Ashcroft Cottage is the baseline owned home.
- Lower Meadow allotment can be leased and adds 2 plots to the existing garden plot list.
- Old Orchard strip can be purchased and adds 2 plots to the existing garden plot list.
- Workshop Yard bay can be leased as workspace foundation for the later business release.
- Leases charge daily rent and track arrears.
- Property acquisition and rent are recorded in the existing economy ledger.
- Cottage expansion is staged: pantry room -> work room -> upper room.
- Expansion is gated by existing cottage condition, existing repair supplies, money and prerequisite work.
- Property state is migrated for older saves and exposed in the public game view.

## Verification evidence

- Python compileall: PASS.
- Frontend JavaScript syntax: PASS.
- JSON asset/data parsing: PASS.
- New property public-path diagnostic: 11/11 PASS.
- Gardening regression: 11/11 PASS.
- Economy regression: 11/11 PASS.
- Content/cottage integration regression: 12/12 PASS.
- Economy/village-change regression: 8/8 PASS.
- Life simulation expansion regression: 10/10 PASS.
- Adaptive horror/failure regression: 5/5 PASS.
- Interface horror regression: 14/14 PASS.

Historical diagnostics that hard-code old release identities or old asset assumptions are not rewritten to manufacture passes. The v2.0.5 certification also contains a season-dependent foraging check that can fail when the selected season has no forage pool; that is a diagnostic determinism issue, not evidence that v2.1.0 property work broke foraging.

## Deliberately not implemented in this part

- Renting properties out to NPC tenants.
- Player business ownership/management.
- Vehicle ownership.
- NPC marriage/family autonomy expansion.
- Authored romance routes.
- Full adversarial town-consciousness strategy layer.
- Story-depth rewrite.
- New UI-corruption effects beyond the already confirmed implementation.

Those remain later roadmap work and should be preceded by focused audits of their current authoritative state owners.
