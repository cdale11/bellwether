# Changelog

## v1.0 — Certification

- Decluttered the main utility and action UI without removing game capabilities.
- Added an explicit confirmed fresh-reset path and documented browser reload behaviour.
- Added save provenance metadata, atomic writes, a last-good backup, and backup recovery.
- Added conservative consecutive message and world-event deduplication.
- Removed the generic “village keeps its own quiet rhythm” display fallback in favour of authored location text.
- Prevented immediate actions from being duplicated in category trays.
- Bounded long-session social memory, encounter, AI event, trace, queue-event, and other runtime histories.
- Added certification diagnostics for save semantics, UI preservation, deduplication, story continuity, and package integrity.

# v0.9.1 — Failure, Recovery, and Runtime Performance

- Added single-worker asynchronous background LLM execution for Town Mind and procedural arcs.
- Added legal-result revalidation and stale-result rejection.
- Added preparation checks, injury mitigation, persistent setbacks, and authored recovery routes.
- Reduced parser overhead with precompiled choice-token parsing and compact request serialization.
- Preserved foreground dialogue priority and all-available-thread Ollama requests.

## v1.0 RC1 — Complete Story

- Added an eight-stage deterministic authored story spine from arrival to ending eligibility.
- Connected story progression to ordinary life, place familiarity, investigation breadth, mystery depth, trusted relationships, experienced contradictions, story beats, and recurrence anchors.
- Added protected authored revelations and persistent story-gate history.
- Added current story chapter/objective to the public game view and Developer Console.
- Preserved multiple investigation orders by using accumulated-state gates rather than a brittle single clue path.
- Removed exposure of legacy placeholder ending choices; canonical ending families are reserved for RC2.
- Rewrote README.md as a single coherent current-version document and removed accumulated release drift.

## v0.9.0 — Recurrence Expansion

- Expanded recurrence runtime to schema v2 with migration from schema v1.
- Added latent and returned memory fragments with bounded progressive return across in-game days.
- Added cross-run home, community, inquiry, and institutional anchors derived from authoritative play state.
- Added context-sensitive recurrence awakening locations driven by strong anchors.
- Added richer asymmetric NPC echoes with independent strength, kind, activation day, and activation state.
- Added bounded story residues that preserve selected continuity context without copying mutable quest state wholesale.
- Preserved and strengthened danger instincts across runs.
- Added recurrence developer diagnostics for anchors, latent/returned fragments, NPC echoes, story residues, and awakening history.
- Added v0.9.0 focused recurrence-expansion certification.

## v0.8.4 — Interface Horror

- Added a presentation-only Interface Horror resolver with explicit authority boundaries.
- Added controlled map contradictions that never alter authoritative geography or travel.
- Added bounded text displacement/repetition, portrait tonal shifts, journal inconsistencies, and theme mismatch effects.
- Effects are derived only from active validated horror overlays and expire with their source state.
- Added Developer Console visibility for current presentation effects, provenance, and history.
- Preserved Developer / Settings access and all accepted v0.8.3 systems.
- Added reduced-motion handling for presentation effects.

## v0.8.3 — Horror Consequence and Recovery Depth
- Added persistent player horror strain and recovery state.
- Added witness-gated NPC anomaly aftermath with structured memory and cognition ingestion.
- Added temporary NPC place avoidance after witnessed anomalies and bounded routine filtering.
- Added recovery effects from ordinary life activities without resetting story, inventory, or anomaly history.
- Added gradual NPC recovery and Developer Console aftermath diagnostics.
- Preserved adaptive-horror eligibility, authored anomaly authority, mystery systems, and Developer / Settings access.
- Added focused v0.8.3 diagnostics and repository-wide regression certification.


## v0.8.2 — Adaptive Horror
- Added persistent adaptive-horror profile derived from authoritative player identity and coping style.
- Added bounded domain preference routing for authored eligible anomalies.
- Added mandatory quiet/recovery windows and auditable suppression counts.
- Added domain-diversity scoring to reduce repetitive horror pressure.
- Added adaptive selection logs and Developer Console visibility.
- Preserved authored anomaly catalogue authority and deterministic eligibility gates.
- Added old-save migration and focused v0.8.2 diagnostics.


## v0.8.1 — Regression Integrity Release

- Restored the always-accessible Developer / Settings gear button and preserved the Developer Console.
- Preserved all v0.8.0 mystery expansion systems and content.
- Added a regression-integrity diagnostic covering intentional developer access, API routes, UI anchors, packaged authoritative context, mystery catalogue integrity, and release metadata.
- Packaged the authoritative World and Story Bible and LLM Role/Authority specification alongside the existing engineering/design context documents.
- Re-ran Python compilation, JavaScript syntax validation, focused release diagnostics, cumulative diagnostics, static UI integrity checks, JSON catalogue validation, and save/load smoke checks.


## v0.8.0 — Full Mystery Expansion
- Expanded investigation from 3 to 7 interconnected mystery threads.
- Added dense cross-location evidence graph and seven multi-source hypotheses.
- Added mystery progress states and cross-thread connections.
- Added notebook mystery-thread UI and richer developer investigation diagnostics.
- Preserved testimony/truth separation and optional player-driven investigation.

## v0.7.2 — Procedural Social Arcs
- Added persistent validated multi-day social arc state and migration.
- Added five legal authored arc templates with timed causal stages.
- Added infrequent deep-model template selection with deterministic fallback.
- Added structured memory-event and bounded NPC-concern consequences.
- Added active-arc limits, history, provenance, expiry-by-resolution, and compact context.
- Added focused v0.7.2 diagnostics and exhaustive repository audit.

## Earlier release history

## v0.7.0 — Town Mind Architecture

- Added persistent Town Mind strategic state with bounded, revisable intentions.
- Added infrequent opening and periodic strategic reviews routed to the deep Ollama model.
- Added compact strategic context construction for low-end hardware.
- Added strict predefined intention catalogue, validation, expiry, replacement, history, and deterministic fallback.
- Town Mind intentions influence specialist Director context but cannot directly mutate world state.
- Added migration-safe Town Mind state and focused diagnostics.


