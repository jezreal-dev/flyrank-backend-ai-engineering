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
