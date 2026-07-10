# Bellwether v3.5.0 evidence ledger

Pre-edit inspection confirmed v3.4.1 had a validated interpretation substrate, but only `town_mind` was scheduled for review. The declared observer set contained Town Mind, Chorus, and village only; core NPCs did not have independent theory spaces. The shared evidence packet exposed the same recent authoritative event window to every observer.

v3.5.0 adds observer-specific evidence access and theory spaces for Mara, Jonah, Mrs Ellis, village social interpretation, Town Mind, and Chorus. NPC evidence is limited to durable memory references; village interpretation uses public/socially observable events; Chorus receives anomaly/horror/recurrence-adjacent evidence; Town Mind retains broad strategic access. Review outputs are validated against each observer's own visible evidence set, preventing an LLM from grounding a private NPC belief in an event that NPC could not know.

To remain viable on the target low-end local CPU, sleep queues Town Mind plus one rotating additional observer rather than six simultaneous reviews. The architecture remains asynchronous and non-authoritative.

No claim is made that live semantic interpretation quality is certified without the user's local Ollama runtime. Deterministic access boundaries, validation, scheduling, compilation, and package integrity are tested.
