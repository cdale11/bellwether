# Part 3 — Social Web and NPC-to-NPC Relationships

Part 3 adds an authored core-cast social graph and a separate save-persistent runtime relationship layer.

## Added
- immutable authored pair histories, compatibility, friction, meeting contexts and bounded topics;
- runtime affinity, trust, familiarity and tension for each NPC pair;
- autonomous co-location encounter recording with a one-hour cooldown;
- bounded deterministic encounter effects derived from place and current activities;
- bounded shared-topic identifiers as a future Part 10 information-flow hook;
- social context queries for future Directors and dialogue;
- old-save migration and cumulative diagnostics.

## Boundaries
Part 3 does not implement free-form gossip propagation, romance simulation, unrestricted LLM social decisions, or canon mutation. Information-flow rules belong to Part 10. The social web is deliberately a substrate that future events, schedules, dialogue and personal arcs can consume.
