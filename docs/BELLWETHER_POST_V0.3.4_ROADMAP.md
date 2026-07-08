
## Implementation status update — v0.5.2

Completed through v0.5.2: six-person authored core cast, complete pairwise authored social web, durable structured event/NPC-memory substrate, fast/deep Ollama task-routing readiness, a separate 24-resident lightweight population tier, and persistent structured player social consequences including explicit commitments, grievances, apology resolution, shared history, relationship stages, and auditable catalogue-backed gossip propagation. Full regional expansion remains scheduled for v0.6.x; full Town Mind scheduling remains in v0.7.x.

# BELLWETHER — POST-v0.3.4 DEVELOPMENT ROADMAP

**Roadmap version:** 1.0  
**Baseline:** Bellwether v0.3.4 Map Correction build  
**Date:** 2026-07-08  
**Implementation status:** v0.6.0 World Expansion completed; next planned release v0.6.1 Travel and Journey Depth.  
**Status:** Strategic implementation roadmap for development after the v0.3.4 baseline

---

## 1. Purpose

This roadmap defines the recommended development sequence after the accepted v0.3.4 Map Correction build.

It is a sequencing document, not a replacement for the project's authoritative specifications or the current repository. Every development session must inspect the actual code before modification.

Bellwether must continue to evolve additively. Existing working simulation, conversation, persistence, Director, weather, season, story, horror, relationship, investigation, branch, recovery, recurrence, endgame, UI, map, asset, diagnostic, and deterministic fallback behaviour must be preserved unless an explicit later design decision intentionally changes it.

The goal of the roadmap is to move Bellwether from its current strong systems prototype and visual foundation toward a complete, content-rich village life-sim, psychological horror RPG, and persistent recurrence narrative without creating disconnected systems or prematurely scaling content on unstable foundations.

---

## 2. Authority and precedence

When roadmap wording conflicts with a more authoritative source, use the project's established precedence:

1. Current accepted working behaviour must not be accidentally regressed.
2. Explicit latest user direction overrides older design intention.
3. The Canonical World and Story Bible governs story truth.
4. The LLM Role, Authority, and Constraint Specification governs AI authority and architecture.
5. The Engineering Context Snapshot describes the inspected implementation baseline.
6. The Comprehensive Project Context describes broad intended direction.
7. This roadmap governs sequencing and milestones, not canon.
8. Older planning notes are historical context unless explicitly promoted.

---

## 3. Baseline at v0.3.4

The v0.3.4 baseline already contains substantial working foundations:

- authoritative world geography and travel routing;
- persistent exploration map with discovered locations and paths;
- autonomous NPC purpose and bounded movement;
- NPC social relationships and encounters;
- explicit NPC knowledge boundaries and gossip propagation;
- authored and free-text player conversation;
- compact longitudinal LLM context;
- constrained local Ollama integration with deterministic fallback;
- weather, season, temperature, time, and village pulses;
- ordinary player activities and gardening;
- economy, shops, buying, and produce selling;
- jobs and employment substrate;
- dynamic village events;
- investigation and evidence architecture;
- systemic horror and anomaly eligibility;
- behaviour-derived player identity;
- danger, injury, treatment, death, and terminal outcomes;
- recurrence and bounded cross-run memory;
- cooking and cottage restoration;
- authored quest and branch substrate;
- save/load migration and atomic persistence;
- API-driven visual frontend;
- portrait, scene, and map asset systems;
- extensive diagnostics, blind playtest infrastructure, stress testing, and real-Qwen QA tools.

Known baseline cautions include:

- the cumulative diagnostic has a Part 20 approved-art-packaging mismatch that must be resolved;
- the deeply simulated core cast is still small;
- authored quest, knowledge, mystery, and ordinary-life content density remains limited;
- recurrence implementation is less rich than the newer canonical vision;
- `backend/core/game.py` is highly centralized and should not absorb every future domain system;
- some legacy and newer state domains coexist and must be traced before consolidation;
- documentation/release metadata contains lineage drift that should be cleaned without altering behaviour.

---

# PHASE A — STABILIZE THE ACCEPTED BASELINE

