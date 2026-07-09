# Bellwether v1.0.8

Bellwether is a local-first village life-sim, RPG, mystery, and psychological horror game. The deterministic engine owns authoritative state; local LLMs may propose dialogue and bounded decisions, which are validated before application.

## Run

Install Ollama and pull the recommended models once:

```bash
ollama pull qwen3.5:2b
ollama pull qwen3.5:4b
```

Then run:

```bash
./run.sh
```

Open the local address printed in the terminal. Bellwether detects available CPU threads. The 2B model handles routine bounded work and short dialogue; the 4B model is reserved for infrequent strategic work. One inference runs at a time to protect 8 GB systems from RAM and zram pressure.

## What changed in v1.0.8

This is a corrective release before v1.1.0. Narrator text has moved out of the scene artwork into a quieter transcript strip. The catch-up banner now observes the real background runtime in wall-clock time and disappears as soon as AI work and simulation debt clear; it no longer depends on another game tick.

AI scheduler diagnostics now distinguish **merged before inference** from **deferred while a same-key inference is already running**. Completed inference is never discarded merely because a newer request appeared, and the runtime exposes a `wasted_after_inference` invariant that should remain zero.

Procedural village arcs are now surfaced as player-visible side-story opportunities while active. Gardening records growth gain and update timing for diagnosis. Currency uses Bellwether's fictional `¤` mark consistently in runtime UI and economy text.

The Raw State **Copy JSON** button now uses the Clipboard API with a legacy fallback and visible result feedback.

## One-click automatic playtest

Open **Developer / Settings** with the gear button and press **Run Full Game Diagnosis**. The test runs in an isolated disposable world and does not replace your real save. It simulates seven in-game days with mixed, home-focused, exploratory, social, economy, and investigation-oriented behaviour, using legal game action pathways. It audits public view integrity, world runtime, ecology, crop growth, story visibility, procedural arc scheduling, economy structure, horror structure, save serialization, and AI scheduler efficiency.

The percentage is real phase completion, not decorative animation. When it reaches 100%, press **Copy Diagnostic Report** and paste the report into ChatGPT. If clipboard access is blocked by the browser, use **Export Report** and upload the text file instead.

The compact report is intentionally spoiler-minimised. It reports failed checks, warnings, causal summaries, scheduler efficiency, crop lifecycle evidence, and subsystem state without dumping story prose. Raw State remains available for exact debugging when necessary.

## Saving and browser reloads

**Menu** provides Quick Save/Quick Load, portable save export/import, history, and fresh reset. Exported saves are ordinary JSON files that can be copied and backed up. A browser reload reconnects to the game already running on the server; it does not start a fresh run. Use **Reset to Fresh Game** when you want a new game.

## Interface and diagnostics

The scene is the main visual surface. People Here is compact and clickable; portraits and relationship context appear when focusing on a person. Immediate choices are shown first, while routine actions are grouped under People, Activities, Explore, Investigate, and Travel.

Developer diagnostics provide readable Living World, NPC, Events, Horror, Investigation, Economy, and AI Runtime views. Raw State is retained for exact state inspection. For ordinary QA, prefer the automatic playtest so you do not need to inspect spoiler-heavy state manually.

## Focused validation

Run the v1.0.8 structural diagnostic with:

```bash
BELLWETHER_AI=0 python tools/v108_corrective_diagnostic.py
```

Older focused diagnostics remain in `tools/`. Canonical design and engineering context are in `docs/Bellwether_Consolidated_Master_Context.txt` and `docs/Bellwether_Post_v1_Design_Direction_and_Context.txt`.

## Next milestone

The next planned major release is **v1.1.0 — Economy and Village Change**: persistent business health, supply and price consequences, employment changes, ecology-to-economy causality, business crises, player intervention opportunities, and longer causal chains linking weather, land, businesses, jobs, NPC routines, and social consequences.

### v1.0.9 full AI diagnostic
The Developer Console's **Run Full Game Diagnosis** now performs real local-model calls for weather, NPC, traffic, conversation, Town Mind, procedural arcs, and ecology before running an isolated seven-day integration autoplay. On low-end CPUs this is intentionally a long-running stress test. Progress reports both overall completion and real AI calls completed. The exported report is designed to be pasted directly into ChatGPT for diagnosis and does not alter the player's live save.

Ecology is now hybrid-authoritative: measured season, weather, soil saturation, drying pressure, and garden moisture are passed to a bounded ecology Director. The model selects only among legal ecological responses; deterministic code applies the selected crop multiplier, vegetation change, and wildlife movement tendency. This keeps the LLM influential without allowing it to invent arbitrary numeric growth or locations.
