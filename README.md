# Bellwether v1.0.12

Bellwether is a local-first village life simulation and psychological horror RPG. The deterministic engine owns authoritative state; local LLMs make bounded proposals and player-like choices through legal public actions.

## Run

Install Ollama and pull the configured models, then run `./run.sh` and open the local address printed in the terminal.

## v1.0.12 corrective certification release

v1.0.12 corrects issues exposed by the v1.0.11 113-minute playtest. The diagnostic AI player now tracks LLM successes, timeouts, invalid responses, fallbacks and no-effect actions separately. Repeated ineffective actions are temporarily blocked until the plan/state changes, coverage goals bias candidate ranking toward relevant prerequisite chains, and the UI no longer displays misleading counters such as `AI 68/63`.

The full diagnostic now verifies that its advertised seven-day simulation actually reaches the required day span, reports a failure if it does not, and has a larger bounded action allowance. Natural horror pacing is not distorted for test coverage: ordinary play records natural exposure while a separate isolated certification checks authored anomaly application, overlay authority and expiry. Procedural content receives a separate controlled lifecycle certification covering start, public involvement and resolution.

Diagnostic state is checkpointed continuously and atomically to `diagnostics/latest_live_diagnostic.json` and `diagnostics/latest_live_diagnostic.txt`. If the browser closes, the server stops, or a long test is interrupted, the most recent trace, phase, counters and feed remain available for examination. The Developer Console restores the interrupted checkpoint summary on restart.

The Economy diagnostic cards now render the fictional Bellwether currency mark as markup instead of showing raw HTML. Live AI-player status distinguishes successful model choices from timeout/invalid fallbacks.

## Full diagnosis

Open the Developer Console and choose **Run Full Game Diagnosis**. This uses an isolated disposable world and does not replace the real save. It performs real specialist calls, a coverage-driven LLM playtest through public actions, climate/ecology checks, persistence checks, controlled procedural lifecycle certification and controlled horror-pipeline certification.

Progress is saved throughout the run. When complete, use **Copy Diagnostic Report** or **Export Report**. If interrupted, provide either checkpoint file from the `diagnostics/` directory.

## Autonomous play

Choose **Let the Village Play** to let the local LLM advance only ordinary, non-authored gameplay in the current run. The live display reports action count, successful LLM choices, timeouts and fallbacks. **Stop AI Player** is cooperative: an in-flight local inference may finish, but its result is discarded and no post-stop action is applied.

## Saving

Menu provides quick save/load and portable JSON export/import. A browser reload reconnects to the running server state. Use **Reset to Fresh Game** for a new run.

## Roadmap

After v1.0.12 certification stabilisation, the next major milestone remains **v1.1.0 — Economy and Village Change**: persistent business health, supply effects, prices, employment changes, business crises, player intervention and longer causal chains connecting weather, ecology, businesses, jobs, NPC routines and social consequences.