## Milestone A1 — v0.3.5 Baseline Certification and Handoff Hygiene

**Primary objective:** make the current baseline fully green, reproducible, and easy for future coding agents to enter safely.

### Work

- Investigate and fix the Part 20 `approved art packaged` diagnostic mismatch.
- Confirm whether the failure is a diagnostic expectation error, packaging error, or manifest mismatch.
- Synchronize VERSION, release notes, and stale README version headings without changing runtime behaviour.
- Add a concise document index/handoff guide listing authoritative documents, reading order, precedence, baseline version, known failures, launch command, diagnostic commands, and expected deliverable format.
- Verify the asset manifest against packaged assets.
- Classify portrait assets as active canonical, planned, or unused where necessary.
- Preserve heavy-asset externalization workflow and stable asset paths.
- Run Python compilation, JavaScript syntax validation, targeted diagnostics, cumulative diagnostics, save/load round trip, representative old-save migration, UI smoke testing, and map screenshot regression checks.

### Exit criteria

- cumulative diagnostics are green or every remaining failure is explicitly accepted and documented;
- fresh launch works through `./run.sh`;
- save/load and migration tests pass;
- map reveal, marker, compass, legend, and resizing are visually checked;
- documentation entry point is clear;
- no gameplay behaviour is intentionally expanded in this milestone.

---

# PHASE B — COMPLETE THE ORDINARY-LIFE VERTICAL SLICE

## Milestone B1 — v0.4.0 Living Cottage and Daily Routine

**Primary objective:** make an ordinary Bellwether week satisfying even if the player largely ignores the central mystery.

### Systems to deepen

- cottage condition and room-level restoration progression;
- gardening depth: crop calendars, season suitability, health, moisture, weeds, soil condition, harvest loops;
- cooking depth: recipes, ingredient substitution rules where appropriate, meals, skill progression, social use of food;
- household resources and recurring expenses where they improve meaningful choices without creating grind;
- reading, tea, correspondence, tidying, rest, weather watching, and other low-pressure home routines;
- persistent next-day consequences from neglected or completed domestic actions;
- better integration between weather, season, garden state, cottage atmosphere, and ordinary prose.

### Design constraints

Ordinary life must not be filler. It establishes normality, attachment, routines, economic context, and learned environmental expectations that later horror can violate.

### Exit criteria

A player can spend at least one satisfying in-game week focused primarily on home life, gardening, cooking, errands, and social visits, with visible persistent progression and without being forced through the main story.

---

## Milestone B2 — v0.4.1 Economy, Work, and Village Interdependence

**Implementation status:** Completed in v0.4.1 foundation release. Further economic content and LLM-governed validated trends remain additive expansion targets.

**Primary objective:** turn economy and jobs from isolated action sources into causal village systems.

### Work

- expand existing EconomyModel and JobModel rather than create parallel systems;
- add several flexible jobs and at least a small number of longer-term employment paths;
- implement schedules, attendance expectations, progression, reputation, and bounded job loss where appropriate;
- connect businesses to dynamic events, weather, supply pressure, staffing, and local relationships;
- add more meaningful uses for money while avoiding punitive survival micromanagement;
- connect player produce and crafted/cooked goods to real economy paths;
- create causal event chains such as supply disruption → business pressure → schedule change → social consequence → player opportunity;
- add logs explaining economic and employment state changes in developer mode.

### Exit criteria

Different work styles produce meaningfully different weeks, contacts, income patterns, and opportunities while remaining compatible with story avoidance and investigation-focused play.

---

## Milestone B3 — v0.4.2 Hobbies, Skills, and Personal Routine

**Implementation status:** Completed in v0.4.2 with foraging, birdwatching, fishing, local-history research, and sketching as the first coherent subset. Persistent skills, collections, seasonal/location gating, activity-history integration, and PlayerIdentityModel influence are implemented. Deeper NPC, economic, and mystery consequences remain additive future work.

**Primary objective:** broaden the player's identity through chosen behaviour rather than character-creation stat allocation.

### Candidate activities

Implement a coherent first subset, not every idea at once:

