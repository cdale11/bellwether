# Bellwether v1.0 RC3

Bellwether is a text-first village life-sim, RPG, mystery and psychological horror game. You can live in the village at your own pace: work, garden, cook, explore, build relationships, investigate mysteries, or follow the main story.

RC3 adds postgame life. Reaching an ending no longer means the simulation stops. The village changes according to the ending, and you can continue farming, working, socialising, following hobbies and investigating remaining side mysteries.

## Start the game

Bellwether is designed for Debian/Linux and uses Ollama locally.

Install the two recommended models once:

```bash
ollama pull qwen3.5:2b
ollama pull qwen3.5:4b
```

Then run:

```bash
./run.sh
```

Open the local address shown in the terminal.

Bellwether detects available CPU threads automatically. You do not need to set thread counts or model names.

## How AI is used

The deterministic engine owns the real game state. The LLM proposes bounded choices; validators decide whether they are legal.

The 2B model handles short dialogue and routine village decisions. The 4B model handles slower strategic work such as Town Mind reviews and procedural social arcs.

Routine AI work runs in a background queue. Walking, gardening, jobs, hobbies and other normal actions do not wait for it. Free-form NPC conversation still waits because the reply is needed immediately.

Only one Ollama inference runs at a time on low-memory systems. This avoids making the 2B and 4B models fight for RAM and CPU. Each inference can use all CPU threads available to Bellwether.

## AI debugging

The Developer / Settings button is intentionally part of the game.

The Developer Console shows:

- queued AI jobs;
- the currently running job;
- completed jobs waiting for validation;
- recent queue, start, finish, failure, harvest and apply events;
- job age and running time;
- accepted, rejected, stale and failed results;
- Ollama traces and timing information.

Completed background results are harvested automatically. They do not have to wait for another player action before validation and application.

## RC3 postgame

After one of the six canonical endings, Bellwether remains playable. Existing farming, jobs, relationships, hobbies and exploration systems stay available.

The postgame also records continued village life and applies an ending-specific village condition. Remaining loose ends can be investigated without reopening the resolved central crisis.

The six ending families are:

- Incorporation
- False Escape
- Rupture
- Accommodation
- Containment
- True Liberation-Coexistence

## Save compatibility

Older saves are migrated forward. Keep backups of important saves while testing release candidates.

## Project files

Diagnostics are in `tools/`. Audit reports and the design documents are in `docs/`.

## Roadmap

- **v1.0 RC3 — Postgame:** current release.
- **v1.0 — Certification:** audio, accessibility, performance, distribution, full playtesting and release certification.
