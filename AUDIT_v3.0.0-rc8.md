# Bellwether v3.0.0-rc8 Audit — Integrated Interaction and Quest Lifecycle

## Method
Inspected the current RC7 action construction, presence-panel lookup contract, side-quest completion calls, quest reward model, procedural arc involvement/resolution lifecycle, public view projection, and frontend side-story/journal rendering before editing.

## Findings
1. The Mara-specific authored talk metadata defect fixed in RC7 did not remain in authored/free-talk paths.
2. Social greeting actions were still missing `npc_id`/`npc_name`, so the presence panel could omit a valid social interaction even though the action tray exposed it. Fixed at the shared action construction point.
3. Authored side quests were correctly marked `done=True`, `status=completed`, and reward-protected exactly once by `QuestModel.complete`. The compact side-story UI filtered all completed quests out, creating the impression that completion was not recorded. The journal could show them, but the compact surface could not.
4. Procedural arcs had a real presentation ambiguity: after the player offered help, the public quest projection still described the arc as simply active with `done=False` until its time-driven final stage. The underlying lifecycle was valid, but no explicit in-progress state was exposed. RC8 now marks player-involved arcs `in_progress`, explains that village time must pass, and projects resolved player-involved arcs as completed with completion status and reward evidence.
5. Procedural rewards were already applied on final-stage resolution through the exactly-once quest transaction layer; this behavior was preserved and certified.

## Verification
- RC8 interaction and quest lifecycle certification: 13/13 PASS.
- RC7 Mara interaction regression: 9/9 PASS.
- RC5 UI/UX regression: 10/10 PASS.
- Complete story diagnostic: 13/13 PASS.
- Python compilation: PASS.
- JavaScript syntax: PASS.
- ZIP integrity: PASS.

## Boundaries
No long autonomous campaign or interactive browser/device session was run. RC8 certifies deterministic lifecycle and source/runtime interaction contracts, not subjective pacing of every procedural arc.
