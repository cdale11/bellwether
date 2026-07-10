# Bellwether v3.0.0-rc7 Audit — Mara Interaction Stabilization

## Evidence-first finding

The reported Mara interaction failure was reproduced as a frontend/backend contract mismatch, not an absent NPC or missing story unlock. After Eleanor's letter, the backend correctly made Mara visible and exposed `talk:mara`. However, authored `talk` actions lacked `npc_id` and `npc_name`, while the NPC presence modal finds interactions by those metadata fields. Clicking Mara in the presence list could therefore show **No special interaction is available right now** even though the main action surface contained a valid Talk to Mara action.

Ordinary `free_talk` actions already carried the metadata, so the defect was concentrated in authored/story-bearing NPC introductions.

## Surgical correction

Authored `talk` actions now carry the same NPC identity metadata contract as `free_talk` actions. No story gates, schedules, LLM prompts, relationship mutations, or dialogue content were changed.

## Verification boundary

The focused diagnostic verifies letter unlock, visibility, co-location, action availability, modal identity metadata, authored dialogue opening, choice availability, intro completion, and transition to repeat free-talk. Static JavaScript syntax and Python compilation are also checked. This is contract-level evidence; target-device browser clicking remains separate runtime evidence.
