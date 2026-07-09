# Bellwether v1.0 RC2

Bellwether is a text-first village life-sim, RPG, mystery, and psychological horror game. You can work, garden, cook, explore, investigate, build relationships, and follow the main story at your own pace. The village continues to change around you.

## Quick start

Bellwether runs on Debian/Linux and uses a local Ollama model when one is available.

Install Ollama, then pull these models once:

```bash
ollama pull qwen3.5:2b
ollama pull qwen3.5:4b
```

Start the game:

```bash
./run.sh
```

Open the local address printed in the terminal.

You do not need to set model names or CPU thread counts. Bellwether detects the installed models and the CPU threads available to the process.

## Which model does what?

- `qwen3.5:2b` handles short player-facing dialogue and routine AI work.
- `qwen3.5:4b` handles slower strategic work such as Town Mind reviews and procedural social arcs.
- If only one supported model is installed, Bellwether uses that model where possible.
- If Ollama is unavailable, deterministic fallbacks keep the game playable.

On low-memory systems, Bellwether runs one Ollama inference at a time. Each inference can use all CPU threads available to the process. Background AI jobs are queued so ordinary gameplay does not wait for routine Director decisions.

## Performance behaviour

Most gameplay systems are deterministic and should remain responsive while background AI is thinking. Free-form NPC conversation is the main action that still waits for a model response because the reply is needed immediately.

The AI system uses:

- one background inference worker;
- foreground dialogue priority;
- asynchronous routine Directors;
- asynchronous Town Mind reviews;
- asynchronous procedural-arc planning;
- compact task-specific prompts;
- cached overview context;
- bounded output lengths;
- deterministic fallbacks;
- validation before AI results change game state.

The Developer Console shows AI queue state, recent traces, prompt size, latency, and Ollama timing fields.

## RC2: ending families

RC2 adds the six canonical ending families:

- Incorporation
- False Escape
- Rupture
- Accommodation
- Containment
- True Liberation-Coexistence

Endings are not chosen from a universal final menu. The game only offers endings that your play has made possible. Eligibility can depend on investigation, relationships, recurrence, anchors, familiarity with the village, preparation, and the way you have lived in Bellwether.

The LLM cannot create, unlock, or resolve an ending. Ending eligibility is controlled by deterministic game state.

## Important game systems

The current build includes ordinary village life, jobs and economy, gardening and cooking, hobbies and skills, a persistent population, core NPC relationships and memory, NPC cognition, procedural social arcs, expanded exploration, travel depth, mystery investigation, adaptive horror, horror aftermath, Interface Horror, recurrence, failure and recovery, Town Mind strategy, and the complete authored story path through ending resolution.

## Developer / Settings

The Developer / Settings control is intentionally part of the game. It is used for debugging and inspection and must not be removed from release builds without an explicit project decision.

The console can inspect simulation state, AI traces, background jobs, Town Mind state, horror systems, recurrence, story progress, and ending eligibility.

## Save compatibility

The game migrates older saves forward. Keep a backup of important saves when testing release candidates.

## Diagnostics

Release diagnostics are in `tools/` and audit reports are in `docs/`. RC2 must preserve the behaviour of accepted earlier releases while adding ending families and performance work.

## Roadmap

- **v1.0 RC2 — Ending Families:** current release.
- **v1.0 RC3 — Postgame:** farming, jobs, relationships, hobbies, side mysteries, and changed village state after resolution.
- **v1.0 — Certification:** audio, accessibility, performance, distribution, full playtesting, and release certification.