- fishing;
- foraging;
- local history research;
- photography;
- birdwatching;
- music;
- volunteering;
- pub/social activities;
- collecting;
- simple crafting.

### Requirements

- activities must use real locations, weather, seasons, time, items, skills, and NPC context;
- progression should use medium-effort goals rather than instant rewards or extreme grinding;
- PlayerIdentityModel should derive meaningful tendencies from repeated behaviour;
- hobbies should create social opportunities, knowledge access, economic side paths, and occasional investigation relevance without becoming mandatory plot keys.

### Exit criteria

At least three substantially different non-story lifestyles are viable and produce different identity, social, economic, and informational consequences.

---

# PHASE C — MAKE THE VILLAGE SOCIALLY DENSE

## Milestone C1 — v0.5.0 Complete Core Cast Expansion

**Primary objective:** expand the deep authored cast from the current small baseline toward approximately 6–7 core NPCs.

### Per-character integration checklist

Every core NPC must include:

- canonical identity and visual reference;
- stable traits and dialogue identity;
- mutable needs and concerns;
- schedule preferences and obligations;
- personal goals;
- social graph edges;
- initial knowledge boundaries;
- relationship dynamics with the player;
- memory hooks;
- ordinary-life scenes;
- authored personal arc structure;
- mystery access boundaries where relevant;
- recurrence sensitivity rules;
- portrait manifest integration;
- deterministic dialogue fallback;
- targeted diagnostics and player-perspective tests.

### Design constraints

Do not create NPCs only to deliver clues. Core NPCs need ordinary lives, relationships with one another, disagreements, commitments, and reasons to exist when the player is elsewhere.

### Exit criteria

The player can form distinct impressions and relationships with the full core cast, and core NPCs visibly affect one another offscreen and in shared spaces.

---

## Milestone C2 — v0.5.1 Lightweight Residents and Village Population

**Primary objective:** make Bellwether feel inhabited without applying core-NPC computational cost to every resident.

### Work

- implement simulation tiers for core, semi-main, and lightweight residents;
- add roughly 20–25 persistent lighter residents;
- give each stable identity, home/work/social anchors, bounded schedules, selected relationships, and limited knowledge;
- batch low-cost simulation pulses;
- allow promotion of selected residents into richer simulation when story or relationship relevance grows;
- prevent procedural systems from inventing residents outside authoritative registries or persisted run-start catalogues.

### Exit criteria

The village feels socially populated and recurring faces are recognizable, while low-end CPU performance remains acceptable.

---

## Milestone C3 — v0.5.2 Relationship Depth and Social Consequences

**Primary objective:** move relationships beyond repeated conversation increments into persistent mutual histories.

### Work

- deepen structured memories and retrieval;
- implement promises, invitations, missed commitments, favours, conflict, repair, gratitude, resentment, and trust boundaries;
- add NPC-to-NPC opinion changes through witnessed or reported events;
- support friendship, rivalry, mentorship, family-like bonds, and optional romance foundations;
- preserve non-romantic routes as fully meaningful recurrence anchors;
- ensure consequential conversation effects are proposed narrowly, validated, and applied by engine logic;
- add explainable causal logs for relationship changes.

### Exit criteria

Relationships can improve, deteriorate, stall, recover, and affect opportunities for reasons the player can understand from play.

---

# PHASE D — EXPAND THE WORLD AND TRAVEL

## Milestone D1 — v0.6.0 Bellwether Region Expansion

**Primary objective:** grow the playable world beyond the initial village slice while preserving the authoritative WorldModel.

### Priority geography

- immediate village expansion;
- woods;
- quarry;
- farms;
- caves and restricted underground spaces where canon permits;
- additional institutions and businesses required by story and ordinary life.

### Requirements

- extend `content/world/locations.json` and WorldModel;
- preserve stable IDs and route validation;
- extend map reveal masks and route corridors from authoritative geography;
- add season/weather suitability and environmental context;
- connect locations to jobs, hobbies, ecology, events, investigation, danger, and NPC schedules;
- test travel, map discovery, save/load, and old saves.

### Exit criteria