## v0.6.1 — Travel and Journey Depth

- Added persistent route familiarity, journey counts and journey history.
- Added first-time route observations.
- Added weather-sensitive and route-condition-sensitive travel duration.
- Added modest familiarity-based route efficiency.
- Added bounded journey encounters using authoritative NPC, weather and ecology state.
- Added safe migration for older saves without travel state.
- Ollama requests now default to all CPU threads available to the Bellwether process, using Linux CPU affinity when available.
- Added focused v0.6.1 diagnostics and audit report.

## v0.6.0 — World Expansion
- Expanded the authored world graph from 9 to 14 locations.
- Added Field Lane, Calder Farm, Bellwether Woods, Old Quarry, and Quarry Caves.
- Added new districts, ecology, investigation, economy/job hooks, and bounded danger entries.
- Integrated new regions with map discovery, route reveal, hobbies, ordinary-life actions, NPC adjacency, and migration-safe location state.
- Preserved integrated Ollama model detection and deterministic fallback.
- Added focused v0.6.0 diagnostic and exhaustive audit report.

# v0.5.2 — Relationship Depth and Social Consequences

- Added persistent structured social acts and per-NPC shared history.
- Added conservative explicit-act extraction for promises, invitations, requests, apologies, insults, agreements, and refusals.
- Added persistent grievances and apology-based grievance resolution.
- Added open commitment retrieval in NPC dialogue context.
- Added relationship-stage derivation without collapsing multidimensional relationship state.
- Added auditable gossip logging tied to catalogue-backed knowledge propagation.
- Added old-save migration and focused v0.5.2 diagnostics.


## v0.5.1 — Village Population and Simulation Tiers

- Added 24 persistent lightweight background residents.
- Added strict resident schema validation, households, occupations, routine archetypes, traits and interests.
- Added batched hourly background simulation with work, commute, school, errands, community and evening routines.
- Added cheap persistent social-link formation without per-resident LLM calls.
- Surfaced lightweight residents in location presence UI while keeping them outside core-NPC cognition and dialogue loops.
- Added old-save migration for the population substrate.
- Added focused v0.5.1 diagnostics and audit documentation.

## v0.5.0 — Complete Core Cast and Memory Foundation

- Expanded the authored core cast from three to six residents.
- Added Asha Patel, Tom Mercer, and Ruth Calder as persistent core NPCs.
- Completed all fifteen pairwise authored social-web edges for the six-person cast.
- Added durable structured event memory, NPC event references, private impressions, unresolved slots, and bounded retrieval context.
- Integrated structured memory into free NPC conversation context and conversation event recording.
- Added migration of new NPCs and memory state into older saves.
- Added fast/deep Ollama task routing configuration while preserving current foreground-priority serialization and fallback.
- Changed recommended default foreground model to qwen3.5:2b and documented qwen3.5:4b strategic installation.
- Added focused v0.5.0 diagnostics and release audit documentation.


## v0.4.2 — Hobbies, Skills, and Personal Routine

- added persistent foraging, birdwatching, fishing, local-history research, and sketching;
- added location, season, weather, and skill-sensitive hobby outcomes;
- added persistent hobby skills, collections, session history, practice dates, and milestones;
- added old-save migration for v0.4.2 activity state;
- integrated hobbies with player activity history and world consequence propagation;
- exposed collection counts in the Inventory panel;
- added focused hobby/skill diagnostic and exhaustive regression audit.

## v0.4.1 — Economy and Work

- added persistent market demand and business pressure state;
- added daily stock deliveries with bounded weather effects;
- added demand-sensitive produce sale prices and bounded pressure pricing;
- added job reliability, career history, progression and modest wage increases;
- added voluntary resignation and reapplication cooldown;
- added daily work-fatigue recovery;
- added v0.4.0 save migration for new economy and job fields;
- added focused economy/work diagnostic and regression checks.


## v0.3.5 — Baseline Certification

- synchronized VERSION and README release metadata;
- restored executable permission for `run.sh`;
- investigated and corrected the stale Part 20 approved-art packaging expectation;
- Part 20 now validates all manifest-declared scene and portrait files;
- synchronized asset manifest metadata to v0.3.5;
- packaged certification and project-direction text documents;
- retained v0.3.4 map correction and existing gameplay behaviour.

# Bellwether v0.3.4

## Fixed
- Corrected the permanent map reference layer: the bottom-left legend is now always visible.
- Replaced the accidental top-right map crop with an isolated compass asset so no hidden geography is exposed.
- Prevented exploration reveals near the Bus Stop from exposing the source map legend frame or other decorative reference graphics.
- Preserved continuous feathered exploration, discovery persistence, route reveal, old-save compatibility, and the live “You are here” marker.

# Bellwether v0.3.3

## Fixed
- Kept the illustrated map legend permanently visible above the exploration fog.
- The legend is now treated as reference UI rather than explorable geography, while all world landmarks remain governed by the persistent feathered exploration mask.
- Preserved discovery persistence, route reveal, old-save compatibility, and the live “You are here” marker.

# Bellwether v0.3.2

## Changed
- Replaced hard-edged map cut-outs with a continuous feathered exploration mask.
- Merged discovered location regions and route corridors into one softened reveal surface.
- Replaced the blurred full-map fog layer with blank, subtly textured parchment so unexplored geography and labels no longer leak through.
- Preserved authoritative discovery state, path reveal, save compatibility, and the live “You are here” marker.

# Bellwether v0.3.1

## Added
- Illustrated exploration map using the canonical Bellwether base map.
- Persistent discovered-location and discovered-path state with old-save migration.
- Fog-of-war style regional reveal and a live “You are here” marker.
- Map keyboard shortcut (`M`) and travel buttons for currently reachable discovered locations.

