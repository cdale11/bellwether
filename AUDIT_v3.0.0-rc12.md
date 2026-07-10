# Bellwether v3.0.0-rc12 audit

## Scope and evidence method
Inspected the RC11 foreground conversation provider, free-talk endpoint and game-thread conversation path, scene dialogue renderer, authored Jonah/Mara choice blocks and resolvers, ordinary core-NPC greetings, lightweight-resident greetings, action labels, and representative story/content diagnostics before editing.

## Confirmed defects
1. Foreground free-form replies had been expanded in RC11 to 1–3 sentences / 60 words. This exceeded the requested conversational discipline and could encourage tangent-prone small-model output.
2. The scene renderer depended only on the ordinary unread-message cursor. Free-form conversation was recorded in history and conversation sessions, but there was no explicit response contract guaranteeing that the just-completed exchange would be rendered in the scene dialogue window after UI acknowledgement/cursor changes.
3. `society:greet:*` attributed narration beginning “You exchange...” to the resident as if the resident had spoken it.
4. `social:greet:*` offered a named NPC interaction but resolved to the same meta-text for every core NPC. The option therefore did not connect to a character-meaningful response.

## Changes
- Free-form NPC replies are prompted and hard-clamped to 1–2 sentences and 30 words maximum; normal target is 6–28 words.
- `/api/talk` game response now exposes the completed `conversation_exchange`; the scene renderer prioritizes that exchange for the dialogue window.
- Lightweight resident greeting outcome is narrator prose, not a false quotation.
- Jonah, Mara, and Mrs Ellis ordinary greeting actions now resolve to concise character-specific lines.
- Added RC12 language/dialogue certification covering reply bounds, transcript contract, greeting attribution, core greeting specificity, authored choice resolution, placeholder prose, Unicode integrity, non-empty labels, and release identity.

## Language, interpretation, and meaning audit boundary
The audit covered player-facing prose and labels in the central game/conversation paths plus authored Jonah/Mara choices and their response branches. Automated hygiene checks also covered placeholder markers and malformed Unicode in the audited core prose. This is not a claim that every dynamically generated LLM sentence has been semantically certified without a live Ollama campaign.

## Verification
- RC12 language/dialogue certification: 10/10 PASS.
- Complete Story diagnostic: 13/13 PASS.
- Interface Horror diagnostic: 14/14 PASS.
- Historical v0.6.1 Conversation Reliability: 7/9; its two failures are stale source-shape expectations for the former 96-token/single-short-sentence contract. Behavioral repetition repair and conversation compaction checks pass.
- Python compilation: PASS.
- JavaScript syntax: PASS.

## Cleanup
Removed Python caches, bytecode, stale live diagnostic reports, and JSONL runtime traces before packaging. Historical source diagnostics and audits were retained as regression/provenance assets.
