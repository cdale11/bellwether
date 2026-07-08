# Part 34 — Manual Narrative Rebuild and Pacing Polish

## Focus
Part 34 responds directly to the real Part 33 Mrs Ellis trace. The social pipeline was functioning, but immediate conversational continuity and long-term memory selection were not yet strong enough for a 1.7B local model.

## Conversation continuity rebuild
Free-text conversation now has two distinct memory layers:

1. `conversation_sessions`: exact recent player/NPC exchange pairs for short-term continuity.
2. `social_memory`: selective compressed memories intended to survive as meaningful relationship history.

The next Qwen call receives up to three exact recent exchanges. The prompt explicitly treats close turns as a continuous conversation and tells the NPC not to restart with a greeting, contradict recent chronology, or claim a long absence after a conversation minutes earlier.

This fixes the failure pattern seen in the trace:
- greeting
- "Do you not remember me?"
- NPC claims "It's been a while"
- advice request
- "Perfect!"
- NPC forgets the advice and starts a new greeting

## Memory consolidation
Acknowledgements such as `okay`, `perfect`, `right`, `yes`, `thanks`, and `great` no longer become long-term memories merely because Qwen emits a memory sentence. Exact turns remain available in the short-term session buffer.

Long-term social memory is kept when an interaction has meaningful affinity/trust effect, sufficient conversational substance, or unusually high familiarity significance. Near-duplicate recent memories are suppressed.

This prevents three paraphrases of the same greeting from crowding out more useful memories.

## Social calibration
The prompt now tells Qwen that brief acknowledgements normally deserve familiarity 0 or 1, not 2. Familiarity 2 is reserved for genuinely significant disclosure or substantial interaction.

## Grounded advice
When the player asks what to do next, the NPC is instructed to answer from current location, activity, and visible story context. Ambient NPCs must not invent invitations, shared plans, objects, or off-screen events.

## Authored prose pass
The opening arrival prose, Jonah's first-meeting lines, and Mara's introduction/repeat line were manually tightened. The goal was quieter specificity and clearer character distinction without increasing exposition.

## Regression findings
- Structural simulation: 7/7 profiles passed across 840 actions.
- Known full-loop balanced-reader seed remains reachable: first anomaly at action 46 and ending completion at action 122.
- A separate balanced seed did not reach anomaly escalation within 360 actions. This remains useful evidence that stochastic route/action distribution can materially change pacing and should be examined further during release-candidate certification rather than hidden by lowering gates again.

## Target-machine QA recommendation
Repeat the exact Mrs Ellis sequence from the Part 33 trace:
1. `Hi! Mrs Ellis`
2. `Do you not remember me?`
3. `Any ideas what I should do next?`
4. `Perfect!`

Expected qualitative behavior:
- turn 2 acknowledges the immediately recent greeting;
- turn 3 gives grounded advice rather than inventing a tea plan;
- turn 4 responds to the advice context rather than restarting the morning;
- `Perfect!` should not receive familiarity +2;
- long-term memory should not fill with repeated greeting paraphrases.
