# BE-01 & W3-A3: Containerized Task CRUD API (FastAPI + PostgreSQL + Docker Compose)

A production-grade, containerized RESTful CRUD API built with **Python 3.12**, **FastAPI**, **PostgreSQL 16**, **`psycopg` 3**, and **Docker Compose**, completing Assignment **A3 (`BE-04: Containerize Your Stack`)** of the FlyRank Backend AI Engineering track.

---

## 1. Goal & The Storage Evolution

This assignment marks the third stage in FlyRank's architectural storage ladder:

| Assignment | Storage Mechanism | Engine & Execution | Routes / Services Changed? |
| :--- | :--- | :--- | :--- |
| **A1 (`BE-01`)** | In-Memory list (`tasks = []`) | App memory (lost on restart) | Baseline implementation |
| **A2 (`BE-02`)** | SQLite file on disk (`tasks.db`) | Embedded `sqlite3` driver | **No** (routes & service unchanged) |
| **A3 (`BE-04`)** | Relational Database in Docker | PostgreSQL 16 + `psycopg` 3 + named volume | **No** — only the repository module changed! |

### Layered Architecture Proving Itself
Because the project enforces strict horizontal separation of concerns:
```text
HTTP Request  ──>  src/routes/tasks_routes.py  (FastAPI route handlers & status codes)
                          │
                          ▼
                   src/services/tasks_service.py  (Business logic & input validation)
                          │
                          ▼
                   src/repositories/tasks_repository.py  (Data Access Layer)
                          │
         ┌────────────────┴────────────────┐
         ▼                                 ▼
   PostgreSQL 16 (A3 Container)     SQLite tasks.db (A2 Fallback)
```
Swapping from SQLite to PostgreSQL changed **only one module** (`src/repositories/`). The routes (`src/routes/`) and services (`src/services/`) remain **100% unchanged**—proving that clean architecture makes storage an implementation detail.

---

## 2. One-Command Stack Startup

Start the entire stack (FastAPI web application, PostgreSQL database, and Redis cache) with a single command:

```bash
# 1. Copy the environment configuration template
cp .env.example .env

# 2. Build and run all services in the background
docker compose up --build -d
```

### Stopping the Stack
```bash
docker compose down
```

---

## 3. Environment Variables Reference

All credentials and connection parameters are loaded via environment variables (never committed to Git). A template is provided in committed [`.env.example`](./.env.example):

| Variable | Example Value | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | `postgresql://postgres:dev@db:5432/tasks` | Full connection string. Inside Docker Compose, the host resolves to service name `db`. For host access outside Docker, port `5433` is mapped to container `5432`. |
| `POSTGRES_USER` | `postgres` | Superuser username for PostgreSQL. |
| `POSTGRES_PASSWORD` | `dev` | Database password (kept secret, ignored by Git). |
| `POSTGRES_DB` | `tasks` | Target PostgreSQL database name. |
| `REDIS_URL` | `redis://redis:6379/0` | Cache connection URL for Redis 7 service. |

> **Security Guarantee**: `.env` is listed in [`.gitignore`](../.gitignore) and [`.dockerignore`](./.dockerignore). Credentials are never baked into Docker images or committed to version control.

---

## 4. Endpoints Reference

| Method | Path | Status Codes | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | `200 OK` | Root metadata returning API name, version, and endpoints list. |
| `GET` | `/health` | `200 OK` | Real health check running `SELECT 1` against PostgreSQL (`{"status": "ok", "db": "ok"}`). |
| `GET` | `/tasks` | `200 OK` | Lists all tasks from PostgreSQL. Supports query parameters `?done=true\|false`, `?search=keyword` (`ILIKE`), `?sort=title`, and pagination (`?limit=&offset=`). |
| `GET` | `/tasks/{id}` | `200 OK`, `404 Not Found` | Fetches a single task by ID using parameterized query (`WHERE id = %s`). |
| `POST` | `/tasks` | `201 Created`, `400 Bad Request` | Creates a new task via parameterized `INSERT ... VALUES (%s, %s) RETURNING *`. |
| `PUT` | `/tasks/{id}` | `200 OK`, `400 Bad Request`, `404 Not Found` | Updates task title and/or done status via `UPDATE ... RETURNING *`. |
| `DELETE` | `/tasks/{id}` | `204 No Content`, `404 Not Found` | Deletes a task by ID via parameterized `DELETE FROM tasks WHERE id = %s`. |
| `GET` | `/stats` | `200 OK` | Computes `{"total": X, "done": Y, "open": Z}` via SQL `COUNT(*)` aggregations. |
| `POST` | `/reset` | `200 OK` | Deterministically resets the database back to the 3 starter tasks (IDs 1, 2, 3). |

