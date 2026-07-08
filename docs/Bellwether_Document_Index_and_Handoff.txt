# Bellwether — Document Index and Handoff Guide

**Status:** Authoritative project entry point  
**Purpose:** Give a fresh developer, coding agent, or LLM the minimum orientation needed to continue Bellwether safely and coherently.

---

## 1. First rule

Do not begin coding from this document alone.

Before modifying Bellwether:

1. inspect the current repository and run the current build where possible;
2. read the authoritative context documents listed below;
3. inspect `VERSION`, current tests, diagnostics, save/migration code, manifests, and the exact implementation of the systems being changed;
4. preserve accepted working behaviour unless the user explicitly requests a design change;
5. implement additively, test regressions, playtest from the player perspective, and return a complete runnable build or complete replacement files.

The repository defines current implementation truth. The documents define design intent, canon, AI authority, engineering rules, and development direction.

---

## 2. Authoritative document set

Read in this order:

### 1. Comprehensive Project Context
Explains what Bellwether is intended to be as a game: player autonomy, life-sim depth, economy, relationships, exploration, horror, recurrence, player identity, UI goals, and long-term scope.

### 2. Engineering Context Snapshot
Explains what the inspected build actually contains: architecture, models, services, frontend, persistence, LLM integration, Directors, map system, diagnostics, technical debt, and extension points.

Treat this as a snapshot, not a replacement for inspecting newer code.

### 3. Canonical World and Story Bible
Defines authoritative hidden truth: Bellwether, the Chorus, metaphysics, historical structure, mystery architecture, recurrence meaning, revelation logic, ending families, and narrative constraints.

Do not procedurally overwrite or casually contradict this document.

### 4. LLM Role, Authority, and Constraint Specification
Defines the most important simulation architecture: Town Mind, specialist Directors, NPC cognition, memory, model routing, asynchronous work, procedural arcs, hallucination prevention, validators, fallback, health degradation, auditability, and allowed/forbidden AI authority.

Core rule:

> The LLM proposes. Validators decide legality. The engine applies. Persistence stores.

### 5. Coding and Implementation Philosophy
Defines how the project must be changed: additive development, behavioural preservation, state authority, save migration, testing, player-perspective playtesting, packaging, coding-agent workflow, regression discipline, and definition of done.

### 6. Post-v0.3.4 Roadmap
Defines the intended development sequence after the map-correction release. Use it to choose coherent release-sized work rather than attempting the entire remaining game in one unstable rewrite.

---

## 3. Precedence when documents or code appear to disagree

Use this order:

1. Current accepted working behaviour must not be accidentally regressed.
2. The user's latest explicit direction overrides older design intention.
3. The Canonical World and Story Bible governs story truth.
4. The LLM Role Specification governs AI authority and AI-system architecture.
5. The latest Engineering Context Snapshot describes the implementation state at the time it was written.
6. The Comprehensive Project Context governs broad intended game direction.
7. The Coding and Implementation Philosophy governs development method.
8. The roadmap governs sequencing, not canon.
9. Older planning notes and visual experiments are historical context unless explicitly promoted to current authority.

If the current repository is newer than a snapshot, inspect the code and update the snapshot rather than forcing the code backward to match stale documentation.

---

## 4. Current handoff baseline

This handoff package is based on the **v0.3.4 Map Correction** line plus project documentation.

The map-correction work should be treated as accepted behaviour unless a later explicit request changes it. In particular, future work must not casually regress:
- the continuous explored-area/parchment-fog map direction;
- route and region reveal behaviour;
- compass behaviour;
- legend visibility;
- current travel integration;
- existing UI functionality;
- existing simulation, persistence, Director, story, horror, relationship, investigation, recovery, recurrence, and fallback behaviour.

Always confirm the exact packaged version and repository state before coding.

---

## 5. How to begin a new development session

A fresh coding agent should:

1. read this handoff guide;
2. inspect the repository tree;
3. read the authoritative documents;
4. run tests and diagnostics;
5. launch the game and observe current behaviour;
6. inspect the exact code paths relevant to the requested feature;
7. identify dependencies, persistence impact, UI impact, LLM impact, and regression risks;
8. define behavioural invariants;
9. implement the smallest coherent architectural change;
10. add or update tests;
11. run targeted tests and the full suite;
12. perform a runtime smoke test;
13. perform relevant player-perspective playtesting;
14. inspect the diff for accidental deletion, simplification, or bypasses;
15. update version/changelog/context snapshot when appropriate;
16. package a complete runnable build.

