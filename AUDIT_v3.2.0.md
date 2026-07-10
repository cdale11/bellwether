# Bellwether v3.2.0 audit — Scene Transcript & Cottage Animals

## Evidence inspected
- v3.1.0 package supplied by the user was unpacked and inspected before editing.
- The frontend scene renderer separated `Narrator` messages into a strip outside the scene image, while the hidden recent-events projection read the full history. This explained why ordinary action consequences could fail to read like foreground scene text.
- Free-form dialogue already had an explicit `conversation_exchange` foreground contract.
- No cottage animal state model existed in v3.1.0.

## Changes
- All newly produced player-facing history rows now render in the scene-image transcript, including Narrator, Bellwether, player, and NPC lines. Free-form exchanges retain priority.
- Added deterministic cottage-animal truth: health, hunger, trust, shelter, feed, production readiness and stored produce.
- Added bounded animal intentions. The LLM may select only from legal intention candidates; deterministic simulation remains authoritative over health, hunger, production, existence and inventory.
- Added asynchronous animal-intention jobs so local inference does not block normal play.
- Added small coop, chickens, ducks, feed, care, trust-building, collection, and a later small goat-shelter/goat path.
- Added an Animals page inside Home.

## Evidence boundary
- Syntax and deterministic model behaviour are locally testable here. Live semantic quality of animal intention selection requires the user's Ollama runtime and is not claimed from this environment.
