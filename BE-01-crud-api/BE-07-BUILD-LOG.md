# BE-07 Build Log

This log records implementation events as they happen. It is not a retrospective summary.

## 2026-11-16 — Stage 0: job and provider setup

- Chose a source-grounded book-enrichment endpoint because the existing scraper already emits validated titles and descriptions.
- Wrote the output contract before making model calls: fixed category enum, one-sentence summary, and two fixed quality flags.
- Selected the OpenRouter free route. The local environment has no `LLM_API_KEY`; therefore the live provider checkpoint is pending. No key was added to the repository.
- Added a provider smoke-check script and the OpenRouter variable names to `.env.example`. The script exits with a clear setup message when the key is absent.
- Next: finish the endpoint in stub mode, then request one live call for the model checkpoint and eval.
- Iteration: installed the declared SDK in the project virtualenv and ran `scripts/check_llm_provider.py`. It exited with code 2 and listed the three missing `LLM_*` settings, as intended. The repo `.env` is ignored and untracked; no credential was printed or committed.

## 2026-11-16 — Stage 1: endpoint contract and stub

- Added `POST /enrich` to the existing layered FastAPI app. Input and output use strict Pydantic models; unknown fields and out-of-range values are rejected.
- Kept the HTTP route thin and routed the first implementation through a deterministic stub. No provider calls occur in this stage.
- The existing app returns 422 for framework request validation by default. Added a path-scoped handler so `/enrich` follows the assignment's 400-with-field requirement while other routes keep FastAPI's normal 422 behavior.
- Added contract tests for the schema, stub response, and field-specific validation errors. Test execution is pending the test dependencies and local database isolation check.
- Iteration: the console-script form `./.venv/bin/pytest` failed collection with `ModuleNotFoundError: src` because it did not put the API directory on the import path. Switched to the documented module form `./.venv/bin/python -m pytest`; 10 endpoint/schema checks passed. Tests force the API onto a temporary SQLite database so they do not depend on the stopped PostgreSQL container.
- Added an explicit 503 response for non-stub requests during this stage rather than allowing an unhandled exception. Stage 2 will replace this temporary path with the real client.

## 2026-11-16 — Stage 2: versioned prompt and live client

- Added `prompts/enrich-v1.md` with the role, exact schema, category meanings, uncertainty rule, and examples, including an instruction-like description.
- Added the OpenRouter-compatible client and kept the scraped fields in a JSON-encoded user message, separate from the system prompt.
- The endpoint now parses and validates JSON before returning it. This is a deliberate safety improvement over the PDF's temporary raw-text checkpoint; invalid output is not exposed while repair/quarantine are added next.
- Added Compose environment mapping for the provider settings so the app container can receive values from the local `.env` without copying `.env` into the image.
- Live-call checkpoint is still pending: no key exists in the local `.env`. Provider behavior is covered with a mocked response until the secret is configured.
- Iteration: a first invalid-output test showed Pydantic included the invalid value in its validation error, which would have leaked the model text to the caller. Diagnostics now omit input values; only the private quarantine record retains the raw response. Endpoint tests pass (12/12) after Stage 2, then 15/15 after repair and quarantine were added.

## 2026-11-16 — Stage 3: bounded repair and quarantine

- Added exactly one repair call after JSON/schema failure. The correction request carries validation diagnostics with input values excluded.
- After a second invalid response, the API returns a generic validation failure and appends the raw result, source record, prompt version, and timestamp to ignored local `logs/quarantine.jsonl`.
- Added `LLM_ENABLED=false` kill switch. It returns a valid deterministic fallback without contacting the provider.
- Verified repair success, exactly one repair on repeated failure, quarantine output, and kill-switch behavior with mocked provider tests. All 15 endpoint tests pass.

## 2026-11-17 — Stage 4: provider limits and call records

