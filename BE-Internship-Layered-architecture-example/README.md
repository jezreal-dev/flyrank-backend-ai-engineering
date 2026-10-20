# Task API — layered version

This is the **same** CRUD API from Assignment 1 — identical endpoints, identical
behaviour — refactored from one 176-line `index.js` into **three layers** so that
each file has one job.

## Run it

```bash
npm install
npm start          # http://localhost:3000  ·  docs at /docs
```

Every endpoint, status code, and validation rule behaves exactly as in Assignment 1.

## The layers

```
Client
  │   HTTP request
  ▼
src/routes/        ← HTTP layer:  read the request, call a service, send the response
  │   plain function calls (ids, bodies)
  ▼
src/services/      ← business rules:  validation, id generation, "not found" logic
  │   findAll / findById / create / update / remove
  ▼
src/repositories/  ← data access:  the ONLY file that knows where tasks are stored
  │
  ▼
Storage  (in-memory now → SQLite in A2 → Postgres in A3)
```

| File | Job | Knows about… |
|---|---|---|
| `src/routes/tasks.routes.js` | Translate HTTP ↔ service calls | `req` / `res`, status codes |
| `src/services/tasks.service.js` | The business rules | validation, id rules — **not** HTTP, **not** storage |
| `src/repositories/tasks.repository.js` | Store & fetch tasks | the data store only |
| `src/middleware/error-handler.js` | Map thrown errors → status codes | `ValidationError`→400, `NotFoundError`→404 |
| `src/errors.js` | Domain error types | nothing about HTTP |
| `src/app.js` | Wire everything into Express | the pieces, not their internals |
| `index.js` | Start the server | just the port |

## Why this matters (the point of the video)

**Separation of concerns.** Each layer changes for one reason. HTTP details change → only the routes. A business rule changes → only the service. **Storage changes → only the repository.**

That last one is the bridge to Week 3. When Assignment 2 moves tasks from memory into a **SQLite** database — and Assignment 3 into **Postgres** — you rewrite exactly one file, `tasks.repository.js`. The routes and the service (your API contract, the promise your clients depend on) never move. The API stays untouched while the database underneath it changes completely.