---

## 5. Live `curl -i` Execution Logs

All tests run live against the Docker Compose stack running on `http://localhost:8000`:

### 1. List Seeded Tasks (`GET /tasks` $\rightarrow$ 200 OK)
```http
$ curl -i http://localhost:8000/tasks
HTTP/1.1 200 OK
date: Sun, 25 Oct 2026 02:12:20 GMT
server: uvicorn
content-length: 165
content-type: application/json

[{"id":1,"title":"Read the FastAPI docs","done":true},{"id":2,"title":"Build a CRUD API","done":false},{"id":3,"title":"Test every endpoint with curl","done":false}]
```

### 2. Fetch Single Task (`GET /tasks/1` $\rightarrow$ 200 OK)
```http
$ curl -i http://localhost:8000/tasks/1
HTTP/1.1 200 OK
date: Sun, 25 Oct 2026 02:12:33 GMT
server: uvicorn
content-length: 52
content-type: application/json

{"id":1,"title":"Read the FastAPI docs","done":true}
```

### 3. Unknown Task Returns Error JSON (`GET /tasks/999` $\rightarrow$ 404 Not Found)
```http
$ curl -i http://localhost:8000/tasks/999
HTTP/1.1 404 Not Found
date: Sun, 25 Oct 2026 02:12:33 GMT
server: uvicorn
content-length: 30
content-type: application/json

{"error":"Task 999 not found"}
```

### 4. Create Task with RETURNING Clause (`POST /tasks` $\rightarrow$ 201 Created)
```http
$ curl -i -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Deploy stack with Docker Compose"}'

HTTP/1.1 201 Created
date: Sun, 25 Oct 2026 02:12:33 GMT
server: uvicorn
content-length: 65
content-type: application/json

{"id":34,"title":"Deploy stack with Docker Compose","done":false}
```

### 5. Input Validation Rejects Empty Title (`POST /tasks` $\rightarrow$ 400 Bad Request)
```http
$ curl -i -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": ""}'

HTTP/1.1 400 Bad Request
date: Sun, 25 Oct 2026 02:12:33 GMT
server: uvicorn
content-length: 49
content-type: application/json

{"error":"Title is required and cannot be empty"}
```

### 6. Update Task Status (`PUT /tasks/34` $\rightarrow$ 200 OK)
```http
$ curl -i -X PUT http://localhost:8000/tasks/34 \
  -H "Content-Type: application/json" \
  -d '{"done": true}'

HTTP/1.1 200 OK
date: Sun, 25 Oct 2026 02:13:04 GMT
server: uvicorn
content-length: 64
content-type: application/json

{"id":34,"title":"Deploy stack with Docker Compose","done":true}
```

### 7. Delete Task (`DELETE /tasks/34` $\rightarrow$ 204 No Content)
```http
$ curl -i -X DELETE http://localhost:8000/tasks/34
HTTP/1.1 204 No Content
date: Sun, 25 Oct 2026 02:13:12 GMT
server: uvicorn
```

---

## 6. Proof of Persistence Across Full-Stack Restart

To prove that PostgreSQL data survives container destruction, we created row `id: 35`, completely stopped and removed all containers with `docker compose down`, and restarted them with `docker compose up -d`.

### Step 1: Create a Persistent Row Before Shutdown
```bash
$ curl -s -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Persistence Test: Survives docker compose restart"}'
{"id":35,"title":"Persistence Test: Survives docker compose restart","done":false}
```

### Step 2: Tear Down the Whole Stack
```bash
$ docker compose down
[+] Running 4/4
 ✔ Container taskapi              Removed
 ✔ Container taskcache            Removed
 ✔ Container taskdb               Removed
 ✔ Network be-01-crud-api_default Removed
```

### Step 3: Restart Stack and Verify Rows Still Exist
```bash
$ docker compose up -d
[+] Running 4/4
 ✔ Network be-01-crud-api_default Created
 ✔ Container taskdb               Healthy
 ✔ Container taskcache            Healthy
 ✔ Container taskapi              Started

$ curl -s http://localhost:8000/tasks
[
  {"id":1,"title":"Read the FastAPI docs","done":true},
  {"id":2,"title":"Build a CRUD API","done":false},
  {"id":3,"title":"Test every endpoint with curl","done":false},
  {"id":35,"title":"Persistence Test: Survives docker compose restart","done":false}
]
```

