# Bellwether v3.0.0-rc10 Audit

## Scope
Evidence-first audit of the reported missing Sleep action and the local-LLM foreground dialogue runtime contracts.

## Sleep defect
The authoritative `Game.actions()` implementation correctly emitted `sleep` at Ashcroft Cottage after Eleanor's letter was read, and the action handler correctly advanced the day. The defect was in shared progressive disclosure: `compact()` caps each category at eight actions and sorted ordinary-life actions alphabetically. As Home & Life content expanded, Sleep could be displaced beyond the cap. The fix is surgical: Sleep is priority-preserved inside its existing category; no location, story gate, or sleep semantics changed.

## LLM runtime audit
Foreground dialogue retains configurable timeout, bounded retry, repetition detection and repair, obvious daypart contradiction detection, hard reply length bounding, and explicit prompt authority prohibitions against invented plot facts and off-screen events. This release adds deterministic certification of those contracts. It does not claim semantic quality from a live Ollama campaign because no local Ollama runtime was available in this build environment.

## Cleanup
Removed Python caches, bytecode, stale live diagnostic reports and JSONL traces before packaging. Historical source diagnostics and audits were retained as regression provenance.
