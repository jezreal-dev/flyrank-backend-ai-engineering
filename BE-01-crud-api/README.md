# BE-01 & W3-A2: Task CRUD API (FastAPI + SQLite)

A clean, production-structured RESTful CRUD API built with **Python**, **FastAPI**, and **SQLite (`sqlite3`)** across Assignments **A1 (`BE-01`)** and **A2 (`W3 · A2`)** of the FlyRank Backend AI Engineering track.

---

## Architecture & Separation of Concerns

```text
Client  -->  main.py (API / HTTP Layer)  -->  database.py (SQLite Storage Layer)  -->  tasks.db (On Disk)
```

| File | Layer | Responsibility |
| :--- | :--- | :--- |
| [`main.py`](./main.py) | **API / HTTP Layer** *(Week 1/2)* | Defines FastAPI routes, HTTP status codes (`200`, `201`, `204`, `400`, `404`), and input validation. Contains **zero SQL**. |
| [`database.py`](./database.py) | **Storage Layer** *(Week 3)* | Manages `tasks.db`, automatic schema creation, idempotent seeding, and parameterized SQL queries (`?`). Contains **zero FastAPI/HTTP code**. |
| [`stage4_queries.sql`](./stage4_queries.sql) | **SQL Exploration** *(Week 3 · Stage 4)* | Hand-executed SQL queries for inspecting and mutating `tasks.db` directly. |
| [`ai-version/main_ai.py`](./ai-version/main_ai.py) | **Quarantined AI Build** *(Stage 6)* | Single-shot AI-generated implementation kept separate for `git diff` code review. |

---

## Quick Start (1-Command Run)

```bash
uvicorn main:app --reload --port 8000
```

> First time setting up the virtual environment?
> ```bash
> python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
> uvicorn main:app --reload --port 8000
> ```

When the server starts:
1. `init_db()` in [`database.py`](./database.py) automatically creates `tasks.db` and the `tasks` table if they do not exist.
2. If `SELECT COUNT(*) FROM tasks` is `0`, it seeds the 3 starter tasks inside a transaction. Restarting the server never duplicates the seed data.

---

## Why SQLite & Where the Database Lives

- **Why SQLite was chosen**: SQLite is a serverless, zero-configuration relational database stored in a single file on disk, and Python ships with `sqlite3` built into its standard library. It gives us real SQL queries, ACID transactions, and durable persistence across server restarts without needing a separate database server container.
- **Where the database file lives**: The database file is stored at `./tasks.db` (created automatically next to `main.py` on first run). It is listed in `.gitignore` so every fresh `git clone` starts with a clean, automatically seeded database.

---

## Endpoints Reference

| Method | Path | Status Codes | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | `200 OK` | Returns API metadata (`name`, `version`, and available `endpoints`). |
| `GET` | `/health` | `200 OK` | Health check endpoint returning `{"status": "ok"}`. |
| `GET` | `/tasks` | `200 OK` | Lists tasks from `tasks.db`. Supports SQL filters `?done=true\|false` (`WHERE done = ?`), `?search=keyword` (`WHERE title LIKE ?`), `?sort=title` (`ORDER BY title`), and `?limit=&offset=`. |
| `GET` | `/tasks/{id}` | `200 OK`, `404 Not Found` | Fetches one task via `SELECT id, title, done FROM tasks WHERE id = ?`, or returns `{"error": "Task {id} not found"}`. |
| `POST` | `/tasks` | `201 Created`, `400 Bad Request` | Validates `{"title": "..."}` and inserts a row via `INSERT INTO tasks (title, done) VALUES (?, ?)`. |
| `PUT` | `/tasks/{id}` | `200 OK`, `400 Bad Request`, `404 Not Found` | Updates a task's `title` and/or `done` via `UPDATE tasks SET title = ?, done = ? WHERE id = ?`. |
| `DELETE` | `/tasks/{id}` | `204 No Content`, `404 Not Found` | Deletes a row via `DELETE FROM tasks WHERE id = ?` and returns an empty body on success. |
| `GET` | `/stats` | `200 OK` | Computes `{"total": X, "done": Y, "open": Z}` directly in SQL using `SELECT COUNT(*) FROM tasks`. |
| `POST` | `/reset` | `200 OK` | Restores `tasks.db` back to the original 3 starter tasks in a single transaction. |

---

## Real `curl -i` Checkpoint Output

The exact same `curl -i` commands from Assignment 1 (`BE-01`) pass without modification against the SQLite-backed API:

```http
$ curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{"title": "Wire PUT and DELETE to SQLite"}'
HTTP/1.1 201 Created
date: Tue, 20 Oct 2026 12:23:10 GMT
server: uvicorn
content-length: 61
content-type: application/json

{"id":4,"title":"Wire PUT and DELETE to SQLite","done":false}

$ curl -i -X PUT http://localhost:8000/tasks/4 -H "Content-Type: application/json" -d '{"title": "Wired PUT and DELETE to SQLite", "done": true}'
HTTP/1.1 200 OK
date: Tue, 20 Oct 2026 12:23:10 GMT
server: uvicorn
content-length: 61
content-type: application/json

{"id":4,"title":"Wired PUT and DELETE to SQLite","done":true}

$ curl -i http://localhost:8000/tasks/4
HTTP/1.1 200 OK
date: Tue, 20 Oct 2026 12:23:10 GMT
server: uvicorn
content-length: 61
content-type: application/json

{"id":4,"title":"Wired PUT and DELETE to SQLite","done":true}

$ curl -i -X DELETE http://localhost:8000/tasks/4
HTTP/1.1 204 No Content
date: Tue, 20 Oct 2026 12:23:10 GMT
server: uvicorn


$ curl -i http://localhost:8000/tasks/4
HTTP/1.1 404 Not Found
date: Tue, 20 Oct 2026 12:23:10 GMT
server: uvicorn
content-length: 28
content-type: application/json

{"error":"Task 4 not found"}
```

