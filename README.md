# Bellwether v0.6.1 — Travel and Journey Depth

Bellwether v0.5.2 deepens the six-person core cast with persistent structured social consequences, grievances, commitments, shared history, relationship stages, and auditable gossip propagation. It is an additive upgrade from v0.5.1 and preserves the 24-resident lightweight population tier and integrated local Ollama model detection.


## v0.6.1 — Travel and Journey Depth

Travel is now a persistent simulation system rather than a fixed location switch. Routes remember journey count and familiarity, first journeys produce route observations, weather and route condition alter travel time, repeated use modestly improves journey efficiency, and occasional bounded journey encounters can surface NPC movement, ecology, or weather texture. Journey history is saved and migrated safely.

### Ollama CPU usage

Bellwether now automatically sends Ollama the full number of CPU threads available to the game process. On Linux it uses the process CPU-affinity set, so a normal unrestricted launch uses every logical CPU thread (4 on the i3-4160), while containers or deliberately pinned processes respect their allowed CPU set. No environment-variable fiddling is required. `BELLWETHER_AI_THREADS` remains an optional developer override.

Normal setup remains: pull the recommended models once, then run `./run.sh`.


## v0.6.0 — World Expansion

This release expands Bellwether from nine locations to fourteen with Field Lane, Calder Farm, Bellwether Woods, the Old Quarry, and the Quarry Caves. The new region is connected to the existing travel graph, parchment exploration map, hobbies, investigation tags, ecology hooks, danger system, NPC adjacency and old-save migration. New places contain ordinary-life actions and hobby opportunities rather than functioning as empty travel nodes. Existing local Ollama auto-detection is unchanged.

Run the focused diagnostic with:

```bash
PYTHONPATH=. python tools/v060_world_expansion_diagnostic.py
```

## v0.5.2 — Relationship Depth and Social Consequences

This release adds a persistent structured social-consequence layer on top of the existing relationship and memory systems. Explicit promises, invitations, requests, apologies, insults, agreements, and refusals can now become validated social acts. Ordinary conversation is deliberately not mechanized. Core-NPC dialogue context receives unresolved commitments, grievances, favour state, and shared history, allowing local Ollama models to respond to specific past interactions instead of only numeric relationship scores.

Apologies can resolve existing grievances; direct insults create persistent grievances and bounded trust/affinity consequences; explicit commitments are stored as open social obligations. NPC-to-NPC catalogue-backed information propagation is now mirrored into an auditable gossip log while retaining the existing knowledge-boundary rules. Relationship context also exposes a derived stage (`new`, `acquainted`, `friendly`, `close`, `strained`, or `hostile`) without replacing the underlying multidimensional values. Old saves migrate additively.


## v0.5.1 scope

- 24 persistent lightweight background residents with strict validated schemas.
- Stable households, occupations, traits, interests, routine archetypes, and identities.
- Hourly batched simulation rather than per-resident LLM calls.
- Work, commute, school, errands, community activity, and evening movement schedules.
- Cheap persistent social-link formation from repeated co-location.
- Lightweight residents appear in the location presence UI without entering core-NPC dialogue/cognition loops.
- Old-save migration creates the population safely without replacing existing state.
- Existing integrated Ollama auto-detection remains unchanged: pull the recommended models once, then run `./run.sh`.

Run the focused diagnostic with:

```bash
PYTHONPATH=. python tools/v052_relationship_depth_diagnostic.py
```


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

## v0.6.1 conversation reliability update

Free-form NPC dialogue is intentionally concise on low-end local hardware. NPCs are instructed to answer in one short natural sentence, normally 4–18 words, and the engine enforces a hard 24-word display/storage ceiling. Conversation generation uses a reduced 48-token budget.

Recent conversation context is compacted before it is sent to Ollama instead of injecting the same full NPC reply repeatedly. The provider detects near-verbatim reply loops and can perform one bounded corrective retry. Ordinary greetings and brief weather small talk are engine-clamped so they cannot create implausible trust or major familiarity gains.

The normal Ollama workflow remains unchanged: pull the recommended models once, then run `./run.sh`. Bellwether automatically uses all CPU threads available to the process and routes local Ollama calls internally.

## v0.7.0 Town Mind architecture

Bellwether now includes the first strategic Town Mind layer. It performs an opening strategic review and infrequent periodic reviews, using the locally installed deep Ollama model when available. On the recommended low-end profile, routine and foreground tasks use `qwen3.5:2b`, while Town Mind reviews route to `qwen3.5:4b` automatically. No environment variables are required.

Town Mind cannot directly change weather, move NPCs, create facts, alter quests, or mutate resources. It chooses only from a validated catalogue of strategic intentions. Accepted intentions are persistent, expire or are revised, and are supplied as context to specialist systems. The authority chain remains: Town Mind proposes direction; specialist systems make bounded proposals; validators enforce legality; the deterministic engine applies accepted changes.