Do not ask the user to manually edit code when the agent can modify and return the files.

Do not provide illustrative snippets when production-ready implementation was requested.

---

## 6. Bellwether in one engineering paragraph

Bellwether is a persistent state-driven village life-sim/RPG and psychological-supernatural horror game. The player may pursue ordinary life, work, farming, cooking, relationships, exploration, investigation, or combinations of them. The village continues changing offscreen. Authored story and fixed metaphysical truth coexist with an emergent LLM-driven simulation. The deterministic engine owns truth, legality, causality, persistence, calendar progression, resources, and hard rules. The LLM system acts as a constrained hierarchical simulation intelligence that interprets the village, proposes legal developments, manages pacing and environment, helps NPCs reason, supports conversation, and composes novel causal chains from validated primitives. Failure and recurrence preserve town history and selected progression while changing horror pressure. Existing working systems must be extended rather than casually replaced.

---

## 7. Non-negotiable LLM rule

Bellwether depends heavily on LLMs, but no model output is authoritative merely because it sounds plausible.

Every consequential AI path should use, as appropriate:

- compact relevant context;
- explicit role and task;
- positive world grounding;
- explicit authority and non-authority;
- stable entity/action IDs;
- structured output;
- parsing;
- semantic validation;
- state-precondition validation;
- targeted repair;
- bounded retries;
- deterministic fallback;
- health tracking;
- developer audit traces.

Emergence means **unanticipated legal composition**, not unvalidated invention.

---

## 8. Non-negotiable preservation rule

Before changing a system, find out what it already does.

Do not:
- duplicate an existing system because its implementation was not inspected;
- replace working architecture with a smaller toy implementation;
- erase save compatibility;
- move authoritative state into prose or UI;
- let LLM text directly mutate state;
- remove fallback behaviour;
- hide diagnostic failures;
- break executable permissions or packaging;
- simplify away simulation systems to make a new feature easier.

A new feature is complete only when the new behaviour works and accepted old behaviour still works.

---

## 9. Testing expectation

Bellwether requires more than unit tests.

Use:
- unit tests;
- integration tests;
- deterministic simulation tests;
- LLM contract and hallucination tests;
- save compatibility tests;
- UI smoke tests;
- full player-perspective playthroughs.

For substantial releases, test different player styles: social, investigative, life-sim/farming, economic/job-focused, cautious, reckless, story-avoiding, and mixed.

The user should be able to discover the story as a player rather than spoiling themselves to verify whether the game works.

---

## 10. Expected delivery format

The preferred result of a coding task is:

1. a complete runnable versioned build/archive, or
2. when archive delivery is unavailable, complete replacement files with exact repository paths.

Avoid:
- partial snippets;
- pseudo-code;
- instructions requiring the user to manually merge changes;
- claims of completion without runtime/test verification.

Include concise release notes describing:
- version;
- implemented changes;
- migrations;
- tests performed;
- known limitations;
- any diagnostics that remain failing.

---

## 11. Roadmap use

The roadmap is a sequencing guide, not permission to ignore the current repository.

Before starting a roadmap phase:
- audit whether part of it is already implemented;
- preserve existing implementations that work;
- split large phases into coherent releases;
- update the roadmap when implementation reality changes;
- avoid building later systems on temporary shortcuts that contradict the LLM or engineering specifications.

---

## 12. Handoff checklist

Before handing Bellwether to another agent or developer, verify:

- [ ] Current version is identified.
- [ ] Current build launches.
- [ ] Test status is recorded.
- [ ] Known failing diagnostics are recorded rather than hidden.
- [ ] Latest Engineering Context Snapshot matches the build closely enough or is marked stale.
- [ ] Canonical Story Bible is included.
- [ ] LLM Specification is included.
- [ ] Coding and Implementation Philosophy is included.
- [ ] Roadmap is included.
- [ ] This handoff guide is included.
- [ ] Heavy external asset location/workflow is documented.
- [ ] Save compatibility status is known.
- [ ] Recent release changes are summarized.
- [ ] No temporary credentials, secrets, or machine-specific paths are packaged.
- [ ] Next task is stated clearly.

---

## 13. Final instruction to a fresh agent

Treat Bellwether as a living accumulated system, not a blank prototype.

Read before rewriting. Preserve before extending. Keep state authoritative. Make causes traceable. Validate AI output. Maintain deterministic fallback. Test as a player. Let authored truth and emergent simulation coexist.

The objective is not simply to add features.

The objective is to keep making the village more alive without losing what already makes it Bellwether.