## v0.2.0 Part 1 — World Expansion Architecture
- Added a validated, data-driven world catalog with districts and rich location metadata.
- Added shared world-model queries for routes, access, suitability, ecology/economy/job hooks, and bounded NPC adjacency.
- Preserved legacy WORLD compatibility, existing player exits, travel timing, NPC movement constraints, and story location IDs.
- Added save-state migration for runtime location modifiers, access overrides, seasonal closures, and supernatural overlays.
- Added focused Part 1 architecture diagnostics and technical documentation.
- No economy, jobs, farming, ecology simulation, new story prose, or unrestricted Director behavior is introduced in this architecture-only build.

## v0.1.0 RC2.1 — Conversation Semantic Grounding
- Recent exact exchanges now use explicit `PLAYER_SAID` and `YOU_SAID` fields to reduce small-model speaker-attribution errors.
- Current player input is now placed after context, immediately before generation, and marked `CURRENT_PLAYER_MESSAGE`.
- Prompt hierarchy explicitly requires answering the current message first; recent conversation is supporting context rather than a replacement topic.
- Added the last two NPC replies as repetition-avoidance context.
- Added a conservative long-term-memory grounding guard that rejects clear topic substitution, including the observed practical-advice question being incorrectly remembered as a weather question.
- Preserved RC2 elapsed-time chronology, daypart grounding, acknowledgement familiarity clamp, and narrow temporal contradiction retry.
- Full deterministic release diagnostic passes: 14/14 structural runs, save/load/migration, parser isolation, scheduler/weather invariants, and balanced full-loop completion remain healthy.
- No simulation, story, horror, Director, weather, save-format, branch, or endgame mechanics were changed.

## v0.1.0 RC2 — Small-Model Conversation Stabilization
- Added elapsed-game-time annotations to exact recent NPC conversation exchanges.
- Conversation context now carries an authoritative derived daypart: morning, afternoon, evening, or night.
- Strengthened chronology grounding so exchanges minutes ago cannot reasonably be described as a long absence.
- Added a deterministic acknowledgement guardrail: short replies such as `Perfect!`, `Okay`, `Thanks`, and similar acknowledgements cannot produce familiarity greater than +1.
- Added a narrow explicit time-of-day contradiction validator. Obvious contradictions such as sunset during morning trigger one corrective foreground retry; broad semantic policing is intentionally avoided.
- Preserved valid dialogue/social parsing and all Part 34 selective-memory behavior.
- Split real-Qwen QA semantics into explicit `first_contact` and `continuity` scenarios.
- Continuity QA now starts from a genuine prior exact exchange rather than mixing first-meeting and repeat-meeting semantics.
- Full deterministic RC diagnostic passes after the patch: 14/14 structural runs, save/load migration, conversation parser/fallback isolation, scheduler/weather invariants, and balanced full-loop reachability remain healthy.
- No new gameplay systems were added.

## v0.1.0 RC1 / Part 35 — Persistence, Recovery, and Release Certification
- Combined Part 35 and the first v0.1.0 release candidate as requested.
- Relationships UI now hides NPCs until the player has actually met or spoken with them.
- Added `tools/release_candidate_diagnostic.py`, a single comprehensive target-machine diagnostic covering compilation, permissions, structural simulation, player-perspective pacing, save/load round-trip, old-save migration, conversation continuity, social parser fallback, scheduler lock state, seasonal temperature movement, transition validation, and real-Qwen continuity/performance traces.
- Enhanced real-Qwen QA output with exact recent exchange, newly created long-term memory, attempt number, result, latency, queue wait, inference time, prompt-eval count, and generation count.
- Added Part 35 RC certification documentation and diagnostic instructions.
- Verified atomic save/load preservation of relationship state, social memory, exact conversation session history, evidence, and old-save migration.
- Local certification without Ollama passed all executed engineering checks.
- Structural certification passed 14/14 profile runs in the RC diagnostic.
- Player-perspective diagnostic demonstrated both non-escalating specialist profiles and balanced routes capable of reaching anomaly escalation and completion.
- Preserved all Part 34 conversation continuity, selective memory, grounded-advice, authored-story protection, living-village, Director scheduling, and controlled-horror systems.

## Part 34 — Manual Narrative Rebuild and Pacing Polish
- Added exact short-term `conversation_sessions` per NPC, separate from long-term social memory.
- Direct Qwen conversations now receive up to three exact recent player/NPC exchange pairs for immediate continuity.
- Strengthened chronology instructions so NPCs do not restart greetings, contradict recent turns, or claim a long absence minutes after meeting.
- Added selective long-term memory consolidation: trivial acknowledgements stay in short-term context but do not crowd persistent social memory.
- Added near-duplicate social-memory suppression.
- Tightened social calibration: brief acknowledgements normally produce familiarity 0..1, with 2 reserved for significant interaction.
- Added grounded-advice rules to prevent ambient NPCs inventing invitations, shared plans, objects, or off-screen events.
- Strips accidental outer quotation marks from visible generated NPC dialogue.
- Added old-save migration for conversation session buffers.
- Manually polished the arrival prose and key early Jonah/Mara authored dialogue for quieter specificity and stronger voice distinction.
- Added a `continuity` scenario to the real-Qwen QA runner reproducing the Mrs Ellis failure sequence.
- Added `docs/PART34_NARRATIVE_REBUILD_AND_PACING.md` with findings, fixes, and target-machine acceptance checks.
- Regression: 7/7 structural profiles passed across 840 actions; known balanced full-loop seed still reaches authored horror and completes an ending.

