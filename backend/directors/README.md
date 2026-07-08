# Director Framework

The first executable Director contract is now present.

Current:
- `base.py`: common Director interface.
- `weather.py`: bounded weather state schema and fallback.

Planned:
- World Director / Village Brain
- NPC Director
- Conversation Director
- Traffic Director
- Garden Director
- Wildlife Director
- Economy Director
- Dream Director
- Supernatural Director

Design rule:
1. Director builds minimal context.
2. AI provider proposes a small structured state change.
3. Director validates the proposal.
4. Engine applies the accepted state.

The schemas are deliberately bounded so ordinary model responses can be accepted
with minimal rejection and safe fallback when malformed.
