# Bellwether v0.7.1 — NPC Cognition and Long-Term Memory

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

## v0.7.1 highlights

- Persistent per-NPC cognition state separate from objective world truth.
- Explicit distinction between fact, belief, rumour, impression, and suspicion.
- Confidence-bounded beliefs with source provenance.
- Belief reinforcement and revision history.
- Concerns, unresolved questions, short-term goals, and long-term ambitions.
- Witness-gated event interpretation: NPCs cannot remember events they did not witness or participate in.
- Salience/confidence-aware bounded retrieval for dialogue context.
- Daily fading of weak subjective beliefs while authoritative facts remain stable.
- Asymmetric cognition: different NPCs may interpret or remember the same event differently.
- Conversation events feed cognition only through structured witnessed events; generated prose does not become canon.
- Town Mind intentions remain strategic context only and cannot dictate NPC beliefs.
- Safe migration for older saves.

## AI authority boundary

The authority chain remains:

**LLM proposes → parser/validator checks → deterministic engine applies → persistence stores**

NPC beliefs are subjective state. A belief, rumour, impression, or suspicion never becomes objective world truth merely because an NPC or model says it. Canonical facts remain controlled by authored content and deterministic game systems.

## Conversation style

Free NPC dialogue is intentionally concise for both tone and low-end hardware. NPCs are asked for one short natural sentence, normally 4–18 words, with a hard 24-word display/storage ceiling. Recent conversation is compacted, near-verbatim repetition is detected, and ordinary greetings or weather small talk cannot create implausibly large relationship gains.

## Diagnostics

Focused v0.7.1 diagnostic:

```bash
PYTHONPATH=. python3 tools/v071_npc_cognition_diagnostic.py
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

- **v0.7.1** — NPC cognition, subjective beliefs, concerns, goals, ambitions, revision and bounded retrieval.
- **v0.7.0** — Town Mind strategic intention architecture and deep-model routing.
- **v0.6.1** — journey depth, route familiarity, weather-sensitive travel, short dialogue, repetition guards, and automatic CPU-thread use.
- **v0.6.0** — world expansion to fourteen authored locations.
- **v0.5.2** — structured social consequences, commitments, grievances, and relationship stages.
- **v0.5.1** — 24 persistent lightweight residents and tiered background simulation.
- **v0.5.0** — six-person core cast, durable memory substrate, and local Ollama auto-detection.

See `CHANGELOG.md`, the roadmap, handoff guide, and version audit reports in `docs/` for full development context.
