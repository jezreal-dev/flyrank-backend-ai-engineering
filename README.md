# FlyRank Backend AI Engineering Track

Welcome to the repository for the **FlyRank Backend AI Engineering** assignments, layered architecture implementations, and reference walkthroughs.

## 1. Assignments Index (Python / FastAPI + SQLite Track)

| ID | Assignment | Architecture & Stack | Folder | Status |
| :--- | :--- | :--- | :--- | :--- |
| **BE-01 (W1/W2 · A1)** | Build Your First CRUD API | Python, FastAPI, Uvicorn | [`./BE-01-crud-api`](./BE-01-crud-api) | Complete |
| **BE-06 (W7 · A7)** | Your First Background Job (202 Accepted + Inngest Queues, Workers & Cron) | FastAPI, Inngest Python SDK, Inngest Dev Server | [`./BE-06-background-jobs`](./BE-06-background-jobs) | Complete (All 6 stages, retries with backoff, cron, AI rematch) |
| **BE-09 (W7)** | Build an AI Decision Flow with React Flow + Inngest | Next.js 14, React Flow, Inngest, OpenAI SDK, Tailwind CSS | [`./BE-09-decision-flow`](./BE-09-decision-flow) | Complete (Phases 1–4, binary branching, live execution traces) |
| **BE-07 (W6)** | Connect to an AI API: schema-validated book enrichment | FastAPI, Pydantic, OpenRouter-compatible API | [`./BE-01-crud-api`](./BE-01-crud-api#be-07-connect-to-an-ai-api) | Complete (8/8 eval passed, 100% schema & category accuracy) |
| **BE-02 (W3 · A2)** | Connecting Your CRUD to the Database (Layered + SQLite) | 3-Layer (`routes` $\rightarrow$ `services` $\rightarrow$ `repositories` + `database.py` SQLite) | [`./BE-01-crud-api`](./BE-01-crud-api) | Complete |
| **BE-05 (W5 · A9)** | The Polite Scraper (3 Catalogue Pages $\rightarrow$ 60 Validated Books) | Python, `requests`, `beautifulsoup4`, `pydantic`, `pytest` | [`./scraper`](./scraper) | Complete |

## 2. Week 5 Learning Notes

### Backend AI Engineering
- [Scraping in Practice — From Messy HTML to Clean Data](./workshops/BE-S5-Web-Scraping-in-Practice.md): session notes, recording chapters, and the documented scope difference between the lecture exercise and BE-05.
- [Watch the workshop recording](https://youtu.be/aQZKJOqrg2Q).
- The scraper's implementation, run instructions, outputs, and tests are documented in [`scraper/README.md`](./scraper/README.md).

### General AI Fluency
- [Who Is Watching the Robot? — AI Governance, Security, Risk & Compliance](./learning/general-ai-fluency/week-05/ai-governance-risk-compliance.md): session summary, current official framework references, and an application to the FL-07 Study Coach.
- [Raw transcript supplied with the course](./learning/general-ai-fluency/week-05/ai-governance-risk-compliance-transcript.txt) · [Recording](https://www.youtube.com/watch?v=AXDwPosCqU8).
- [Week 9: Launch & Keep Building — Graduation & Compounding Platform](./learning/general-ai-fluency/week-09/launch-and-keep-building.md): Synthesis of Checkpoint 2 launch gate, adversarial testing (Break Your Own Site), planting your flag (domain, HTTPS, analytics, graduate badge), and the 30-minute keep-building habit.
- [Curriculum Reference Guide](https://aifluency.flyrank.ai/week-09.html).

## 3. Week 6 Mentor Notes

- [Web3 & Crypto — Alessandro Macagno](./workshops/BE-W6-Web3-and-Crypto.md): transcript-informed notes on verifiability, blockchain mechanics, wallets, keys, transactions, smart contracts, tokens, practical risks, and the testnet exercise.
- [Watch the recording](https://www.youtube.com/watch?v=ZE3eLTe4XTc).

## 4. Week 6 Assignment

- [BE-07: Connect to an AI API](./BE-01-crud-api#be-07-connect-to-an-ai-api) enriches one scraped book record with a schema-checked category and short summary. The README explains setup, the prompt, safety and retry behavior, and how to run the eight labelled evaluation cases. The real-model evaluation was executed with `baidu/ernie-5.5-flash-preview:free`, passing 8/8 schema checks and 8/8 category matches (100% accuracy) at $0.00 provider-reported cost.

## 5. Week 7 Mentor & Workshop Notes

- [From Skeptic to AI-First Developer — Jasmin Dudic](./workshops/BE-W7-From-Skeptic-to-AI-First-Developer.md): In-depth guide on the developer AI adoption curve (from skeptic to Claude Code agentic engineering), core primitives (thinking modes, plans, skills, context engineering), where AI falls short, and an end-to-end live build and deployment to Render.
- [Watch Jasmin Dudic's session on YouTube](https://www.youtube.com/watch?v=RuvzDOR6hF0).
- [When the Request Can't Wait — Background Jobs & Durable Workflows](./workshops/BE-W6-Background-Jobs-and-Durable-Workflows.md): Inngest queues, workers, polling, and retry backoff.
- [LLMs in Production](./workshops/BE-W6-LLMs-in-Production.md): Provider seams, schema-checked JSON, smart retries, and unit economics.

## 6. Official Walkthrough Reference Codebases (Cloned & Included)

| Reference Repo | Purpose in Week 3 Walkthrough (`https://youtu.be/FdhEiQ5I4q8`) | Folder |
| :--- | :--- | :--- |
| **`BE-A1-First-CRUD-API`** | Single-file Express CRUD baseline (`index.js` + `openapi.json`) showing why in-memory data disappears on restart and why single-file architecture becomes hard to maintain. | [`./BE-A1-First-CRUD-API`](./BE-A1-First-CRUD-API) |
| **`BE-Internship-Layered-architecture-example`** | Refactored 3-Layer Architecture (`src/routes/`, `src/services/`, `src/repositories/`, `src/middleware/error-handler.js`, `src/errors.js`) demonstrating Separation of Concerns so swapping storage touches only the repository layer. | [`./BE-Internship-Layered-architecture-example`](./BE-Internship-Layered-architecture-example) |

## 6. How the 3-Layer Architecture Maps Across Both Stacks

| Layer | Responsibility | Node.js Reference (`BE-Internship-Layered-architecture-example`) | Python + SQLite Assignment (`BE-01-crud-api`) |
| :--- | :--- | :--- | :--- |
| **1. Routes (HTTP Layer)** | Parse request params/body, call service, return status codes (`200`, `201`, `204`). | `src/routes/tasks.routes.js` | `src/routes/tasks_routes.py` |
| **2. Service (Business Rules)** | Validate inputs, enforce domain rules, raise `ValidationError` / `NotFoundError`. | `src/services/tasks.service.js` | `src/services/tasks_service.py` |
| **3. Repository (Data Access)** | The **only** layer that knows where tasks are stored (`tasks.db` SQLite). | `src/repositories/tasks.repository.js` | `src/repositories/tasks_repository.py` + `database.py` |
| **4. Error Handling** | Map domain errors to HTTP `400` / `404` responses in one central place. | `src/middleware/error-handler.js` + `src/errors.js` | `src/middleware/error_handler.py` + `src/errors.py` |