- Set the HTTP client's request timeout to 12 seconds and disabled hidden SDK retries. The adapter retries at most once for timeouts, connection failures, 429, and 5xx; authentication and other client errors are not retried.
- Honors short `Retry-After` values (up to two seconds). Longer provider cooldowns are returned immediately so a free-tier quota wait cannot leave the workflow hanging.
- Added structured stdout records for prompt version, actual model, prompt/completion tokens, provider-reported cost when available, duration, and repair count. No prompt, input, output, or credential is logged.
- Verified 429 retry, 401 no-retry, long `Retry-After` handling, and safe telemetry with mocked provider responses. All 18 endpoint/provider tests pass.

## 2026-11-17 — Stage 5: evaluation and handoff docs

- Added eight human-labelled cases and a local HTTP eval runner that reports schema pass rate, exact category accuracy, and expected quality-flag checks. The runner can save a JSON report, but no report is checked in before a real run.
- Added local setup, endpoint examples, prompt and guardrail behavior, retry limits, kill switch, test command, and current evaluation status to the assignment README and repository index.
- Ran Python compilation, the eval runner's help path, all 18 local tests, and `git diff --check`; all passed. No live model evaluation was run because the local `.env` has no key. The real score, returned model, and cost remain to be recorded after credentials are configured.
- Started the API separately from Docker on port 8017 with `LLM_STUB=1`, posted a book record with `curl`, received HTTP 200 and the documented deterministic stub response, then stopped that temporary server. This confirms the HTTP loop in stub mode; it is not a model result.

## 2026-11-17 — Stage 6: first live evaluation and credential isolation

- Confirmed the local `.env` contains a key without printing it; `.env` is ignored and is not tracked by Git.
- The first eight-case live evaluation returned 3/8 schema-valid responses. Five calls failed in the provider adapter; the API hid the upstream status, which made the report hard to diagnose. A later one-case retry for E02 succeeded.
- The full mocked suite initially failed because the app's database setup loads `.env`, so a “missing API key” test made a real provider request. Fixed the test to explicitly clear provider settings. It now passes without using the key.
- Added safe provider-error classification (status or exception type only) to API details and included HTTP error details in eval reports. No provider response body or credential is exposed.
- Reran the full eight-case evaluation. Latest result: schema 4/8, category match 4/8 (all four valid responses matched), and the insufficient-text flag case did not finish because its request failed. Four provider calls failed intermittently. Individual retries of E02 and E03 then succeeded with the expected labels. The free route selected different model IDs across successful calls and reported $0 provider cost for those calls.
- Ran the full local suite after the test-isolation and error-reporting changes: 19 passed. The live run remained a revise because the free route did not complete all eight cases reliably.

## 2026-11-17 — Stage 7: pin model, pace requests, rerun evaluation

- Replaced `openrouter/free` with `baidu/ernie-5.5-flash-preview:free` in the local ignored `.env` and public `.env.example`. OpenRouter lists this as a zero-price model with structured JSON support and 99.93% availability over the previous three days; it is served by one provider. The earlier individual live calls had succeeded with this model.
- Enabled JSON mode for the pinned model while keeping Pydantic validation as the contract. Added `LLM_JSON_MODE=0` for providers without JSON mode.
- Corrected eval case E04: its old description was a nonfiction book about comics, making its expected `comics` label ambiguous. Replaced it with a clearly described Tintin comic-book story.
- Added a default four-second gap between eval requests to stay below the free request-per-minute limit. The exact cause of the earlier 429 was not isolated; model pinning and pacing were changed together.
- After a cooldown, the full live eval passed: 8/8 schema-valid, 8/8 expected categories, and the insufficient-text flag matched. The same pinned model served all eight calls. Logs totaled 4,261 prompt tokens and 1,267 completion tokens; provider-reported cost was $0.00. At 10,000 calls/day, that is approximately 5.33 million input and 1.58 million output tokens/day, above the free tier's 50 requests/day limit.
- Re-ran the local suite after the model and JSON-mode changes: 19 passed. The latest eval report is checked in; the local API key remains ignored and untracked.