---

## Stage 4: Exploring SQLite by Hand

In [`stage4_queries.sql`](./stage4_queries.sql), we executed the 5 core SQL queries directly against `tasks.db`:

```sql
SELECT * FROM tasks WHERE done = 1;
```
**What it returned**: It returned the single completed starter row `[(1, 'Read the FastAPI docs', 1)]`, and when we subsequently ran `UPDATE tasks SET done = 1;` directly against `tasks.db`, calling `GET /tasks` on the running server immediately returned `"done": true` for all three tasks without a server restart because both read the same `tasks.db` file on disk.

---

## Screenshots: Swagger UI (`/docs`) & DB Browser for SQLite

### Swagger UI (`/docs`)
![Swagger UI Screenshot](./assets/swagger-ui.png)

### DB Browser for SQLite (`tasks.db`)
![DB Browser for SQLite Screenshot](./assets/db-browser.png)

*(Save your DB Browser for SQLite screenshot of `tasks.db` to `./assets/db-browser.png`)*

---

## Stretch Goals & Engineering Notes

1. **Why Identical Tests Passing Proves Storage Is "Just an Implementation Detail"**:
   Running the exact same `curl -i` commands from Assignment 1 against the Week 3 SQLite API produces the exact same status codes (`200`, `201`, `204`, `400`, `404`) and JSON payloads, proving that the HTTP API is a stable contract while the underlying storage engine (RAM list vs. SQLite vs. PostgreSQL) is completely hidden from the client.
2. **SQL Index (`CREATE INDEX IF NOT EXISTS idx_tasks_done ON tasks(done)`)**:
   An index is a lookup structure that lets SQLite jump directly to rows matching `WHERE done = ?` instead of scanning every row in the `tasks` table one by one.
3. **Database Transaction (`with get_connection() as conn:`)**:
   Wrapping multi-step SQL operations (like seeding the 3 starter tasks or resetting the table) in a transaction guarantees that either all statements succeed together or the database rolls back cleanly on error, preventing partial or corrupted data.
4. **The Mortality Experiment (Solved in Week 3)**:
   In Week 1/2, tasks vanished on server restart because they lived in volatile process RAM. Moving storage to `tasks.db` on disk solved the mortality experiment—tasks created via `POST /tasks` now survive server restarts indefinitely.

---

## AI vs Me (Week 3 SQLite Rematch)

### The Prompt Used
> *"Migrate my FastAPI Task CRUD API from an in-memory Python list to Python's built-in `sqlite3` using a database file named `tasks.db`. Create the `tasks` table (`id INTEGER PRIMARY KEY`, `title TEXT`, `done INTEGER`) on startup if missing, and seed the 3 starter tasks only when the table is empty. Keep all 5 CRUD endpoints (`GET /tasks`, `GET /tasks/{id}`, `POST /tasks`, `PUT /tasks/{id}`, `DELETE /tasks/{id}`) plus `/stats` and `/reset` with identical status codes (`200`, `201`, `204`, `400`, `404`), `{"error": "..."}` error JSON, and parameterized `?` queries."*

### 3 Concrete Differences Found via `git diff`

1. **Separation of Concerns (`database.py` + `main.py` vs. Monolithic `main_ai.py`)**:
   - **My version**: Splits the HTTP API layer ([`main.py`](./main.py)) from the SQLite storage layer ([`database.py`](./database.py)), so `main.py` contains zero SQL and `database.py` contains zero FastAPI code.
   - **AI version ([`ai-version/main_ai.py`](./ai-version/main_ai.py))**: Put all `sqlite3` connections, SQL strings, Pydantic models, and FastAPI routes into a single monolithic file.
2. **Connection & Transaction Safety (`with get_connection() as conn:` vs. Manual `.commit()` / `.close()`)**:
   - **My version**: Uses Python's context manager (`with get_connection() as conn:`) so transactions commit automatically on success and roll back automatically if an exception occurs.
   - **AI version**: Calls `conn = db_conn()`, `conn.commit()`, and `conn.close()` manually inside each route—if an unexpected error occurs before `conn.close()`, the connection stays open and uncommitted.
3. **Database-Level Filtering & Counting vs. Python Loops**:
   - **My version**: Pushes `?done=`, `?search=` (`WHERE title LIKE ?`), `?sort=title` (`ORDER BY title`), `LIMIT/OFFSET`, and `/stats` (`SELECT COUNT(*)`) down into SQLite so the database engine does the filtering and counting.
   - **AI version**: Runs `SELECT * FROM tasks` to pull every row into Python memory first, then filters `done`/`search` and computes `/stats` using Python list comprehensions—which would become slow on a table with 100,000 rows.
   - **Rematch Takeaway**: When I updated the prompt to explicitly require a separate `database.py` module, context-managed transactions, and SQL-level `WHERE`/`LIKE`/`COUNT(*)` queries, the regenerated code matched our clean two-layer architecture.
