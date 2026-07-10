# Bellwether v3.14.0 audit

Evidence-first inspection found v3.13.0 retained only the isolated overnight diagnostic entry point. This removed the distinct live autonomous-play behavior the project requires. v3.14.0 keeps both modes: isolated seven-day QA on a clone and intentional live village play on the authoritative Game object under the normal game lock. The UI warns before starting live mutation.

Provider inspection confirmed discovery order is qwen3.5:4b then qwen3.5:2b, with deep_model defaulting to fast_model. Thus absence of 4B falls back to 2B without loading both automatically.
