# Bellwether v3.0.0-rc11 audit

## Scope and evidence
RC11 inspected the foreground free-form dialogue path in `backend/ai/provider.py` and `backend/core/game.py` before editing. The prior contract forced one short sentence and 48 generated tokens. It had strong safety and continuity context, but the response grammar encouraged terse, generic replies and weak answers to questions, advice requests, disclosures, and follow-up turns.

## Changes
The foreground prompt now explicitly distinguishes questions, advice requests, disclosures, and small talk; requires direct answering; uses recent turns as conversational continuity; allows 1-3 short sentences; permits but does not require one relevant follow-up question; asks characters to express voice through priorities and rhythm; and treats NPC knowledge as a ceiling with explicit uncertainty allowed. Generation budget increased to 96 tokens and stored/displayed replies remain bounded to three sentences and 60 words. Story authority restrictions are unchanged.

RC11 also adds an accelerated 120-day baseline economy certification. It checks positive prices, bounded business health/reserves, bounded produce demand, and bounded history/ledger growth. This is deterministic balance evidence, not a claim that every active player strategy has been economically optimized.

## Verification boundary
No live Ollama model is available in this build environment, so semantic dialogue quality remains a runtime evidence requirement. Structural prompt, parser, bounds, authority, and deterministic economy contracts are certified here.