## Part 33 — Socially Consequential LLM Conversation and Real-Qwen Narrative QA
- Non-story player-authored NPC conversations now affect affinity, trust, and familiarity according to the social meaning of the player's own words.
- Dialogue and social interpretation are produced in one foreground Qwen inference to avoid doubling loading time on low-end CPUs.
- Added NPC-specific social personality context for Jonah, Mara, and Mrs Ellis.
- Social deltas are strictly bounded per turn: affinity -2..+2, trust -2..+2, familiarity 0..+2.
- Neutral conversation is no longer automatically rewarded with fixed positive affinity.
- Meaningful LLM-derived social memories are stored and fed into later conversations.
- Malformed social metadata cannot discard a valid NPC reply; only the metadata is ignored and a neutral +1 familiarity contact effect is used.
- Raw relationship deltas remain hidden from the player.
- Added `tools/real_qwen_narrative_qa.py` for controlled warm, reserved, intrusive, and inconsistent multi-turn continuity testing across all three NPCs.
- Added Part 33 QA methodology and acceptance criteria in `docs/PART33_REAL_QWEN_QA.md`.
- Preserved authored story-dialogue protection: story-bearing conversations still bypass free-text LLM generation.
- Preserved Part 32 progressive player-style context, blind playtesting, pacing gates, and all Part 31 transition guards.
- Post-change regression: 7/7 structural profiles passed; balanced player-perspective run reached horror escalation and completed an ending.

## Part 32 — Player-Perspective Playtesting and Pacing Validation
- Added a player-visible blind-style playtest harness with six play styles and sequential transcript capture.
- Agents choose only from visible prose, quests, locations, present actors, and offered actions; hidden thresholds and source state are not used for decisions.
- Bundled 12 baseline runs and full sequential transcripts.
- Both balanced-reader baseline runs reached authored horror and completed an ending in 218 and 254 actions.
- Blind testing exposed brittle learned-place pacing; horror familiarity qualification was adjusted from 8 to 6 and endgame familiar-place qualification from 10 to 8 while preserving ordinary-life gating.
- Direct player-to-NPC LLM conversation now explicitly receives the evolving compact player-style summary and the last three notable player choices.
- Expanded player-style summary tracks social engagement, dominant life routine, routine strength, investigation tendency, community orientation, and care orientation.
- Preserved the dedicated low-latency foreground conversation path from Part 31.2.
- Preserved Part 31 traffic/NPC transition guards, Part 30.2 observation causality, compact prompts, serialized inference, and 120-minute weather decision cadence.
- `run.sh`, thread benchmark, structural stress test, and blind playtest utility are packaged executable.

Run blind playtests:
`python3 tools/blind_playtest.py --steps 320 --runs 2 --transcript-dir playtest_transcripts`

## Part 31.2 — Dedicated LLM Conversation Path
- Replaced generic expressive generation for player-to-NPC free talk with a dedicated foreground reply path.
- The player reply prompt now contains only local conversational facts needed for continuity and no duplicated global overview payload.
- Trace-equivalent test prompt reduced to roughly 1.1k characters / under 100 words.
- Player dialogue requests use foreground queue priority, thinking disabled, a 48-token output cap, two attempts, and a configurable 75-second per-attempt timeout.
- Successful LLM replies remain the normal path; deterministic fallback remains only as last-resort resilience for an unavailable or repeatedly failed local model.
- Structural regression after the change: 7/7 profiles passed across 840 actions.

## Part 31.1 — Player Conversation Reliability Hotfix
- Diagnosed the Part 30.2 player-conversation failure as a foreground Ollama timeout, not a dialogue parser failure.
- Replaced the full game-overview dump in player-conversation prompts with a compact continuity projection.
- Removed unrelated recent bounded Director choices from direct player-to-NPC conversation prompts.
- Player conversations now receive foreground priority, a configurable 45-second default timeout, and one retry.
- Added intent-aware deterministic fallback replies for farewells, thanks, and greetings, so a timeout after `Thanks, bye!` produces a natural goodbye instead of asking the player to repeat themselves.
- Preserved Part 31 traffic/NPC transition guards and structural stress tooling.
- Post-fix structural regression matrix: 7/7 profiles passed across 840 actions.

## Part 31 — Automated Simulation and Structural Stress Testing
- Added an offline structural stress harness covering social, homebody, investigator, wanderer, avoidant, repetitive, and random player styles.
- Bundled a reproducible 14-run / 1,680-action baseline report; all structural runs pass.
- Added reusable structural validators for impossible traffic locations, invalid NPC locations, stuck Director rounds, and repetition metrics.
- Added actor-specific NPC memory routing: bounded NPC prompts use that NPC's own recent action history, nearby NPC activity, encounters, memories, and relevant world events instead of mixed recent decisions from other NPCs.
- Added local NPC movement validity: NPCs may remain in place or cross one connected world edge per Director decision.
- Added route-phase transition filters for Route 7 bus, delivery van, and Morning train.
- Fixed the bus jump bug: a bus that is `away` can no longer jump directly to boarding or stopping in the village.
- Added corresponding train and delivery-van phase constraints so class-valid states must also be valid next states.
- Added defensive runtime transition guards in proposal application; malformed or stale AI proposals that imply impossible movement are rejected and recorded as `simulation_guard` events.
- Preserved Part 30.2 read-only observation, 120-minute weather decision cadence, compact bounded prompts, full player-conversation memory, serialized inference, coalesced Director scheduling, atomic saves, branch/endgame systems, and executable packaging.

### Structural baseline
Run with:
`python3 tools/stress_test.py --steps 120 --runs 2`

The bundled baseline covers 7 profiles × 2 runs × 120 player actions = 1,680 actions and passed 14/14 structural runs.

## Part 30.2 — Inference Efficiency and Simulation Causality
- Observation is now read-only: `ask_village` describes already-simulated NPC and traffic state instead of triggering a second mutating Director round.
- Time still advances after observation, so due simulation changes happen naturally through the normal scheduler.
- Replaced the shared traffic candidate pool with vehicle-class-specific state libraries for Route 7 bus, delivery van, and train.
- Train states are now restricted to `railway_halt` and `away`; road and village-green train states are impossible.
- Weather LLM decisions now occur every 120 simulated minutes instead of every 50 minutes; temperature still updates chronologically during every time-advance step.
- Compacted bounded weather, NPC, and traffic global-memory projections to remove duplicated season/weather/history data already present in local context.
- Reduced bounded recent-decision memory from four same-domain calls to two.
- Trimmed bounded local event/history windows while retaining actor continuity and current world state.
- Preserved full master playthrough memory for player free-text conversations and rich context for conversational generation.
- Preserved Part 30.1 candidate shortlisting, repetition filtering, deterministic trivial-choice bypass, timing instrumentation, bounded retry policy, and all canonical story protections.

