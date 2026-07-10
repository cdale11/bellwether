# Bellwether v3.0.0-rc3 Audit — NPC Characterization and Dialogue Continuity

## Evidence-first audit
Inspected `core_cast.json`, `npc_model.py`, foreground conversation path in `game.py`, provider prompt/parser/repetition repair, memory and cognition models, social consequences, NPC social web and knowledge contexts, autonomous-life state, and ambient NPC conversation director.

## Confirmed gap
The foreground conversation path already supplied personality, relationship, structured memory, cognition, social consequences, recent turns, life needs, player style and story bounds. However, it did not supply NPC social-web context or bounded knowledge context, and autonomous-life events/goals were not translated into a compact expressive context. Ambient NPC-to-NPC dialogue also lacked authored identity/voice context, encouraging generic interchangeable exchanges.

## Changes
Added a presentation-only `dialogue_expression_model.py` with distinct authored voice constraints for Jonah, Mara and Mrs Ellis. It derives bounded current-goal, dominant-need and recent autonomous-life context without mutating canon. Foreground dialogue now receives expression, social-web and knowledge context. Provider instructions require recognizable voice without caricature, catchphrase repetition or forced biography. Ambient NPC conversation now receives both participants' authored identity and expression context.

## Authority boundary
No LLM path can mutate story truth, knowledge catalogue, relationship canon, autonomous-life state, or authored identity through this model. Generated dialogue remains expressive output; state mutations continue through existing bounded parsers and deterministic systems.

## Verification
- RC3 dialogue-expression certification: 12/12 PASS
- Conversation reliability diagnostic: 9/9 PASS
- NPC cognition diagnostic: 12/12 PASS
- NPC Lives regression: 10/10 PASS
- Python compilation: PASS
- JSON parsing: PASS
- ZIP integrity: PASS

No long Ollama semantic-quality campaign or browser-level interaction session was run in this environment.