The expanded region supports ordinary use, social use, economic use, and investigative use rather than functioning as empty quest corridors.

---

## Milestone D2 — v0.6.1 Layered Travel and Encounters

**Primary objective:** make travel meaningful when appropriate and fast when routine.

### Work

- quick resolution for familiar safe routes where appropriate;
- richer first-time travel observations;
- weather-dependent travel effects;
- schedule-aware social meetings;
- bounded travel encounters;
- discoveries, shortcuts, and route familiarity;
- selective danger as corruption rises;
- supernatural geography contradictions only when authorized by anomaly state.

### Exit criteria

Routine movement is not tedious, while unfamiliar, socially important, dangerous, or anomalous journeys can become memorable events.

---

# PHASE E — DEEPEN SIMULATION INTELLIGENCE WITHOUT SURRENDERING AUTHORITY

## Milestone E1 — v0.7.0 Town Mind and Hierarchical Planning

**Primary objective:** coordinate village-scale emergence using bounded strategic AI rather than arbitrary drama generation.

### Architecture

- deterministic engine remains authoritative;
- Town Mind receives compact aggregate context;
- Town Mind proposes priorities, tensions, or bounded strategic directions;
- domain Directors generate legal candidate responses;
- validators reject illegal, stale, canon-breaking, or unsupported proposals;
- engine applies accepted state deltas;
- deterministic fallback remains available;
- strategic calls occur on slow clocks rather than every action.

### Candidate responsibilities

- village pressure prioritization;
- event focus selection;
- social tension opportunities;
- economy pressure interpretation;
- background arc pacing;
- non-canonical atmosphere coordination;
- adaptive but bounded attention toward unresolved player patterns.

### Exit criteria

The village produces coherent multi-system developments that are causally traceable and reproducible enough to debug.

---

## Milestone E2 — v0.7.1 Long-Term NPC Cognition and Memory Retrieval

**Primary objective:** allow persistent agents to interpret history without feeding small models giant transcripts.

### Work

- separate structured facts, beliefs, impressions, episodic memories, commitments, and current concerns;
- implement bounded retrieval by actor, topic, location, recency, emotional significance, and causal relevance;
- add contradiction handling between belief and authoritative fact;
- prevent knowledge leakage;
- compact old memories while preserving engine-relevant structured state;
- test hallucinated entities, forbidden knowledge, malformed output, and deterministic fallback.

### Exit criteria

NPC conversation and choices can reference meaningful shared history across long play without omniscience or unbounded prompt growth.

---

## Milestone E3 — v0.7.2 Procedural Social Arcs and Errands

**Primary objective:** generate replayable short and multi-day situations grounded entirely in real state.

### Work

- create reusable deterministic arc primitives;
- allow LLM selection or constrained interpretation within legal candidate sets;
- ground arcs in real NPC needs, locations, items, businesses, weather, jobs, relationships, and schedules;
- distinguish procedural opportunities clearly from authored main-story truth;
- allow arcs to fail, change, or resolve without freezing the simulation;
- persist arc state and consequences.

### Exit criteria

Procedural content creates variation and personal stories without fabricating canon or feeling like disconnected random quests.

---

# PHASE F — BUILD THE FULL MYSTERY AND HORROR ARC

## Milestone F1 — v0.8.0 Authored Mystery Expansion

**Primary objective:** translate the Story Bible into a complete, playable investigation structure.

### Work

- expand mystery catalogue into multiple connected threads;
- author evidence chains, testimony conflicts, records, geographic clues, ecological observations, institutional evidence, and recurrence-only insights;
- define hypothesis eligibility and assessment paths;
- make most central truth inferable through play;
- preserve a small deliberate residue of uncertainty;
- avoid omniscient exposition and final-villain lore dumps;
- allow multiple routes to understanding where canon permits.

### Exit criteria

A careful player can form theories, test them, revise them, and understand approximately 90–95% of the central supernatural structure on the most revealing routes.

---

## Milestone F2 — v0.8.1 Adaptive Horror Escalation

**Primary objective:** make horror arise from violated normality, learned routine, attachment, psychology, and recurrence.

### Work

