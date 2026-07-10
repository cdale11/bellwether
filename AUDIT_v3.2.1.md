# Bellwether v3.2.1 audit

## Evidence
Inspection of `frontend/static/js/game.js` in v3.2.0 confirmed that all `new_messages`, including `speaker == Narrator`, were mapped into `#dialogue`, while `#narrator-strip` was unconditionally hidden. The HTML and CSS still retained a dedicated narrator strip from the earlier presentation architecture.

## Change
The renderer now partitions the response into dialogue and narration. Player/NPC/Bellwether speech remains in the scene transcript. Narrator rows render in the dedicated narrator strip. Explicit `conversation_exchange` remains authoritative for the immediate free-form exchange and does not suppress narration generated in the same response.

## Scope boundary
No backend history, acknowledgement cursor, story state, action resolver, animal state, or LLM authority contract was changed.