### Step 4: Direct `psql` Inspection Inside Container
```bash
$ docker exec taskdb psql -U postgres -d tasks -c "\dt"
         List of relations
 Schema | Name  | Type  |  Owner   
--------+-------+-------+----------
 public | tasks | table | postgres
(1 row)

$ docker exec taskdb psql -U postgres -d tasks -c "SELECT id, title, done FROM tasks ORDER BY id ASC;"
 id |                       title                       | done 
----+---------------------------------------------------+------
  1 | Read the FastAPI docs                             | t
  2 | Build a CRUD API                                  | f
  3 | Test every endpoint with curl                     | f
 35 | Persistence Test: Survives docker compose restart | f
(4 rows)
```
**Conclusion**: Because the PostgreSQL service mounts named volume `taskdata:/var/lib/postgresql/data`, all records remain intact across arbitrary container destroys, recreations, and engine reboots.

---

## 7. Stretch Goals Completed

### 1. Real Database Health Check (`GET /health`)
The `/health` endpoint executes `SELECT 1;` on the live connection pool to verify the database engine is accepting queries:
```json
{
  "status": "ok",
  "db": "ok"
}
```
*Why this matters in production*: Reverse proxies and load balancers (e.g. AWS ALB, Kubernetes readiness probes) rely on this endpoint to route traffic only to application replicas that have an active database connection.

### 2. Redis 7 In-Memory Cache Service
Added `redis:7-alpine` to `docker-compose.yml` with automated container healthcheck. Verified live response:
```bash
$ docker exec taskcache redis-cli ping
PONG
```

### 3. Database Index & `EXPLAIN ANALYZE` Performance Proof
Created index `CREATE INDEX IF NOT EXISTS idx_tasks_done ON tasks(done);`.

**Query Execution Without Index (Sequential Table Scan)**:
```text
Seq Scan on tasks  (cost=0.00..22.50 rows=625 width=37) (actual time=0.022..0.023 rows=1 loops=1)
  Filter: done
  Rows Removed by Filter: 3
Planning Time: 0.304 ms
Execution Time: 0.097 ms
```

**Query Execution With Index (Bitmap Index Scan)**:
```text
Bitmap Heap Scan on tasks  (cost=9.00..25.25 rows=625 width=37) (actual time=0.422..0.424 rows=1 loops=1)
  Recheck Cond: done
  Heap Blocks: exact=1
  ->  Bitmap Index Scan on idx_tasks_done  (cost=0.00..8.84 rows=625 width=0) (actual time=0.124..0.124 rows=4 loops=1)
        Index Cond: (done = true)
Planning Time: 0.617 ms
Execution Time: 0.732 ms
```

### 4. Slim Multi-Stage Dockerfile Size Comparison
We implemented a two-stage Dockerfile (`builder` $\rightarrow$ `runner` on `python:3.12-slim`). Build artifacts and wheel caches are stripped from the final runtime image:
- **Standard Single-Stage Python 3.12 Image**: $\sim 1,020\text{ MB}$ (1.02 GB)
- **Our Multi-Stage Slim Image (`be-01-crud-api-api`)**: **54.8 MB** (content size)
- **Reduction**: **$\approx 95\%$ size reduction**, improving deploy speed and security footprint.

---

## 8. Stage 6: The AI Rematch (AI vs. Me Code Review)

To complete Stage 6, we prompted an AI assistant to generate a containerized FastAPI + PostgreSQL stack in quarantine ([`ai-version/`](./ai-version/)), ran diff analysis against our hand-crafted stack, and conducted a code review:

### Prompts Used
Recorded in full in [`ai-version/prompt.md`](./ai-version/prompt.md).

### Diff Comparison (`git diff --no-index`)
```bash
git diff --no-index ai-version/docker-compose.ai.yml docker-compose.yml
git diff --no-index ai-version/Dockerfile.ai Dockerfile
```

### Key Differences & Takeaways
1. **Startup Race Condition Handling**: The AI's compose file used a bare `depends_on: [db]`. In production, this creates race conditions because Docker considers `db` started as soon as the container process begins, but PostgreSQL takes 3–5 seconds to initialize sockets. Our production compose file includes healthchecks (`pg_isready`) and specifies `condition: service_healthy` so FastAPI never crashes on startup.
2. **Container Image Bloat**: The AI generated a naive single-stage Dockerfile based on full `python:3.12` ($\approx 1\text{ GB}$). Our implementation uses a multi-stage `python:3.12-slim` build, reducing the image to **54.8 MB**.
3. **Host Port Collisions & Networking**: The AI directly mapped `5432:5432`, which conflicts with existing native PostgreSQL instances on developer workstations. Our solution isolates the container's external mapping to `5433:5432` while keeping internal compose networking on standard `db:5432`.
