# Bellwether v0.7.2 — Procedural Social Arcs

Bellwether is a persistent village life-sim/RPG and psychological-supernatural horror game. The deterministic engine owns truth and legality; local LLMs provide bounded dialogue, Director choices, and strategic proposals that are validated before application.

## Run

```bash
./run.sh
```

Open the local address printed by the launcher. If Ollama is unavailable, deterministic fallback keeps the game playable.

## Local Ollama setup

Bellwether detects models already pulled into the local Ollama service. No environment variables or manual model selection are required for normal play.

For the target Intel i3-4160 / 8 GB RAM system, install once:

```bash
ollama pull qwen3.5:2b
ollama pull qwen3.5:4b
```

Then run only:

```bash
./run.sh
```

Bellwether automatically prefers `qwen3.5:2b` for foreground dialogue and routine bounded Director work, and `qwen3.5:4b` for strategic Town Mind tasks. If only one compatible model is installed, the game uses the available model where appropriate. Ollama calls automatically use all logical CPU threads available to the Bellwether process; on an unrestricted i3-4160 this is 4 threads. Linux CPU-affinity limits are respected.

For a faster computer that still has 8 GB RAM, `qwen3.5:4b` can be used as the single installed model. Larger models are not required by this release.

## v0.7.2 highlights

- Persistent multi-day procedural social arcs composed only from legal authored templates.
- Deep-model routing for infrequent arc selection, with deterministic fallback when Ollama is unavailable.
- Five initial causal arc families spanning shop pressure, cottage-garden cooperation, railway routine disagreement, bakery workload, and local-history questions.
- Stage timing across multiple in-game days, persistent active/history state, bounded location-specific player involvement, and safe old-save migration.
- Arc stages create structured memory events and bounded NPC concerns without turning generated prose into objective truth.
- Maximum two simultaneous arcs and infrequent proposal scheduling to protect low-end hardware.
- Town Mind intentions can inform arc selection context but cannot directly create facts, residents, relationships, evidence, or story outcomes.
- v0.7.1 cognition, v0.7.0 Town Mind, concise dialogue, travel depth, and all earlier systems remain intact.

## AI authority boundary

The authority chain remains:

**LLM proposes → parser/validator checks → deterministic engine applies → persistence stores**

NPC beliefs are subjective state. A belief, rumour, impression, or suspicion never becomes objective world truth merely because an NPC or model says it. Canonical facts remain controlled by authored content and deterministic game systems.

## Conversation style

Free NPC dialogue is intentionally concise for both tone and low-end hardware. NPCs are asked for one short natural sentence, normally 4–18 words, with a hard 24-word display/storage ceiling. Recent conversation is compacted, near-verbatim repetition is detected, and ordinary greetings or weather small talk cannot create implausibly large relationship gains.

## Diagnostics

Focused v0.7.2 diagnostic:

```bash
PYTHONPATH=. python3 tools/v072_procedural_social_arcs_diagnostic.py
```

Cumulative regression suite:

```bash
PYTHONPATH=. python3 tools/post_v010_diagnostic.py
```

Release-candidate certification with local Ollama:

```bash
PYTHONPATH=. python3 tools/release_candidate_diagnostic.py
```

Use `--skip-qwen` only for deterministic engineering certification when Ollama is not available.

## Recent release line

- **v0.7.2** — persistent validated multi-day procedural social arcs and causal stage progression.

- **v0.7.1** — NPC cognition, subjective beliefs, concerns, goals, ambitions, revision and bounded retrieval.
- **v0.7.0** — Town Mind strategic intention architecture and deep-model routing.
- **v0.6.1** — journey depth, route familiarity, weather-sensitive travel, short dialogue, repetition guards, and automatic CPU-thread use.
- **v0.6.0** — world expansion to fourteen authored locations.
- **v0.5.2** — structured social consequences, commitments, grievances, and relationship stages.
- **v0.5.1** — 24 persistent lightweight residents and tiered background simulation.
- **v0.5.0** — six-person core cast, durable memory substrate, and local Ollama auto-detection.

See `CHANGELOG.md`, the roadmap, handoff guide, and version audit reports in `docs/` for full development context.
