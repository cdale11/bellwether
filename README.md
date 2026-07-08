# Bellwether v0.5.0 — Complete Core Cast and Memory Foundation

Bellwether v0.5.0 expands the deeply simulated authored cast from three to six core residents and introduces the first durable structured memory substrate required for later relationship depth, procedural social arcs, and the Town Mind. It is an additive upgrade from v0.4.2.

## Run

```bash
./run.sh
```

Bellwether uses local Ollama models when available and retains deterministic fallback behaviour when AI is unavailable.

## Local Ollama models — automatic in-game use

Bellwether now discovers compatible models already pulled into the local Ollama service and uses them directly. **No model exports, environment-variable setup, or manual model selection is required for normal play.**

For the target i3-4160 / 8 GB RAM machine, install once:

```bash
ollama pull qwen3.5:2b
ollama pull qwen3.5:4b
```

Then simply run:

```bash
./run.sh
```

The game automatically prefers `qwen3.5:2b` for foreground and routine simulation work and `qwen3.5:4b` for strategic task classes. If only one compatible model is installed, Bellwether uses that available model for the roles it can serve. If Ollama is unavailable, deterministic fallback keeps the game playable.

For a faster home computer that still has 8 GB RAM, pulling only `qwen3.5:4b` is a reasonable simple profile:

```bash
ollama pull qwen3.5:4b
./run.sh
```

Bellwether will detect and use it automatically. Advanced environment overrides remain supported for developers and benchmarking, but players do not need them. Context defaults to 4096 and thread count defaults to the logical CPUs visible to the operating system.

## v0.5.0 scope

- expands the authored core cast from Jonah, Mara, and Mrs Ellis to six residents;
- adds Asha Patel, Tom Mercer, and Ruth Calder with authored identities, needs, obligations, preferences, private tensions, and personal threads;
- expands the authored social web to all fifteen pairwise relationships among the six core residents;
- integrates the new residents into runtime NPC state, relationships, conversations, knowledge state, social simulation, schedules, and old-save migration;
- adds a durable structured event store with stable event IDs;
- adds per-NPC event references, private impressions, unresolved-memory slots, and salience-aware retrieval context;
- records player/NPC conversations into structured memory without turning generated prose into objective truth;
- supplies retrieved structured memory to free-form NPC conversation context;
- adds task-class model routing readiness with fast and deep model configuration;
- keeps all current synchronous gameplay tasks on the fast model;
- preserves deterministic fallback and the existing serialized foreground-priority inference gate.

## Design boundary

The memory substrate stores structured events and references. It does not treat generated prose as canon. NPC memories are bounded by witnessed or participated events, and private impressions remain distinct from objective world facts. The full Town Mind and procedural multi-day arc system remain later roadmap work.

## Diagnostics

Run the focused v0.5.0 diagnostic:

```bash
python3 tools/v050_core_cast_memory_diagnostic.py
```

Run the cumulative suite:

```bash
python3 tools/post_v010_diagnostic.py
```

For release-candidate certification with a live local model:

```bash
python3 tools/release_candidate_diagnostic.py
```

Use `--skip-qwen` only when certifying deterministic engineering layers without a running Ollama service.