## Part 30.1 — Bounded Director Performance Patch
- Kept the broad 15–20 candidate libraries but added a pre-inference shortlist stage; bounded NPC and traffic calls now see 5–8 varied candidates.
- Immediate repeat action IDs and exact semantic no-ops are filtered before Qwen is called when genuine alternatives exist.
- Candidate shortlisting prefers diversity of action kind and destination, reducing overlapping continuity choices.
- Added deterministic bypass when filtering leaves only one genuine choice, avoiding a pointless LLM round trip.
- Bounded choice generation now requests only 8 output tokens instead of 48.
- Bounded choices use two attempts and a configurable 45-second timeout (`BELLWETHER_BOUNDED_AI_TIMEOUT`) to avoid the Part 29 pattern of 30-second timeout followed by an immediate duplicate request.
- Timed-out retries now use a bounded cooldown before retrying.
- Raw traces now separate AI-gate queue wait, HTTP/Ollama inference time, total latency, and timeout policy.
- Preserved Part 30 context routing, full player-conversation memory, canonical story authority, Director coalescing, request serialization, atomic saves, and Part 29 branch/endgame systems.

## Part 30 — LLM Context Router and Latency Optimization
- Added a task-aware Context Router between persistent master game memory and Qwen requests.
- Weather, traffic, NPC activity, ambient conversation, player conversation, and season selection now receive different global-memory projections.
- Local Director context remains intact; only irrelevant global metadata is omitted from bounded calls.
- Player free-text conversation retains the richest whole-playthrough context for continuity.
- Recent LLM decisions are now routed by task relevance instead of attaching the same mixed history to every call.
- Added prompt character and word counts to raw request traces for latency diagnosis.
- Added an opt-in thread benchmark utility for 2/4/6/8-thread testing without slowing normal game startup.
- Fixed a Part 29 health-cache control-flow regression that prevented enabled health checks from reaching Ollama after cache expiry.
- Preserved Director coalescing, request serialization, foreground priority, atomic saves, branch/endgame systems, and canonical story authority.
- `run.sh` remains executable and reports the optional benchmark command.

## Part 29 — Branches, Recovery, Endgame, and Performance Audit
- Added four persistent play-style branch axes: care, community, inquiry and avoidance.
- Added recoverable setback framework; overwhelming unease and running out of money open recovery actions rather than abrupt game-over states.
- Added authored endgame eligibility based on story progress, lived familiarity, relationships, investigation and experienced anomalies.
- Added four authored ending families: stay, leave, share, and keep; run completion is archived by the existing cross-run context foundation.
- Added branch and ending context to the whole-game LLM overview without allowing AI to author canon.
- Ollama requests now use all detected logical CPU threads by default via `num_thread`, with `BELLWETHER_AI_THREADS` override.
- Added 10-second Ollama health cache to avoid repeated `/api/tags` polling.
- Added whole-game overview caching so unchanged state does not repeatedly rebuild and deepcopy the same metadata for adjacent LLM calls.
- Retained serialized AI generation, foreground conversation priority, coalesced Director scheduling, atomic saves, and API mutation locking.
- Audited all Python and frontend source files for blocking calls, repeated serialization, duplicate Director invocation paths and save-state mutation hazards.
- `run.sh` prints LLM thread count and remains executable.

## Part 28 — Controlled Horror, Temperature Fix, and Simulation Safety
- Fixed time advancement so each 10-minute Village Pulse sees its actual chronological time.
- Temperature now follows the seasonal diurnal target across elapsed time instead of replaying all pulses at the final timestamp.
- Coalesced Director domains during a player action into one AI batch, preventing long activities from launching repeated sequential Director rounds.
- Added per-domain pulse deduplication and a non-reentrant Director round guard.
- Serialized mutating API endpoints around the singleton game state to prevent concurrent action/save/load/talk races.
- Save files are now written atomically through a validated temporary JSON file and replacement.
- Save/load buttons participate in the same frontend request lock and Loading overlay as gameplay requests.
- Added controlled psychological horror that requires learned normality: ordinary play, place familiarity, and authored story prerequisites.
- First anomalies contradict routines the player has genuinely learned; time or supernatural pressure alone cannot force them.
- Added persistent unease, certainty, familiarity disruption, anomaly history and psychological stage metadata.
- LLM overview receives experienced psychological context but is explicitly forbidden from inventing anomalies or advancing horror canon.
- `run.sh` remains executable.

## Part 27 — Whole-Game LLM Context and Story Integration
- Added persistent `llm_context` metadata compiled from authoritative game state.
- Every Qwen choice, value, Director and dialogue request now receives the evolving whole-game overview.
- Overview tracks story status, player play style, notable choices, relationships, investigation, season/weather, NPC positions, recent world history and authored story beats.
- Recent accepted LLM decisions are carried into subsequent calls and persisted in saves.
- Added a compact cross-run archive foundation for future run-based play.
- Added authored story-integration signals triggered by simulation state; AI context can react to them but cannot create canon.
- Story integration now reacts to cottage care, shared garden progress, investigation depth and weather/location combinations.
- Startup terminal output explains the season-selection wait and prints whether Qwen or fallback selected the season.
- Fixed authored dialogue relationship updates to use Part 24 structured relationship state.
- `run.sh` remains executable.