- expand anomaly catalogue while preserving authored canon;
- gate anomalies by familiarity, knowledge, location, routine, relationship, psychology, story phase, and recurrence state;
- add adaptive targeting that selects among legal anomalies rather than inventing truth;
- integrate environmental, social, memory, probability, geographic, and interface manifestations;
- ensure early horror is subtle and deniable;
- preserve playability unless a legitimate failure state is reached;
- record causes and eligibility decisions in developer logs.

### Exit criteria

Horror escalation differs between play styles but remains coherent, fair, and connected to the same canonical truth.

---

## Milestone F3 — v0.8.2 State-Driven Interface and Presentation Horror

**Primary objective:** allow the game's presentation layer to become selectively unreliable without random usability sabotage.

### Candidate effects

- map contradictions;
- discovered routes temporarily disagreeing with reality;
- subtly altered portraits;
- corrected or changing text;
- journal contradictions;
- false but state-authorized notifications;
- impossible timestamps;
- altered quest wording;
- recurrence annotations;
- controlled colour corruption;
- audio suppression or distortion.

### Requirements

Every effect must be tied to authoritative anomaly, psychology, story, or recurrence state. The frontend must not invent supernatural truth.

### Exit criteria

Presentation horror is meaningful, bounded, recoverable where appropriate, and more disturbing because the ordinary UI has become familiar.

---

# PHASE G — RECURRENCE, FAILURE, AND CROSS-RUN STORY

## Milestone G1 — v0.9.0 Recurrence Architecture Expansion

**Primary objective:** align the existing recurrence subsystem with the richer canonical vision.

### Work

- preserve selected completed story milestones across recurrence where canon requires;
- support context-sensitive recovery or awakening locations;
- implement progressive fragmented memory return;
- distinguish literal continuity, emotional echo, instinct, contradiction, and supernatural residue;
- make NPC memory asymmetric and canon-controlled;
- connect strong friendships, community networks, institutional ties, and romance to recurrence anchoring without making romance mandatory;
- preserve danger instincts and other bounded carry-forward state where appropriate;
- add migration from current recurrence schema.

### Exit criteria

Recurrence feels narratively significant rather than like a conventional New Game Plus or simple full reset.

---

## Milestone G2 — v0.9.1 Failure, Recovery, and Authored Death Routes

**Primary objective:** make setbacks and terminal outcomes legible, consequential, and narratively integrated.

### Work

- expand authored hazard and death routes carefully;
- ensure core NPC deaths require authored or validated gates;
- add meaningful prevention opportunities and consequences;
- deepen non-terminal setback recovery;
- connect injury, health, preparation, relationships, and institutional access;
- ensure recurrence does not automatically trivialize death;
- playtest reckless, cautious, underprepared, and socially isolated paths.

### Exit criteria

Failure states are understandable in retrospect, recovery paths are meaningful, and recurrence changes interpretation without erasing consequence.

---

# PHASE H — COMPLETE STORY, ENDINGS, AND POSTGAME

## Milestone H1 — v1.0 RC1 Complete Authored Story Architecture

**Primary objective:** implement the full main story from arrival through late-game convergence.

### Work

- complete authored main quest structure;
- complete Eleanor discovery architecture;
- connect institutional, geographic, social, ecological, historical, and recurrence evidence;
- implement protected revelations and canonical gates;
- support multiple investigation orders where possible;
- preserve player freedom between pressured story moments;
- ensure authored missions coexist with village simulation;
- complete core personal arcs and their interaction with the central story.

### Exit criteria

The complete central narrative can be played from opening to ending eligibility without developer knowledge or debug intervention.

---

## Milestone H2 — v1.0 RC2 Ending Families

**Primary objective:** implement and validate the canonical ending families.

### Ending families

- Incorporation;
- False Escape, used sparingly and only where narratively justified;
- Rupture;
- Accommodation;
- Containment;
- True Liberation-Coexistence.

### Requirements

The deepest ending must depend on broad understanding and lived participation rather than plot-token collection. Relevant requirements may include investigation breadth, recurrence experience, stable identity, social anchors, community trust, geographic understanding, institutional access, preparation, health, Eleanor discoveries, and knowledge of normal village life.

