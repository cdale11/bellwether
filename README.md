# Bellwether v0.9.0 — Recurrence Expansion

Bellwether is a text-first village life-sim, RPG, mystery, and psychological/supernatural horror game. v0.9.0 expands recurrence with progressive fragmented memory return, asymmetric NPC echoes, cross-run anchoring, story residues, danger instincts, and context-sensitive awakening locations while keeping mutable village state reset and authoritative.

Bellwether is a text-first village life-sim, RPG, mystery, and psychological/supernatural horror game. v0.8.4 adds bounded, state-driven presentation contradictions while preserving authoritative game state. Map contradictions, subtle text displacement/repetition, portrait tonal shifts, journal inconsistencies, and theme mismatches are derived only from active validated anomaly overlays. Developer / Settings access remains directly available for inspection of true state and presentation effects.

Bellwether is a persistent village life-sim/RPG and psychological-supernatural horror game. The deterministic engine owns truth and legality; local LLMs provide bounded dialogue, Director choices, and strategic proposals that are validated before application.


## v0.8.3 — Horror Consequence and Recovery Depth

Experienced anomalies now leave bounded, persistent aftermath. Core NPCs only react as witnesses when authoritative location state says they were present; witnessed anomalies enter structured memory and cognition without becoming new objective facts. NPCs can carry temporary strain and short-lived place avoidance into routine selection. The player gains a persistent strain/recovery layer, and ordinary activities such as tea, cottage care, gardening, walking and nature-based hobbies can support bounded recovery and reduce unease. Recovery is gradual, causal, inspectable in the Developer Console, and never erases story progress or anomaly history.

Focused diagnostic:

```bash
python tools/v083_horror_aftermath_diagnostic.py
```

## v0.8.2 — Adaptive Horror

Horror now adapts its **selection and pacing**, never its canon. The engine derives a bounded horror profile from authoritative player behaviour and coping patterns, then prioritizes only already-authored, already-eligible anomaly domains. Socially oriented play can make memory and information contradictions more salient; investigative play can emphasize records, routes, and spatial inconsistency; routine-heavy play can make learned rhythms and familiar spaces more vulnerable.

Adaptive horror includes mandatory quiet/recovery windows, anti-spam suppression, domain-diversity pressure, persistent selection logs, old-save migration, and Developer Console visibility. The system cannot invent anomalies, bypass eligibility, alter money or inventory, reveal hidden truth, or directly mutate relationships, quests, evidence, or NPC knowledge.

Focused diagnostic:

```bash
python tools/v082_adaptive_horror_diagnostic.py
```

## v0.8.1 — Regression Integrity Release

This release restores the intentional Developer / Settings access button, preserves the complete v0.8.0 mystery expansion, packages the authoritative project context text files, and adds explicit regression-integrity diagnostics. No accepted gameplay system is intentionally removed or simplified.

Focused v0.8.1 diagnostic:

```bash
python tools/v081_regression_integrity_diagnostic.py
```


## v0.8.0 — Full Mystery Expansion

Bellwether now contains seven interconnected investigation threads spanning village routines, Eleanor's patterns, the railway halt, disputed land boundaries, contradictory records, returning routes, and synchronised ecological behaviour. Investigation remains optional and player-driven. Evidence is gathered from authored places and testimony, hypotheses require multiple independent supports, testimony remains distinct from truth, and cross-mystery connections emerge only from accumulated evidence. The notebook now exposes active mystery threads without revealing hidden canon.

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

## v0.8.0 highlights

- Seven interconnected mystery threads, expanded from the original three.
- Evidence links across geography, Eleanor's habits, institutional records, route behaviour, village routines, and ecology.
- Seven multi-source hypotheses with tentative and supported states.
- Persistent mystery progress states: unopened, active, and deepening.
- Cross-thread connections emerge only when related mysteries have actually been activated by evidence or testimony.
- New bounded testimony facts concerning disputed boundaries, a missing woodland route, and synchronised animal behaviour.
- Investigation Notebook now shows active mystery threads without exposing hidden canon.
- Developer diagnostics now separate notebook state from the richer mystery graph.
- Existing Town Mind, cognition, procedural arcs, concise dialogue, travel, life-sim, social, economy, horror, and recurrence systems remain intact.

## AI authority boundary

The authority chain remains:

**LLM proposes → parser/validator checks → deterministic engine applies → persistence stores**

NPC beliefs are subjective state. A belief, rumour, impression, or suspicion never becomes objective world truth merely because an NPC or model says it. Canonical facts remain controlled by authored content and deterministic game systems.

## Conversation style

Free NPC dialogue is intentionally concise for both tone and low-end hardware. NPCs are asked for one short natural sentence, normally 4–18 words, with a hard 24-word display/storage ceiling. Recent conversation is compacted, near-verbatim repetition is detected, and ordinary greetings or weather small talk cannot create implausibly large relationship gains.

## Diagnostics

Focused v0.8.0 diagnostic:

```bash
PYTHONPATH=. python3 tools/v080_full_mystery_expansion_diagnostic.py
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

- **v0.8.0** — seven interconnected mystery threads, multi-source hypotheses, cross-thread connections, and expanded testimony.
- **v0.7.2** — persistent validated multi-day procedural social arcs and causal stage progression.

- **v0.7.1** — NPC cognition, subjective beliefs, concerns, goals, ambitions, revision and bounded retrieval.
- **v0.7.0** — Town Mind strategic intention architecture and deep-model routing.
- **v0.6.1** — journey depth, route familiarity, weather-sensitive travel, short dialogue, repetition guards, and automatic CPU-thread use.
- **v0.6.0** — world expansion to fourteen authored locations.
- **v0.5.2** — structured social consequences, commitments, grievances, and relationship stages.
- **v0.5.1** — 24 persistent lightweight residents and tiered background simulation.
- **v0.5.0** — six-person core cast, durable memory substrate, and local Ollama auto-detection.

See `CHANGELOG.md`, the roadmap, handoff guide, and version audit reports in `docs/` for full development context.