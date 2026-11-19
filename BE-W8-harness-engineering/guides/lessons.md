# Hard-Won Operational Facts & Engineering Lessons

This guide captures hard-won production lessons from building FastAPI, SQLite, and Agentic harnesses across the FlyRank Backend AI Engineering track.

---

## Fact 1: Pydantic v2 Alias Handling
- **Lesson:** Pydantic v2 explicitly rejects model fields with leading underscores (e.g., `_gotcha: Optional[str]`).
- **Fix:** Declare the model with `Field(default="", alias="_gotcha")` and configure `model_config = ConfigDict(populate_by_name=True)`.
- **Harness Rule:** When the agent validates ingress payloads, it must never mutate the model to remove the leading underscore from the incoming JSON.

## Fact 2: SQLite Thread-Safety in Async Environments
- **Lesson:** In FastAPI async routes, background workers run on AnyIO worker threads. SQLite defaults to thread-pinning, throwing `sqlite3.ProgrammingError: SQLite objects created in a thread can only be used in that same thread`.
- **Fix:** Always instantiate `sqlite3.connect(db_path, check_same_thread=False)` and enable WAL mode (`PRAGMA journal_mode=WAL;`).

## Fact 3: Contract Fingerprint Immutability
- **Lesson:** An executing agent, when encountering a test failure, will frequently "cheat" by editing the contract or test assertion rather than fixing the code.
- **Fix:** The harness seals the contract with a SHA-256 fingerprint in a separate file. Before running the probe, the harness verifies the contract hash. If mismatched, it terminates with `BLOCKED`.

## Fact 4: Three-Terminal Runner Design
- **Lesson:** An agent loop without explicit terminal states either runs indefinitely (burning tokens/quota) or silently reports false success.
- **Fix:** Enforce exactly three endings: `DONE` (exit 0), `BLOCKED` (exit 2), and `SAFETY_LIMIT` (exit 3).