### Exit criteria

All intended endings are reachable, causally understandable, tested from player perspective, and meaningfully reflect how the player lived rather than only the final choice.

---

## Milestone H3 — v1.0 RC3 Postgame Continuity

**Primary objective:** ensure resolution does not simply terminate the world.

### Postgame support

- farming expansion;
- jobs and economy continuation;
- cottage development;
- hobbies;
- festivals;
- relationships and optional romance continuation;
- side mysteries;
- lower-intensity anomalies;
- visitors, departures, and voluntary returns;
- world-state changes reflecting the achieved ending.

### Exit criteria

The player can continue living in Bellwether after resolution, and the world meaningfully reflects the ending achieved.

---

# PHASE I — AUDIO, ACCESSIBILITY, PERFORMANCE, AND RELEASE POLISH

## Milestone I1 — Audio Architecture

Implement a manifest-driven layered audio system with:

- location ambience;
- weather ambience;
- ecological ambience;
- indoor/outdoor filtering;
- time-of-day layers;
- seasonal variation;
- music states;
- supernatural suppression, repetition, desynchronization, and distortion;
- graceful continuation when optional audio files are absent.

Audio state must derive from authoritative game state.

---

## Milestone I2 — Accessibility and Responsive Presentation

Add and validate:

- reduced motion;
- scalable text where practical;
- keyboard navigation;
- focus visibility;
- readable contrast across weather/night/horror states;
- alternatives for information conveyed only through colour;
- mobile portrait and landscape support;
- desktop narrow and wide layouts;
- control of intense flashing or disruptive visual effects;
- audio volume categories and mute controls.

---

## Milestone I3 — Performance and Distribution

### Work

- profile low-end CPU operation;
- measure LLM latency and queue behaviour;
- bound histories and save growth;
- verify simulation scaling with resident count;
- use event-driven updates and separate clocks;
- optimize asset packaging after visual canon stabilizes;
- define PNG/WebP policy and compression targets;
- test clean installation and launch;
- preserve Linux executable permissions;
- document local model setup and deterministic no-AI mode.

---

# 4. Cross-cutting requirements for every milestone

Every milestone must include, where relevant:

1. repository inspection before design;
2. identification of authoritative state owner;
3. dependency tracing before modification;
4. stable IDs and schema awareness;
5. migration/defaulting for persistent fields;
6. deterministic legality and fallback;
7. bounded LLM authority;
8. targeted unit tests;
9. integration tests;
10. cumulative regression diagnostics;
11. save/load round trip;
12. representative old-save migration test;
13. UI smoke test for player-facing changes;
14. screenshot review for visual changes;
15. real local-model QA for changed LLM behaviour;
16. player-perspective playtesting;
17. diff review for accidental deletions or simplification;
18. version update and concise change notes;
19. complete runnable package or complete replacement files.

A milestone is not complete because its new path works in isolation.

---

# 5. Recommended release sequence

The intended sequence is:

| Release | Focus |
|---|---|
| v0.3.5 | baseline certification, diagnostic repair, handoff hygiene |
| v0.4.0 | living cottage and ordinary-life vertical slice |
| v0.4.1 | economy and employment depth |
| v0.4.2 | hobbies, skills, and lifestyle differentiation |
| v0.5.0 | full core cast expansion |
| v0.5.1 | lightweight residents and village population |
| v0.5.2 | relationship depth and social consequence |
| v0.6.0 | regional world expansion |
| v0.6.1 | layered travel and encounters |
| v0.7.0 | Town Mind and hierarchical planning |
| v0.7.1 | long-term NPC cognition and memory retrieval |
| v0.7.2 | procedural social arcs and grounded errands |
| v0.8.0 | full authored mystery expansion |
| v0.8.1 | adaptive systemic horror |
| v0.8.2 | state-driven interface horror |
| v0.9.0 | expanded recurrence architecture |
| v0.9.1 | failure, recovery, and authored death routes |
| v1.0 RC1 | complete authored story architecture |
| v1.0 RC2 | ending families and true-ending validation |
| v1.0 RC3 | postgame continuity and final integration |
| v1.0 | certified complete release |

