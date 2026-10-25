# AI Rematch Prompts & Evaluation (BE-04)

## Prompt 1 (Initial AI Generation)
> "You are an expert backend engineer. Take our FastAPI Task CRUD API and containerize it onto PostgreSQL using `psycopg` 3. Requirements:
> 1. Store database credentials in `.env` and commit `.env.example`. Never hardcode secrets.
> 2. Create the `tasks` table (`id serial primary key`, `title text`, `done boolean`) on startup, and seed the 3 starter tasks only if the table is empty.
> 3. Implement full CRUD using parameterized queries (`%s`).
> 4. Write a `Dockerfile` and `docker-compose.yml` to start both the API and PostgreSQL with one command (`docker compose up`).
> 5. Use a Docker named volume so data persists across restarts."

---

## Prompt 2 (Rematch Prompt — Sharpened Specification)
> "You are an expert production systems engineer. Containerize a FastAPI task CRUD service and PostgreSQL 16 using Docker Compose and `psycopg` 3 with strict production constraints:
> 1. Strict layered architecture: the repository must implement `find_all`, `find_by_id`, `create`, `update`, `remove`, `get_stats`, and `reset` so that routes and service layers remain 100% unchanged.
> 2. Use a multi-stage Dockerfile based on `python:3.12-slim` to reduce image size and keep compilers out of runtime.
> 3. In `docker-compose.yml`, define `api`, `db`, and a `redis:7-alpine` caching service. Use container healthchecks (`pg_isready` for Postgres) and configure `depends_on` with `condition: service_healthy` so the web API never crashes waiting for Postgres socket initialization.
> 4. Add a database index on the `done` boolean column and provide `EXPLAIN ANALYZE` proof.
> 5. Ensure internal container networking connects via service hostname `db:5432`, and map the database port cleanly to avoid host port collisions."
