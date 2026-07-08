# Bellwether v0.3.0 Part 1 — UI Architecture and Interaction Grammar

Part 1 restructures the player-facing frontend while preserving the authoritative simulation backend. It introduces a scene-first responsive hierarchy, shallow contextual action categories, quick actions, a compact immediate-state rail, dedicated information panels, and a development-only diagnostics console.

The scene stage is intentionally asset-ready rather than asset-complete. Part 2 will establish the asset bible and populate stable scene/character presentation slots.

Developer mode is enabled by adding `?dev=1` to the game URL for the browser session and disabled with `?dev=0`. The old Village Mind player-facing control is removed. The Developer Console exposes read-only clock/weather, run and recurrence state, player state, NPC positions and activities, simulation/runtime overlays, dynamic events, horror/psychology, investigation, economy/employment/activity state, provider health, AI events and raw request traces.

The interface has dedicated Journal, Map, Inventory, Relationships, Notebook and Home panels. Map and Home are architectural placeholders for Part 3; they do not invent state or bypass the simulation.
