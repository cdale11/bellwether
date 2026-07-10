# Bellwether v0.3.0 Part 3 — Functional Game Surfaces

Part 3 converts the Part 1 placeholder information architecture into state-driven game surfaces while preserving the authoritative simulation backend.

Implemented player surfaces:
- knowledge-driven Map showing only the current place, visited/observed places, and currently reachable routes;
- expanded Inventory with carried items, household stores, and garden produce;
- portrait-backed Relationships with qualitative relationship language and remembered impressions, without raw affinity/trust/familiarity numbers;
- Investigation Notebook with unresolved leads, evidence, and connections;
- Home overview using the approved cottage interior artwork;
- live Garden view with plots, crop growth stage, moisture, weeds, soil, seed stock, harvest store, skill, and real garden actions;
- live Cooking view with known recipes, ingredient readiness, meals cooked, skill, and real cooking actions;
- live Restoration view with completed repairs, pending work, supplies, and real repair actions.

Approved artwork integrated in this build:
Ashcroft Cottage, Cottage Interior, Bus Stop, Village Green, Village Road, Bakery, Village Shop, Clinic, Blacksmith, and portraits for Mara, Jonah, Agnes, Elise, and Dr Vale.

All panel actions call the existing `/api/action` path. No parallel frontend simulation state was introduced. Existing v0.1.0 and v0.2.0 systems remain authoritative.
