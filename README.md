# FlyRank Backend AI Engineering Track

Welcome to the repository for the **FlyRank Backend AI Engineering** assignments, layered architecture implementations, and reference walkthroughs.

## 1. Assignments Index (Python / FastAPI + SQLite Track)

| ID | Assignment | Architecture & Stack | Folder | Status |
| :--- | :--- | :--- | :--- | :--- |
| **BE-01 (W1/W2 · A1)** | Build Your First CRUD API | Python, FastAPI, Uvicorn | [`./BE-01-crud-api`](./BE-01-crud-api) | Complete |
| **BE-02 (W3 · A2)** | Connecting Your CRUD to the Database (Layered + SQLite) | 3-Layer (`routes` $\rightarrow$ `services` $\rightarrow$ `repositories` + `database.py` SQLite) | [`./BE-01-crud-api`](./BE-01-crud-api) | Complete |
| **BE-05 (W5 · A9)** | The Polite Scraper (3 Catalogue Pages $\rightarrow$ 60 Validated Books) | Python, `requests`, `beautifulsoup4`, `pydantic`, `pytest` | [`./scraper`](./scraper) | Complete |

## 2. Official Walkthrough Reference Codebases (Cloned & Included)

| Reference Repo | Purpose in Week 3 Walkthrough (`https://youtu.be/FdhEiQ5I4q8`) | Folder |
| :--- | :--- | :--- |
| **`BE-A1-First-CRUD-API`** | Single-file Express CRUD baseline (`index.js` + `openapi.json`) showing why in-memory data disappears on restart and why single-file architecture becomes hard to maintain. | [`./BE-A1-First-CRUD-API`](./BE-A1-First-CRUD-API) |
| **`BE-Internship-Layered-architecture-example`** | Refactored 3-Layer Architecture (`src/routes/`, `src/services/`, `src/repositories/`, `src/middleware/error-handler.js`, `src/errors.js`) demonstrating Separation of Concerns so swapping storage touches only the repository layer. | [`./BE-Internship-Layered-architecture-example`](./BE-Internship-Layered-architecture-example) |

## 3. How the 3-Layer Architecture Maps Across Both Stacks

| Layer | Responsibility | Node.js Reference (`BE-Internship-Layered-architecture-example`) | Python + SQLite Assignment (`BE-01-crud-api`) |
| :--- | :--- | :--- | :--- |
| **1. Routes (HTTP Layer)** | Parse request params/body, call service, return status codes (`200`, `201`, `204`). | `src/routes/tasks.routes.js` | `src/routes/tasks_routes.py` |
| **2. Service (Business Rules)** | Validate inputs, enforce domain rules, raise `ValidationError` / `NotFoundError`. | `src/services/tasks.service.js` | `src/services/tasks_service.py` |
| **3. Repository (Data Access)** | The **only** layer that knows where tasks are stored (`tasks.db` SQLite). | `src/repositories/tasks.repository.js` | `src/repositories/tasks_repository.py` + `database.py` |
| **4. Error Handling** | Map domain errors to HTTP `400` / `404` responses in one central place. | `src/middleware/error-handler.js` + `src/errors.js` | `src/middleware/error_handler.py` + `src/errors.py` |
