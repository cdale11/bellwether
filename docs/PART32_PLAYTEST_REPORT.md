# Part 32 Player-Perspective Playtest Report

## Method
The automated agents choose only from player-visible `Game.view()` information: prose, visible quests, current location, present actors, and offered actions. Hidden flags, branch thresholds, horror eligibility, and source code are not consulted when choosing actions.

Baseline: 12 runs across six play styles, up to 320 actions each. Full sequential transcripts are stored in `docs/part32_transcripts/`.

## Full-loop result
Both balanced-reader runs reached authored anomalies and completed the game:
- completion steps: 218 and 254
- first anomaly steps: 197 and 194
- locations visited: 8 and 9
- evidence collected: 9 and 15

This confirms end-to-end reachability without hidden-state steering.

## Important findings
Extreme single-system profiles do not accidentally advance the horror or endgame. Story-only travellers, pure life-sim repetition, pure investigation at one place, and cautious travel-only runs remain incomplete. This is intentional evidence that horror still requires learned normality across ordinary life rather than elapsed time alone.

The first baseline exposed brittle familiarity thresholds for varied players. Part 32 lowers learned-place horror eligibility from 8 to 6 familiarity and endgame familiar-place qualification from 10 to 8. Horror remains gated behind reading Eleanor's letter, at least eight ordinary life activities, and familiarity with at least two places.

Direct NPC conversation now explicitly receives the evolving compact player-style summary and the last three notable player choices, while retaining the dedicated low-latency foreground prompt path.

## Limits
These automated runs validate sequence, reachability, pacing structure, and visible-choice behavior. They do not replace manual prose-quality reading with real Qwen output. The next release phase should include real-model transcript review on the target i3-4160 machine and manual player-perspective narrative passes.
