# Bellwether v0.1.0 — Part 18

Run:

```bash
./run.sh
```

## Qwen3 generation fix

Part 15 fixes the failure identified by Part 14 diagnostics.

Bounded Director choices previously used `num_predict: 12`. Qwen3 consumed that budget before emitting visible answer text, producing:

```text
done_reason: length
response: ""
```

Bounded choices now:
- prepend `/no_think`;
- start with a 96-token budget;
- use a lower temperature for stable option selection;
- detect empty output with `done_reason: length`;
- automatically increase the next attempt's token budget instead of repeating the same request.

Conversation generation remains separate and generative. It does not use the bounded-choice no-thinking profile.

## Candidate cleanup

Jonah is no longer offered `Return to bakery work` while already at the bakery. NPC candidate generation also removes semantically duplicate activity/destination pairs.

## Diagnostics

The Part 14 request tracing remains fully available in Village Mind so the new Qwen behavior can be verified directly.


## Part 23 daily life
Bellwether now offers location-specific ordinary activities. These consume in-world time, allowing the village simulation and Directors to continue while the player reads, gardens, tidies, eats, watches, walks, or runs errands. The resulting life state and activity history persist in saves.


## Release candidate diagnostic

For a comprehensive certification run, including real local-Qwen conversation continuity:

```bash
python3 tools/release_candidate_diagnostic.py
```

Paste the complete output and attach `rc_diagnostic_report.json` when requesting diagnosis. Use `--skip-qwen` only when testing the deterministic engineering layers without Ollama.

### v0.2.0 Part 15 development note
Run `python tools/post_v010_diagnostic.py` for cumulative Parts 1–15 checks. Part 15 adds lossy cross-run recurrence; see `docs/PART15_CROSS_RUN_MEMORY_AND_RECURRENCE.md`.

## v0.2.0 status

The 17-part v0.2.0 roadmap is complete. The release combines the frozen v0.1.0 narrative/simulation baseline with systemic ordinary life, economy, jobs, ecology, NPC autonomy, information flow, investigation, systemic horror, evolving identity, danger/death, recurrence, and integrated cooking/home-restoration content.

Run the cumulative post-v0.1.0 diagnostic with `python tools/post_v010_diagnostic.py`. For target-machine legacy certification including the local model, use `python tools/post_v010_diagnostic.py --include-release`.