This numbering is strategic rather than mandatory. If implementation reality shows that two adjacent milestones are inseparable, combine them only after inspecting dependencies. Do not reorder foundational work merely to chase visually impressive features.

---

# 6. Parallel work that may occur without changing the critical path

Some work can proceed alongside the main roadmap when it does not destabilize the current milestone:

- generation and curation of canonical visual assets;
- asset compression experiments on copies;
- writing ordinary dialogue banks;
- drafting item, crop, recipe, hobby, and event catalogues;
- audio asset research and manifest design;
- accessibility audits;
- additional blind-playtest personas;
- performance benchmark expansion;
- authoring evidence and records against locked Story Bible canon;
- documentation cleanup.

Parallel content work must not silently redefine canon or create IDs that conflict with authoritative registries.

---

# 7. Content production targets before v1.0

Exact numbers should remain flexible, but the finished game should aim for sufficient density in the following categories:

- approximately 6–7 deeply simulated core NPCs;
- approximately 15–20 persistent lighter residents, introduced gradually;
- a geographically coherent village and surrounding region including woods, farms, quarry, and canon-relevant underground spaces;
- multiple viable work and lifestyle paths;
- several hobbies with real systemic connections;
- a substantial calendar of ordinary and seasonal events;
- enough authored social and personal content that NPCs do not feel dependent on generated dialogue;
- multiple connected mystery threads with evidence from different domains;
- a broad but bounded anomaly catalogue;
- meaningful recurrence-exclusive content;
- all canonical ending families;
- a continuing postgame state.

Quality and integration take precedence over hitting arbitrary content counts.

---

# 8. Player-perspective certification strategy

Before every major release family, conduct full playthroughs or long-session tests using different player styles:

- highly social;
- investigation-focused;
- cottage/garden-focused;
- economic/job-focused;
- hobby-focused;
- cautious;
- reckless;
- story-avoiding;
- socially isolated;
- mixed naturalistic play.

Assess:

- whether the game is understandable without code knowledge;
- whether ordinary life is enjoyable before horror escalates;
- whether choices are motivated;
- whether the village feels alive when the player ignores systems;
- whether information boundaries remain believable;
- whether investigation is fair;
- whether horror escalation is legible rather than random;
- whether setbacks and recurrence make sense;
- whether relationships have causal continuity;
- whether long sessions become repetitive;
- whether all ending routes are actually reachable;
- whether the game remains usable after long persistence histories.

The project owner should be able to discover the story as a player rather than reading spoiler-heavy debug material to certify it.

---

# 9. Scope discipline

The roadmap is intentionally ambitious, but development should proceed through complete vertical slices rather than simultaneous partial implementation of every planned feature.

Prefer:

**complete small loop → integrate → test → playtest → expand**

over:

**create ten disconnected prototypes → leave all half-finished**

Do not prematurely build a generic simulation engine for hypothetical future games. Build the systems Bellwether needs, using extensible registries, focused models, stable schemas, and narrow integration points.

---

# 10. Final destination

The intended finished Bellwether is a persistent village life-sim and psychological horror RPG in which:

- ordinary life is genuinely worth living;
- the player has broad autonomy;
- NPCs possess persistent lives, memories, knowledge boundaries, relationships, and goals;
- the village changes while the player is occupied elsewhere;
- authored mystery remains coherent and mostly inferable;
- local LLMs add interpretation, variation, and social reactivity without owning truth;
- horror grows from the violation of learned normality;
- recurrence accumulates emotional and investigative significance;
- different lives create different routes through stable canon;
- failure has consequence without making the simulation disposable;
- endings reflect understanding, identity, preparation, and relationships;
- the true resolution changes belonging from possession toward consent;
- the player may continue living in the changed village afterward.

The roadmap should be revised when implementation evidence demands it, but revisions must preserve the central development principle:

> **Preserve what works. Extend existing truth. Build causally. Validate generated behaviour. Test as a player. Deliver complete playable increments.**

---

**END OF POST-v0.3.4 DEVELOPMENT ROADMAP**
