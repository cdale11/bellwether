# Bellwether v0.5.0 — Complete Core Cast and Memory Foundation

Bellwether v0.5.0 expands the deeply simulated authored cast from three to six core residents and introduces the first durable structured memory substrate required for later relationship depth, procedural social arcs, and the Town Mind. It is an additive upgrade from v0.4.2.

## Run

```bash
./run.sh
```

Bellwether uses local Ollama models when available and retains deterministic fallback behaviour when AI is unavailable.

## Required local models for the recommended low-end profile

For the current target machine (Intel i3-4160, 8 GB RAM, 4 GB zram), install these two models:

```bash
ollama pull qwen3.5:2b
ollama pull qwen3.5:4b
```

The 2B model is the foreground/default model for dialogue, bounded Directors, NPC choices, weather, traffic, memory-adjacent work, and ordinary simulation calls. The 4B model is the optional strategic model reserved by the routing layer for future Town Mind, procedural-arc, recurrence-strategy, and horror-strategy task classes. v0.5.0 is routing-ready, but does not yet run the future Town Mind loop.

Recommended low-end environment:

```bash
export BELLWETHER_AI_FAST_MODEL=qwen3.5:2b
export BELLWETHER_AI_DEEP_MODEL=qwen3.5:4b
export BELLWETHER_AI_THREADS=4
export BELLWETHER_AI_NUM_CTX=4096
export OLLAMA_NUM_PARALLEL=1
./run.sh
```

Do not increase context merely because a model advertises a very large maximum. Bellwether deliberately uses compact context routing and structured memory retrieval. On an 8 GB CPU system, 4096 is the recommended starting point.

## Installing Ollama on headless Debian

If Ollama is not installed:

```bash
curl -fsSL https://ollama.com/install.sh | sh
sudo systemctl enable --now ollama
ollama pull qwen3.5:2b
ollama pull qwen3.5:4b
ollama list
```

If the service needs explicit low-end settings, create a systemd override:

```bash
sudo systemctl edit ollama
```

Add:

```ini
[Service]
Environment="OLLAMA_NUM_PARALLEL=1"
Environment="OLLAMA_MAX_LOADED_MODELS=1"
```

Then apply it:

```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

`OLLAMA_MAX_LOADED_MODELS=1` is recommended on the 8 GB low-end machine so the future strategic model does not compete in RAM with the foreground model. Model switching is slower, but safer.

## Better 8 GB home computer profile

For a materially faster CPU with 8 GB RAM, the safe default is still:

```bash
ollama pull qwen3.5:4b
```

Run the 4B model as the foreground and strategic model:

```bash
export BELLWETHER_AI_FAST_MODEL=qwen3.5:4b
export BELLWETHER_AI_DEEP_MODEL=qwen3.5:4b
export BELLWETHER_AI_NUM_CTX=4096
./run.sh
```

A larger strategic model should only be introduced after benchmarking actual RAM pressure and latency. Bellwether must remain playable with one small local model and deterministic fallback.

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
