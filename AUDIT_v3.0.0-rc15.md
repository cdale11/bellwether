# Bellwether v3.0.0-rc15 — Content & Narrative Polish Audit

## Method
Inspected the rc14 codebase before editing. Reviewed player-facing action construction, procedural side-story templates and lifecycle prose, ordinary-life cooking outcomes, story/quest content files, dialogue-expression contracts, and frontend rendering surfaces. Changes were limited to evidence-backed content clarity defects and repeated generic outcomes.

## Findings and changes
1. Procedural side-story titles were grammatically valid but read like internal simulation summaries (for example, chains of obligations and questions drawing memory and evidence together). These are now concise player-facing thread titles.
2. Procedural involvement actions mechanically worked but exposed the awkward generic form `Offer to help with: <simulation label>`. Each authored arc now has a concrete action label describing what the player will actually do.
3. `Exchange a Few Words with <name>` duplicated the separate free-form `Speak to <name>` path and sounded mechanically vague. The bounded five-minute social action is now clearly labelled `Greet <name>`; its existing character-specific response remains unchanged.
4. Eleven distinct recipes shared one identical generic completion paragraph. Recipe consumption and rewards were already distinct, so the smallest coherent change was recipe-specific outcome prose without altering mechanics.
5. Story and quest authority was not changed. No chapter gates, evidence truth, quest rewards, ending eligibility, LLM authority boundaries, or simulation mechanics were modified.

## Verification boundary
Certification covers source contracts, Python parsing, content JSON parsing, action-label replacement, recipe-specific outcomes, and placeholder-prose scanning. It does not claim a full long-campaign semantic review of every possible runtime combination or live Ollama dialogue quality.
