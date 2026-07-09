# Bellwether v1.0.3

Bellwether is a village life-sim, RPG, mystery, and psychological horror game. You can work, garden, cook, explore, build relationships, investigate the village, or ignore the main story for long stretches.

## Run the game

Bellwether uses Ollama on your own computer. Install the recommended models once:

```bash
ollama pull qwen3.5:2b
ollama pull qwen3.5:4b
```

Then start Bellwether:

```bash
./run.sh
```

Open the local address printed in the terminal.

Bellwether detects the CPU threads available to it. Normal setup does not require extra environment variables.

## What the AI does

The game engine owns the real game state. The AI can propose dialogue and bounded village decisions, but validators decide what is legal.

The 2B model handles short dialogue and routine village decisions. The 4B model handles slower strategic work.

Most AI work runs in the background. Walking, gardening, jobs, hobbies, travel, and other ordinary actions should not wait for background AI. Free-form NPC conversation still waits because the reply is needed immediately.

Only one Ollama inference runs at a time on low-memory systems. This avoids unnecessary RAM and zram pressure. Each inference can use all CPU threads available to Bellwether.

## Saving, loading, and browser reloads

Use **Menu** in the top bar to Quick Save/Quick Load, export a portable save file, load a portable save file, view history, or reset the game. **Export Save File** downloads `bellwether-save.json`, a plain JSON file that can be copied, backed up, and loaded into another Bellwether installation.

A browser reload reconnects to the game already running on the server. It does not create a fresh game. If you want to start completely over, use **Menu → Reset to Fresh Game**. Reset asks for confirmation and does not carry recurrence memory forward.

Saves are written atomically. Bellwether keeps one last-good backup and can recover from it if the main save file is damaged. Save metadata records the game version that wrote the save.

## Interface

The main screen keeps common choices visible and groups the rest under People, Activities, Explore, Investigate, and Travel. Actions shown as immediate choices are not repeated inside those category trays.

The Developer / Settings button remains available in the top bar. It shows simulation state, AI queue activity, running jobs, completed jobs waiting for validation, timing traces, and other debugging information.

## v1.0 certification work

This release focuses on the whole game rather than adding another large system. It includes:

- UI and action-list cleanup;
- clearer save, load, reload, and fresh-reset behaviour;
- save backup and provenance metadata;
- repeated-message suppression and cleaner recent-event presentation;
- location-card presentation cleanup;
- bounded long-session histories and cache checks;
- race-condition checks around state access and background AI application;
- story, ending, recurrence, failure, and postgame regression testing;
- language and documentation cleanup;
- package, asset, JSON, Python, JavaScript, and shell validation.

## Project files

Diagnostics are in `tools/`. Design documents and audit reports are in `docs/`.

## v1.0.1 living-world runtime

v1.0.1 activates a persistent environmental runtime beneath the existing season and weather systems. Bellwether now remembers recent weather and carries slow environmental conditions forward: wet periods, drying pressure, soil saturation, river pressure, pollinator activity, and bird activity. These conditions can affect garden growth, local observations, river state, and bounded delivery pressure.

The runtime is deterministic and save-compatible. AI remains bounded: it can handle dialogue and legal strategic choices, while authoritative environmental consequences are calculated and validated by the engine. The Developer / Settings simulation view exposes the living-world runtime and ecology tendencies.

Run the focused check with `python tools/v101_living_world_runtime_diagnostic.py`; run the cumulative suite with `BELLWETHER_AI=0 python tools/post_v010_diagnostic.py`.

## v1.0.3 interaction redesign and timeout efficiency

v1.0.3 strengthens progressive contextual disclosure in the action surface: immediate story, danger, and conversation choices remain visible, while routine life, exploration, investigation, and travel actions stay grouped behind category trays. Repetitive simulation-tick boilerplate is filtered from the Recent Events rail so authored and player-relevant moments carry more visual weight.

The local-AI timeout policy is now role-aware. Routine bounded Directors receive a 75-second single attempt by default, while strategic 4B Town Mind and Procedural Arc decisions receive a 120-second single attempt. This is intentionally not a blind increase plus retry: an HTTP timeout does not reliably cancel an Ollama generation already consuming CPU, so retrying can duplicate computation. Environment overrides remain available through `BELLWETHER_BOUNDED_AI_TIMEOUT` and `BELLWETHER_STRATEGIC_AI_TIMEOUT`.

## v1.0.2 AI runtime architecture

v1.0.2 keeps Bellwether's low-memory rule of one local-model inference at a time, but background work is no longer a simple FIFO line. The background runtime now uses domain-aware priorities: routine Director batches are serviced ahead of infrequent strategic Town Mind work, while the provider's existing foreground dialogue gate continues to give waiting player conversation precedence at the Ollama boundary.

The Developer / Settings AI view now exposes queue policy, queued domains, job priority, queue-wait time, rolling duration summaries, and lifecycle counters. This makes it possible to see whether AI is running, what is waiting, how long work takes, and whether results are applied, rejected as stale, or fail.

A review of real v1.0.1 traces also found that routine 2B bounded calls were parsing and applying correctly, while 4B Town Mind and Procedural Arc calls were receiving unnecessarily large overview payloads, timing out, and becoming stale. v1.0.2 now gives those strategic Directors compact global projections while retaining their purpose-built local context.

Diagnostics are also easier to read. `python tools/post_v010_diagnostic.py` prints compact per-stage progress and writes a JSON report containing elapsed time, pass/fail totals, and the slowest stages. Focused checks are available as `python tools/v101_living_world_runtime_diagnostic.py` and `python tools/v102_ai_runtime_architecture_diagnostic.py`.

### Package hygiene

Release packages retain source diagnostics and authored audit/design documents, but no longer ship obsolete generated diagnostic snapshots or large historical playtest transcript payloads. This reduces package clutter without removing executable diagnostics or gameplay content.

### Next planned update: v1.0.3

The next update is the UI Interaction Redesign: reduce action clutter through progressive contextual disclosure, strengthen the narrative hierarchy, make NPC interaction panels more useful, remove duplicated contextual information, and improve keyboard/input safety while preserving the scene-first, API-driven interface.