## Part 26 — Seasons, Climate, Expanded Bellwether, and Action Groups
- New games ask Qwen to choose one of ten UK-like seasonal phases; local random fallback is used if AI is unavailable.
- Weather Director receives season, temperature range, local hour and diurnal trend as context.
- Temperature now follows a season-aware day/night curve and changes gradually with weather.
- Added Village Shop, St Bartholomew's Churchyard, Riverside Path and Bellwether Halt.
- Expanded travel graph, location activities, investigation observations, place state and NPC route possibilities.
- Action buttons are grouped into Story & People, Explore & Investigate, Daily Life and Travel.
- Season is shown in the player status line.
- run.sh remains executable in the archive.

## Part 25 — Investigation and Observation Systems
- Added a persistent investigation notebook with evidence, place notes, observation counts, connections, and open leads.
- Added contextual Observe Carefully, Examine the Area Closely, and Review What You Have Noticed actions.
- Investigation depth responds to attentiveness, place familiarity, repeated observation, and live location consequences.
- Evidence can combine into open questions without automatically advancing authored story.
- Added player-facing notebook, relationship, and recent-activity rendering to the sidebar.
- Investigation consumes time, so the village continues living while the player observes and searches.
- Preserved executable run.sh packaging.

## Part 24 — Relationships, Familiarity, and Social Consequences
- Added persistent per-NPC affinity, familiarity, trust, talk counts, interaction time, and impression history.
- Ordinary Qwen conversations now receive the current relationship state as context.
- Ambient conversations gradually build familiarity while avoiding unlimited rapid affinity growth.
- Visible daily-life behaviour can create small social consequences for NPCs who are actually present.
- Relationship impressions persist and feed future conversations.

## Part 23 — Daily Life and Meaningful Time Use
- Added location-specific daily-life activities across the current village map.
- Activities consume distinct amounts of time while Village Pulses and AI Directors continue running.
- Added persistent cottage care, garden work, familiarity, attentiveness, meals, errands, reading, and activity history.
- Ordinary activity can unlock restrained observations and familiarity discoveries without forcing story progression.
- Player garden work now changes the same physical garden state used by the living-world consequence system.
- Daily-life choices are recorded as world events so later systems and Director context can react to how the player spends time.
- Preserved authored story conversations, contextual free-text ambient talk, foreground AI priority, and executable run.sh packaging.

## Part 22 — Contextual Free-Text Conversations
- Added player-authored free-text input for ordinary NPC conversations.
- Story and quest conversations remain authored and cannot be bypassed through the free-text endpoint.
- Ambient Qwen prompts now include evolving story flags, active quests, village focus, NPC memories, recent events, weather, mood, location, activity, and supernatural pressure.
- Each player message produces exactly one NPC reply.
- Added persistent conversational memory of what the player said.
- `run.sh` is executable in the packaged build.


## v0.1.0 — in development

## Part 21 — Single-Reply Talk and Foreground AI Priority
- Each player Talk request now asks Qwen for exactly one short NPC reply instead of generating both sides of a four-line conversation.
- Player conversation generation budget reduced to 48 tokens and still uses top-level `think: false` with a single live attempt.
- Added strict first-line NPC parsing; extra generated lines can no longer make the model speak for the player.
- Added one-line character-specific authored fallbacks for Jonah, Mara, and Mrs Ellis.
- Added a shared Ollama request gate so local generations are serialized rather than competing concurrently.
- Queued player-facing conversation requests receive priority over queued background Director work; an already-running request is allowed to finish normally.
- Talk consequences still update social memory and persistent village world events.


### Part 19
- Expanded NPC Director decisions to 18–20 character-specific, contextually plausible candidates.
- Expanded traffic Director decisions to 19 context-sensitive route candidates.
- Added shuffled option presentation to reduce first-option and fixed-letter bias.
- Added recent-action context, explicit anti-loop guidance, and controlled novelty pressure.
- Raised bounded-choice sampling temperature moderately while retaining strict one-token parsing and `think: false`.
- Ambient conversations now use `think: false`, a 120-token budget, exactly four alternating dialogue lines, and only one live-model attempt.
- Added immediate authored dialogue fallback so a local-model timeout cannot freeze the village for repeated 30-second retries.
- Preserved Part 17–18 consequence propagation: selected varied actions still update actor state, action history, world events, encounters, memories, place state, and future Director context.


### Part 16
- Replaced the unreliable `/no_think` prompt prefix with Ollama's top-level `"think": false` request field for bounded Director choices.
- Preserved thinking mode for expressive conversation generation.
- Added the request's thinking-mode setting to AI debug traces.
- Fixed the bounded-choice fallback parser import so responses such as `B = Clear` can be parsed safely.
- Retained adaptive retry handling as a fallback for genuinely empty or length-exhausted responses.

### Part 15
- Fixed Qwen3 empty responses caused by 12-token generation exhaustion.
- Bounded Director choices now use `/no_think`.
- Increased bounded-choice initial token budget to 96.
- Added adaptive token-budget escalation after empty `done_reason: length` responses.
- Lowered bounded-choice temperature for more stable option selection.
- Kept conversation generation on the expressive generative profile.
- Removed Jonah's redundant return-to-bakery option when already at the bakery.
- Improved semantic duplicate filtering for NPC candidates.
- Preserved full Part 14 AI diagnostics.

### Part 14 Debug
- Complete per-attempt AI request and parser tracing.

### Part 13
- Bounded candidate choices for authoritative state.
- Free AI generation for NPC conversations.


## Part 18
- Added consequence propagation after every Village Pulse and after applied Director rounds.
- NPC movement now changes place state: Jonah can leave the bakery unattended and Mara's garden work accumulates persistent physical progress.
- Co-located NPCs now create persistent encounters and reciprocal social memories that feed later Director decisions.
- Traffic decisions now alter road activity state; location observations preserve off-screen consequences for later player discovery.
- Look and travel arrival actions now surface relevant persistent place consequences.
- Conversation actions now require the NPC to actually be present, preventing dialogue with actors who have moved elsewhere.
- Expanded NPC and traffic Director context with recent world events, encounters, and place state.

