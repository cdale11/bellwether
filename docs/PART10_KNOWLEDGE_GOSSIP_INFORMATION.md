# Part 10 — Knowledge, Gossip and Information Propagation

Part 10 adds a bounded knowledge layer. Authored facts and permitted distortion variants live in immutable catalogue data; NPC beliefs, confidence, provenance, hearsay variants, transmission logs, and propagation history are save-persistent runtime state.

Fresh autonomous social encounters can transmit at most one eligible fact in each direction. Trust and tension constrain disclosure, sensitive facts can be withheld, and distortion can only select an authored bounded variant. Unknown fact IDs are rejected, preventing LLM or Director output from becoming canon by accident.

The existing Part 3 shared-topic hook is now fed by actual propagation. Dialogue and later behaviour systems can query resolved NPC knowledge context while authoritative truth remains separate from belief.
