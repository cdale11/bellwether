# Bellwether v3.14.0

Bellwether is a local-first, state-driven village-life RPG that gradually becomes psychological and supernatural horror. Ordinary life is mechanically substantial: gardening, cooking and preservation, fishing and foraging, cottage maintenance, jobs, a dynamic economy, property, small-town businesses, transport, relationships, community life, animals, investigation, authored story, recurrence and systemic horror all share one simulation state.

The current development line makes the local LLM an interpretive part of the game rather than a random-number substitute. Deterministic systems record truth and legal actions; LLM systems form fallible observer-specific theories, revise beliefs, maintain NPC projects, compose grounded situations, form goals from persistent social facts and obligations, and influence contextual intentions. The engine validates evidence references and owns all authoritative mutation.

## Run

Requirements: Python 3.11+, packages from `requirements.txt`, and an Ollama-compatible local model service for the full AI experience.

```bash
./run.sh
```

Open the local address printed by the server. Saves are stored under `saves/`.

## Recommended local AI configuration

Bellwether defaults to a single-model policy. When Qwen 3.5 4B is available it is preferred for both fast and deep roles, with 4096 context and a 10-minute idle keep-alive. The purpose is to avoid the high RAM pressure caused by keeping separate 2B and 4B runners resident at the same time.

Environment overrides remain available:

```bash
export BELLWETHER_AI_FAST_MODEL='your-model-tag'
export BELLWETHER_AI_DEEP_MODEL='your-model-tag'
export BELLWETHER_AI_NUM_CTX=4096
export BELLWETHER_AI_KEEP_ALIVE=10m
./run.sh
```

On memory-constrained hosts, use the same model tag for both roles. The Developer Console memory/runtime view warns when fast and deep roles resolve to different models.

## AI authority boundary

The deterministic engine owns saves, money, inventory, legal actions, schedules, story gates, clues, endings, hazards and world mutation. The LLM may interpret evidence, form hypotheses, choose among bounded legal intentions, propose registered situation primitives and generate constrained dialogue. Evidence-backed interpretation is stored separately from objective history, and different observers can disagree.

The current interpretive loop is:

**history → observer-specific evidence → interpretation → hypotheses/projects/goals → legal intentions → deterministic consequences → persistent social facts and obligations → new history**

## Player UI

The main scene separates dialogue from narration. A VN-style **Backlog** button near the narrative area opens the complete player-visible text history with filtering, search and pagination. The Life Book groups Today, People, Home, Work, World, Mystery and Things without exposing backend subsystem names.

## Developer Console

Open the gear button in the top bar. The default Overview is human-readable; advanced tabs expose detailed subsystem state, AI runtime, Town/Adversary interpretation, memory usage and raw state.

The main QA controls are:

- **Run Fast QA** — quick deterministic health checks.
- **Run Targeted QA** — broader subsystem regression checks.
- **Run Full Game Diagnosis** — controlled integrated certification.
- **Run 7-Day Overnight AI Playtest** — isolated human-like autonomous campaign using the legal player action surface and local LLM decisions.
- **Let AI Play the Village** — autonomous play on the authoritative campaign state; every action and consequence persists exactly as normal player actions do.
- **View Live/Final Report** — displays the current interrupt-safe report directly in the web UI.
- **Copy Complete Report** — copies one comprehensive text report suitable for pasting into ChatGPT for analysis.
- **Export Overnight Report** — downloads the same report.
- **Export QA Bundle** — packages QA evidence.

### Overnight AI playtester

The seven-day playtester runs on an isolated clone of the current game state, so it cannot consume or corrupt the player's active save. It pursues changing gameplay goals, traverses the world, exercises ordinary-life and story-adjacent surfaces, performs periodic save round-trip checks, records action diversity, checks domain-specific consequences, detects exceptions and silent no-effect actions, inspects player-visible text for obvious AI boilerplate/raw structured output, and writes an interrupt-safe live report after every action.

The final report contains an executive summary, developer priorities, day-by-day campaign summaries, action diversity, a domain coverage ledger with reasons for gaps, anomaly journal, visited locations, recent live trace and provider telemetry. If the run is interrupted, the latest live report remains available.

Runtime diagnostic artifacts are created under `diagnostics/` only when diagnostics are run. Generated traces and reports are not shipped in the release archive.

## Testing philosophy

Bellwether uses evidence-first development. Release claims should be supported by source inspection plus relevant runtime or deterministic evidence. Historical release claims are not assumed true merely because an old changelog says they were implemented. For each release: inspect current code, preserve accepted behaviour, make the smallest coherent extension, run focused and regression checks, clean generated artifacts, and package the complete release.

Long live-model semantic quality and physical target-device browser behaviour remain runtime evidence boundaries unless tested on those actual environments.


## Local model policy (v3.14.0)
Bellwether prefers a single resident `qwen3.5:4b` model for all AI roles. If it is not installed, discovery falls back to `qwen3.5:2b`, then the legacy small-model options. Fast and deep roles resolve to the same discovered model unless explicitly overridden. Default context is 4096 and default Ollama keep-alive is 10 minutes.