## Part 17
- Added character-specific NPC routines and continuity-aware Director context.
- Added recent NPC and traffic action histories to discourage generic repetition and route oscillation.
- Improved semantic candidate separation so character-specific choices do not duplicate continuation choices.
- Added persistent `world_events`: every Village Pulse now leaves a lightweight world consequence even when no AI domain is scheduled.
- Director decisions now create persistent world-event consequences and action-history records, feeding future Director context.

## Part 20 — Mobile Conversations and Request Locking
- Talk actions now follow NPC co-location anywhere in the simulated world.
- Added server-side co-location validation for conversations.
- Added AI-generated player/NPC ambient conversations for ordinary and repeat meetings while preserving authored quest introductions.
- Added immediate authored fallback if local dialogue generation fails.
- Added full interaction locking and animated Loading... overlay while gameplay requests (including LLM-backed pulses and dialogue) are in flight.

## v0.2.0 Part 2 development
- Added authored data-driven core NPC identity catalogue.
- Added validated NPCModel and save-persistent personal-life runtime state.
- Added conservative need drift, obligations, preferences, personal-thread seeds and purpose context.
- Integrated authored identity and personal-life context into bounded NPC Director and ordinary conversation context.
- Added old-save migration for npc_lives while preserving existing relationship, memory and story systems.
- Added focused Part 2 diagnostic and cumulative post-v0.1.0 diagnostic report generator for target-machine regression sharing.

## 0.2.0 Part 3 (development)
- Added authored core-cast social graph and persistent NPC-to-NPC relationship state.
- Added autonomous co-location encounters with cooldown protection and bounded effects.
- Added future information-flow topic hooks and social-context queries.
- Added old-save migration, Part 3 focused diagnostic, and cumulative diagnostic coverage.

## 0.2.0-part4-dev
- Added persistent player activity runtime state.
- Replaced preliminary one-click gardening UI action with prepare, crop selection/sowing, watering, tending, inspection, growth and harvest actions.
- Added weather/moisture, seasonal suitability, weed pressure and crop-health effects.
- Added persistent harvest storage and gardening skill progression.
- Preserved legacy garden progression signals for story/regression compatibility.
- Added old-save migration and Part 4 focused diagnostic.
- Extended cumulative post-v0.1.0 diagnostic through Part 4.

## 0.2.0 Part 5 dev
- Added economy, shops and services substrate.
- Connected seed purchases and produce sales to Part 4 gardening.
- Added persistent ledger and household supplies.
- Extended cumulative diagnostics through Part 5 and corrected compile counting to project source directories.

## v0.2.0 Part 6
- Added persistent jobs, applications, scheduled shifts, wages, attendance history, work reputation and fatigue substrate.
- Connected wages to the Part 5 economy ledger.
- Fixed fresh-game seed inventory: seed stock now begins empty and sowing requires/consumes owned seed units.
- Added Part 6 diagnostic and extended cumulative post-v0.1.0 diagnostics.

## v0.2.0 Part 7
- Added persistent dynamic village event runtime state and authored bounded event definitions.
- Added event scheduling and lifecycle progression through the normal simulation clock.
- Added Late Village Delivery with temporary shop scarcity and resolution restocking.
- Added Village Green Workday with location and NPC activity consequences.
- Added Bakery Oven Repair with job availability effects and server-side stale shift rejection.
- Exposed active location event context through the game view.
- Added old-save migration, focused Part 7 diagnostic, and cumulative diagnostic coverage through Part 7.

## 0.2.0 Part 8
- Added seasonal village-life and ecology substrate.
- Added authored vegetation, wildlife, and village-rhythm profiles for all ten season phases.
- Added weather/time-sensitive ecology activity levels and visible ambient integration.
- Added persistent daily seasonal snapshots and location ecology context.
- Extended old-save migration and cumulative diagnostics through Part 8.

## v0.2.0 Part 15
- Added bounded cross-run recurrence architecture.
- Added compact completed-run archive, lossy memory fragments, inherited danger instincts, and asymmetric NPC familiarity echoes.
- New runs reset mutable world state while preserving only explicit recurrence state.
- Added recurrence context to bounded LLM overview and NPC-specific dialogue context.
- Added Part 15 focused diagnostic and cumulative diagnostic integration.

## 0.2.0 Part 16
- Added connected cooking recipes consuming harvested produce and household stores.
- Added persistent cottage restoration consuming repair supplies.
- Added seasonal cottage prose across all ten seasonal phases.
- Added Part 16 migration and focused diagnostics; cumulative runner extended through Part 16.

## 0.2.0 — Systemic Village Foundation and Release Certification

- Completed the post-v0.1.0 roadmap Parts 1–17.
- Added shared world architecture, NPC personal lives, NPC social web, deep gardening, economy, jobs, dynamic events, seasonal ecology, purpose-driven NPC autonomy, gossip and knowledge propagation, investigation graphs, systemic horror, evolving player identity, causal danger and death, cross-run recurrence, cooking, cottage restoration, and seasonal prose integration.
- Final certification fixed incomplete action schemas for injury treatment and new-run transitions.
- Fixed a critical real-runtime recurrence crash caused by the mismatch between string anomaly IDs and mapping-shaped diagnostic fixtures.
- Corrected Part 9 diagnostic reporting and extended cumulative diagnostics through Part 17.
- Added final release integration diagnostic and long player-profile certification artifacts.

## 0.3.0-part1-dev
- Rebuilt frontend information architecture around scene stage, current prose, contextual action dock, quick actions and compact context rail.
- Added dedicated Journal, Map, Inventory, Relationships, Notebook and Home panels.
- Replaced raw relationship numbers in player UI with bounded interpretive descriptions.
- Renamed Village Mind to Developer Console and hid it behind session developer mode (`?dev=1`).
- Expanded read-only developer diagnostics for simulation, NPCs, events, horror, investigation, economy, recurrence and AI traces.
- Added responsive desktop/tablet/mobile layouts without changing authoritative simulation rules.

