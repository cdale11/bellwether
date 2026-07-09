# Bellwether v1.1.0

Bellwether is a narrative village life-sim and psychological-horror RPG. The simulation is authoritative and deterministic; local LLMs make bounded decisions, interpret changing conditions, drive NPC/world responses, and support autonomous testing without being allowed to rewrite canonical state.

## v1.1.0 — Economy and Village Change

This release adds persistent business health, cash reserves, staffing, supply routes, demand, stock pressure, bounded dynamic pricing, employment consequences, village economic outlook, player support for strained businesses, and economic history. Weather and world-runtime delivery disruption now propagate into supply conditions. Business health can affect hiring and wages, while accounting remains deterministic.

The release also folds in the v1.0.12 playtest findings. The autonomous player now uses compact task-specific state, numeric low-token choices, goal-aware ranking, direct execution of obvious prerequisite steps, goal-stall replanning, and goal-aware fallbacks. High-frequency action selection no longer receives the broad world context projection used by Directors. Provider traces already record prompt size, queue wait, inference duration and Ollama token/duration fields for performance diagnosis.

Full diagnostics remain isolated from the live save. They continuously checkpoint and now also write append-only per-run decision traces under `diagnostics/runs/`, so interrupted long tests retain evidence. Simulation-duration certification and player-action coverage remain separately visible in the report.

## Run

Requirements: Python 3.10+ and the packages in `requirements.txt`. Ollama is optional for deterministic play but required for real AI-assisted runtime and full AI stress certification.

```bash
./run.sh
```

Open the local address printed by the server. Developer diagnostics are available from the in-game developer panel.

## Local AI

Bellwether automatically discovers supported locally installed Ollama models. Environment overrides remain optional. The runtime uses all CPU threads available to the process by default. Stable specialist contracts, compact domain projections and bounded output budgets reduce unnecessary prompt evaluation and generation.

Useful overrides include `BELLWETHER_AI_THREADS`, `BELLWETHER_AI_NUM_CTX`, `BELLWETHER_AUTOPLAYER_TIMEOUT`, `BELLWETHER_BOUNDED_AI_TIMEOUT`, `BELLWETHER_AI_FAST_MODEL`, and `BELLWETHER_AI_DEEP_MODEL`.

## Save and diagnostics

The normal save/export flow produces copyable JSON. Diagnostic checkpoint files are written to `diagnostics/latest_live_diagnostic.json` and `diagnostics/latest_live_diagnostic.txt`; detailed run traces are stored under `diagnostics/runs/`.

## Design rule

LLMs may propose or choose bounded actions. Money, inventory, business health transitions, stock, jobs, crop growth, story gates, horror authority and save state remain validated by game systems.

### Bounded working sessions

The compact autonomous-player paths can reuse Ollama context tokens for bounded 24-turn working sessions, then rebase. This cache is disposable acceleration only: canonical state, memories, relationships and economy remain in the save and are recompiled from authoritative state.
