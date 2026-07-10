# Part 2 — NPC Identity and Personal Lives

Part 2 adds an authored, data-driven identity layer and save-persistent personal-life state for the core cast without replacing frozen v0.1.0 schedules, movement validation, story conversations, relationships, memories, or Director scheduling.

## Architecture

`content/npcs/core_cast.json` is authoritative authored identity data. It defines stable public identity, values, dislikes, social style, private tension, place and weather preferences, baseline needs, bounded obligations, and canon-locked personal-thread seeds.

`backend/core/npc_model.py` validates and queries this catalogue. Runtime state lives separately in `state["npc_lives"]`, preventing simulation drift from rewriting authored canon.

Runtime personal-life state contains needs, current intent, bounded intent history, personal-thread state, daily experiences, and need-update timing. Part 2 implements conservative need drift and exposes identity/life context to ordinary dialogue and the NPC Director. It does not yet implement unrestricted autonomous arc progression.

## Compatibility

Existing NPC IDs and locations are unchanged. Existing authored story conversations remain authored. Existing relationship and social-memory structures remain authoritative for their own domains. Old saves gain `npc_lives` through migration.

## Forward hooks

Part 3 can build NPC-to-NPC relationships on stable identities. Later purpose-driven movement can use needs + obligations + world suitability without replacing the current validated transition graph. Personal arcs can activate authored thread states through explicit conditions rather than LLM invention.