## v0.3.0 Part 3
- Integrated the approved Part 3 scene and portrait asset set.
- Replaced Map and Home placeholders with functional state-driven surfaces.
- Added live garden, cooking, and cottage-restoration views wired to existing actions.
- Expanded Inventory, Relationships, and Investigation Notebook presentation.
- Preserved qualitative relationship presentation; raw social dimensions remain developer-only.
- Cumulative post-v0.1.0 diagnostic passes through Part 20.

## v0.4.0 — Living Cottage and Daily Routine
- Added persistent daily-life state with home comfort, routine streaks, daily variety tracking and a 14-day ordinary-life log.
- Added four repeatable day-bounded cottage routines: airing rooms, laundry, hearth care and day planning.
- Connected gardening, cooking and paid work to the shared daily-routine record.
- Sleep now closes and evaluates the lived day, preserving consequences into following mornings.
- Added migration-safe defaults and a focused v0.4.0 ordinary-life diagnostic.

### v0.5.0 integrated Ollama selection update
- Bellwether now discovers compatible models already installed in the local Ollama service.
- Normal play no longer requires model-selection environment variables.
- Low-end routing automatically prefers qwen3.5:2b for foreground work and qwen3.5:4b for strategic work when both are installed.
- If only one compatible model is available, routing degrades to the available model; deterministic fallback remains available when Ollama is offline.
- README and launcher instructions simplified to pull model(s) once and run `./run.sh`.

## v0.6.1 conversation reliability update
- Reduced free-dialogue generation budget from 112 to 48 tokens.
- Constrained NPC free dialogue to short one-sentence replies with a 24-word hard ceiling.
- Replaced duplicated verbatim recent-reply injection with compact recent-conversation summaries.
- Added near-verbatim repetition detection and one bounded corrective retry.
- Added explicit anti-exposition guidance for greetings and casual weather talk.
- Added engine-side trust/familiarity clamps for greetings and short weather small talk.
- Improved diagnostics so repaired dialogue is distinguishable from cleanly formatted dialogue.
- Added `tools/v061_conversation_reliability_diagnostic.py`.

## v0.7.1 — NPC Cognition and Long-Term Memory
- Added persistent bounded cognition state for every core NPC.
- Added explicit fact/belief/rumour/impression/suspicion typing and source provenance.
- Added belief reinforcement, confidence revision logs, concerns, unresolved questions, short-term goals and ambitions.
- Added witness-gated event ingestion and bounded cognition retrieval for free dialogue context.
- Added daily fading of low-confidence subjective beliefs without degrading authoritative facts.
- Added old-save migration and focused v0.7.1 diagnostics.
- Rebuilt README.md to accurately describe the current release, direct Ollama setup, CPU-thread behaviour, AI authority, conversation limits and diagnostic commands.

## v1.0 RC2 — Ending Families and Runtime Optimisation

- Added six deterministic canonical ending families.
- Added state-derived ending eligibility and Developer Console inspection.
- Moved ordinary NPC, traffic, weather, and ambient conversation Director inference to the background worker.
- Added thread-local prompt overview snapshots so background inference cannot race foreground context.
- Preserved one-inference-at-a-time scheduling for low-memory systems.
- Rewrote README in simpler current-state language.

## v1.0 RC3

- Added persistent postgame life after all six canonical ending families.
- Preserved farming, jobs, relationships, hobbies, exploration and side investigation after resolution.
- Added ending-specific postgame village conditions and ongoing postgame activity tracking.
- Added automatic safe harvesting of completed background AI results under the game lock.
- Added detailed queued/running/completed AI job diagnostics and lifecycle event logs.
- Added stale Director-result rejection and explicit applied/rejected/failed result logging.
- Simplified and rewrote README.md for the current release.

## v1.0.1 — Living World Runtime

- Activated a persistent deterministic `world_runtime` environmental substrate.
- Added weather history and slow wetness, drying, soil, river, pollinator, and bird tendencies.
- Added persistent location conditions and player-visible environmental observations.
- Connected environmental tendencies to gardening growth and bounded economy delivery pressure.
- Added old-save migration and Developer simulation visibility for living-world state.
- Audited current LLM execution paths and preserved bounded authority and deterministic fallback.
- Cleaned duplicate documentation, stale generated report copies, and cache artifacts.
- Added the consolidated master context and post-v1 design direction to the packaged docs.
- Updated README, VERSION, CHANGELOG, and handoff documentation.

## v1.0.2 — AI Runtime Architecture

- Replaced FIFO background AI scheduling with a single-worker priority queue that preserves low-memory operation.
- Added explicit AI job domains and priorities so ordinary Director work is serviced before slower strategic reviews.
- Preserved job coalescing and game-thread-only result application.
- Added queue-wait timing, per-kind rolling duration summaries, queued-domain counts, lifecycle event counters, and clearer Developer Console runtime status.
- Added a focused v1.0.2 AI runtime diagnostic.
- Improved the cumulative diagnostic runner with live stage progress, timeout reporting, total/failed counts, elapsed time, and slowest-stage summaries.
- Added v1.0.1 and v1.0.2 focused diagnostics to cumulative certification.
- Removed stale generated diagnostic logs and historical transcript payloads from the distribution package; source diagnostics and authored audit reports remain.
- Updated README and release documentation for the current runtime architecture and diagnostic workflow.

### v1.0.2 follow-up: portable saves and AI log-driven tuning
- Added browser-downloadable `bellwether-save.json` export and local JSON save import; portable saves remain human-readable and copyable.
- Kept atomic Quick Save/Quick Load and last-good backup recovery for the installation-local slot.
- Added structural validation and normal migration/overview rebuild when importing portable saves.
- Reduced strategic Town Mind and Procedural Arc prompt bloat by routing a compact overview projection instead of reattaching the full compiled playthrough overview.
- This change addresses v1.0.1 traces where 4B strategic calls received ~9.4k-character prompts, timed out twice at 45 seconds, and then became stale while ordinary play continued.
