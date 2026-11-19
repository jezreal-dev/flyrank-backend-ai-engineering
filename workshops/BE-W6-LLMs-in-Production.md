# Week 6 Workshop: LLMs in Production

## Session Details

- **Title:** Workshop: LLMs in Production (`be-s3`)
- **Track:** Backend AI Engineering
- **Portal Date:** August 18, 2026, 1:30 PM (Africa/Lagos GMT+01:00)
- **Portal Duration:** 90 minutes (Build-Along Workshop)
- **Target Assignment:** Preparation for `BE-07` (Connect to an AI API / Put an LLM Behind Your API)
- **Companion Materials:**
  - Attached Guide: `W6 - Your first background job.pdf` (Document metadata: `W4 · A7 — Your first background job`)
  - Associated Resource: [Assignment Overview - LLM in Production](https://internship.flyrank.ai/intern/resources/RES-CUSTOM-MRUSDSFQ-4A3C9C42) (Demo: `POST /quiz` trivia generator via Gemini Flash)
  - Video Reference: [LLM in Production Overview](https://youtu.be/ckrswUArfAo)

---

## 1. Executive Summary & Purpose

In production backend engineering, connecting an LLM to an API is not simply calling an SDK method inside an HTTP route handler. Production systems require:
1. **API Keys isolated in `.env`** and managed through a single provider seam—zero vendor lock-in or hardcoded URLs.
2. **JSON you can trust**—enforced with strict schema validation (Pydantic / Zod) and a closed repair loop when the model misbehaves.
3. **Resilience & Fault Tolerance**—enforcing strict timeouts, retrying only transient errors (429 rate limits, 5xx outages) with backoff, never retrying 400 client bugs, and providing an instant kill-switch.
4. **Observability & Unit Economics**—logging input tokens, output tokens, request latency, and estimated dollar costs per invocation.
5. **Decoupling Slow Work**—identifying when an AI task exceeds acceptable HTTP request thresholds (>5–10s) and offloading it to background job queues.

---

## 2. Core Architectural Principles

### Principle 1: The Provider Seam (Zero Vendor Coupling)
Calling vendor SDKs directly in route handlers tightly couples your API to one provider's quirks, rate limits, and pricing. If that provider experiences an outage, your entire service halts.

* **The Anti-Pattern:**
  ```python
  # BAD: Hardcoded vendor SDK inside route
  from google import genai
  @app.post("/items")
  def create_item(req: ItemRequest):
      client = genai.Client(api_key="AIzaSy...")
      return client.models.generate_content(...)
  ```
* **The Production Pattern:**
  A provider-agnostic service seam (e.g. `services/enrichment.py`) that abstracts the client, model name, base URL, and authentication headers:
  ```text
  FastAPI Route (main.py)
          │
          ▼
  Enrichment Service Seam (services/enrichment.py)
          │
          ├── reads: os.getenv("LLM_API_KEY"), os.getenv("LLM_BASE_URL")
          ├── handles: timeouts, retries, cost logging, schema repair
          ▼
  AI Provider (Gemini / Groq / OpenRouter / Local Ollama)
  ```

---

### Principle 2: JSON You Can Trust (Schemas & Repair Loops)

Raw text responses from LLMs are non-deterministic. Models frequently add markdown fences (````json ... ````), hallucinate unauthorized keys, drop required fields, or alter enum casing.

#### The 3-Layer Defense:
1. **System Prompt Grounding:** A versioned markdown prompt (`prompts/enrich-v1.md`) explicitly defining expected keys, data types, and valid enum values.
2. **Pydantic Validation:** Parsing model output directly through strict Pydantic models.
3. **The Single Repair Loop:**
   - If initial JSON parsing or Pydantic validation fails, make exactly **one repair call** back to the LLM providing the model's invalid output alongside the exact validation error message:
     ```text
     "Your previous response failed validation: {validation_error}.
      Output strictly the corrected JSON adhering to the schema."
     ```
   - If the repair attempt fails, immediately route the payload and error to a **Quarantine Log** (`logs/quarantine.jsonl`) for offline developer inspection and return a graceful HTTP error or fallback.

---

### Principle 3: Timeouts, Smart Retries & The Kill Switch

#### 1. The 12-Second Strict Timeout
Network calls to LLMs can hang indefinitely during provider throttling or high concurrency. Every HTTP request to an external LLM must enforce a strict socket/read timeout:
```python
httpx.Timeout(connect=5.0, read=12.0, write=5.0, pool=5.0)
```

#### 2. The Golden Retry Rule
Never blindly retry all failed API calls:
* **Retryable (Transient):**
  - `429 Too Many Requests` (Rate limits): Wait and retry using exponential backoff with jitter.
  - `500`, `502`, `503`, `504` (Provider Server Errors): Retry up to 2 times.
* **Non-Retryable (Permanent):**
  - `400 Bad Request`: Your request payload or schema is malformed; retrying will yield the identical error.
  - `401 Unauthorized` / `403 Forbidden`: Your API key is invalid or revoked. Retrying burns CPU and adds latency.
  - `404 Not Found`: Model name or endpoint URL does not exist.

#### 3. The Kill Switch (`LLM_ENABLED`)
Production systems require an emergency circuit breaker. By reading an environment flag (`LLM_ENABLED=false`), the backend can immediately bypass all outbound AI network calls and return a deterministic rule-based fallback without redeploying code.

---

### Principle 4: Cost, Latency & Token Accounting

Every LLM call carries a marginal financial cost. Without granular logging, runaway recursive loops or spammed endpoints will exhaust API credits or trigger unexpected billing spikes.

For every call, the provider seam must capture:
- **`input_tokens`**: Tokens consumed by system prompt + user payload.
- **`output_tokens`**: Tokens generated in the response.
- **`latency_ms`**: Total wall-clock time from socket open to response close.
- **`estimated_cost_usd`**: Calculated using published token pricing (e.g. \$0.075 / 1M input tokens for lightweight models).
- **Log Output:** Stored in structured JSONL format alongside request request ID.

---

## 3. The Bridge to Background Jobs (`A7`)

When an AI operation involves large contexts, document summarization, bulk database enrichment, or complex reasoning, processing latency exceeds standard web HTTP timeouts (typically 15–30 seconds on serverless/edge environments like Netlify, Vercel, or AWS API Gateway).

### The Inevitable Handoff:
1. **Synchronous Fast Path (HTTP 200)**: Single-sentence sentiment, tag extraction, or quick validation completing in <2 seconds.
2. **Asynchronous Background Path (HTTP 202 Accepted)**: Multi-step workflows, bulk batch processing, or slow reasoning models.
   - The API receives the request, writes an order record to the database with status `"pending"`, enqueues a background job, and immediately returns `202 Accepted { "job_id": "abc-123" }`.
   - A background worker (Celery, Inngest, BullMQ, or FastAPI `BackgroundTasks`) executes the LLM call asynchronously and writes the result to disk/database.
   - The client polls `GET /jobs/abc-123` until status transitions to `"completed"`.

This directly connects `be-s3` to `A7` (*Your First Background Job*) and the *Background Jobs & Durable Workflows* module.

---

## 4. Verification & Production Implementation Mapping

In our repository (`flyrank-backend-ai-engineering/BE-01-crud-api`), every principle taught in this workshop is fully implemented and tested:

| Workshop Requirement | Production Implementation in Workspace | Verification Evidence |
| :--- | :--- | :--- |
| **Isolated `.env` & Provider Seam** | [`services/enrichment.py`](file:///home/jmomoh/FlyRank%20AI/flyrank-backend-ai-engineering/BE-01-crud-api/services/enrichment.py#L1-L180) | Provider-agnostic HTTP seam supporting Gemini, OpenRouter, and Ollama |
| **Strict Pydantic Schemas** | [`models/schemas.py`](file:///home/jmomoh/FlyRank%20AI/flyrank-backend-ai-engineering/BE-01-crud-api/models/schemas.py) | `EnrichmentResponse`, closed `BookCategory`, `QualityFlag` |
| **Versioned Prompt** | [`prompts/enrich-v1.md`](file:///home/jmomoh/FlyRank%20AI/flyrank-backend-ai-engineering/BE-01-crud-api/prompts/enrich-v1.md) | Immutable markdown contract specifying exact JSON output format |
| **Single Repair Loop** | [`services/enrichment.py`](file:///home/jmomoh/FlyRank%20AI/flyrank-backend-ai-engineering/BE-01-crud-api/services/enrichment.py#L95-L135) | Catches validation errors and executes exactly 1 repair request |
| **Quarantine Log** | [`logs/quarantine.jsonl`](file:///home/jmomoh/FlyRank%20AI/flyrank-backend-ai-engineering/BE-01-crud-api/logs/quarantine.jsonl) | Records unrecoverable outputs with timestamp and Pydantic trace |
| **12-Second Timeout & Retries** | [`services/enrichment.py`](file:///home/jmomoh/FlyRank%20AI/flyrank-backend-ai-engineering/BE-01-crud-api/services/enrichment.py#L60-L90) | `httpx.Timeout(12.0)`, exponential backoff on 429 & 5xx only |
| **Emergency Kill Switch** | [`main.py`](file:///home/jmomoh/FlyRank%20AI/flyrank-backend-ai-engineering/BE-01-crud-api/main.py#L290-L305) | `LLM_ENABLED=false` returns deterministic fallback |
| **Automated Eval Suite** | [`evals/run_eval.py`](file:///home/jmomoh/FlyRank%20AI/flyrank-backend-ai-engineering/BE-01-crud-api/evals/run_eval.py) | **8/8 (100%)** automated passing score across edge cases |
