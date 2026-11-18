# Week 6 Workshop: When the Request Can't Wait — Background Jobs & Durable Workflows

## Session details

- **Track:** Backend AI Engineering
- **Portal date:** August 21, 2026, 1:30 PM (Africa/Lagos) · 2:30 PM (Europe/Sarajevo)
- **Portal duration:** 90 minutes (Recording length: ~58 minutes)
- **Recording:** [When the request can't wait: background jobs & durable workflows](https://www.youtube.com/watch?v=j4QWa9wJbi4)
- **Raw transcript:** [`Week 6/W6-event-background-jobs-durable-workflows-transcript.txt`](../../Week%206/W6-event-background-jobs-durable-workflows-transcript.txt) (1,212 timestamped segments extracted via `youtube-transcript-api`)
- **Transcript note:** Automatic speech-recognition errors in the raw captions were verified and corrected against standard backend terminology (for example, *"injust"* → **Inngest**, *"4 to 9"* → **`429`**, *"403 service down"* → **`503`**, *"event plug"* → **event log**).

---

## 1. The Core Problem: The 40-Second Handler

Short, deterministic work—reading a task list, checking a password, fetching a single database row—finishes in milliseconds and belongs inside a normal synchronous HTTP request.

Slow, flaky, or heavy work breaks the request-response model:
- Calling an LLM (especially reasoning models that take 30–60+ seconds)
- Building a PDF report or bulk export
- Resizing images/videos or running bulk imports
- Sending batches of emails or triggering downstream webhooks

### The Timeout & Double-Billing Trap
When a user clicks **"Generate Report"** and your synchronous handler runs a 40-second AI call behind a host with a 30-second HTTP timeout (such as Vercel):
1. At second 30, the host cuts the HTTP connection and returns a timeout error to the user.
2. **Nothing tells the AI provider to stop.** The model keeps generating tokens, finishes cleanly at second 40, and sends its answer into a dead socket.
3. You still **pay for the tokens**, receive zero output, and the frustrated user clicks the button a second time—triggering a **second billed request**.

*(Alternative mitigations exist depending on the use case—streaming responses, WebSockets, self-hosting with longer timeouts, or provider async/batch APIs—but background jobs are the foundational, general-purpose backend pattern.)*

---

## 2. Accept Fast, Work Later: Jobs, Queues, Workers & Polling

Instead of performing slow work inside the HTTP handler, decouple acceptance from execution using three pieces:

| Component | Role | Mental Model |
| :--- | :--- | :--- |
| **Job** | A record of work to be done (`{ id, topic }`) | An order slip (data, not the action itself) |
| **Queue** | Ordered storage holding pending jobs (often FIFO) | The line keeping tickets safe until picked up |
| **Worker** | Separate background process executing job handlers | The cook pulling the next ticket and doing the work |

### The `202 Accepted` + Polling HTTP Pattern
```text
Client                    API Server                   Queue / Worker
  │                           │                              │
  ├── POST /reports ─────────>│ (1) Save order: "pending"    │
  │                           │ (2) Enqueue event/job ──────>│
  │<── 202 Accepted {id: 42} ─┤ (No slow work done here!)    │
  │                           │                              ├─ Worker picks up job
  ├── GET /reports/42 ───────>│ ──> { status: "pending" }    │  (runs in separate process)
  ├── GET /reports/42 ───────>│ ──> { status: "pending" }    │
  │                           │                              ├─ Saves final result: "done"
  ├── GET /reports/42 ───────>│ ──> 200 OK { status: "done" }│
```

- **Polling** (`GET /reports/{id}` repeatedly until `done`) may feel simple, but as the lecture emphasizes: *"it works, and half the internet runs on it."*
- **Three ways jobs enter a queue:**
  1. **Your own API endpoint** (e.g., `POST /reports` emitting `inngest.send({ name: "report/requested", data: { id, topic } })`)
  2. **A schedule** (Cron jobs)
  3. **Webhooks** (another system calling your URL when an external event occurs)

---

## 3. Scheduled Work: Cron Jobs

When work must run on a clock rather than on a user click (daily reports, billing reminders, nightly data syncs, Sunday cleanups), use a **Cron expression** (*Chronos* = time).

The universal 5-field format (`minute  hour  day-of-month  month  day-of-week`, where `0` = Sunday, `1` = Monday):

| Cron Expression | Meaning | Common Use Case |
| :--- | :--- | :--- |
| `* * * * *` | Every minute | Diagnostics (rarely needed in production) |
| `*/15 * * * *` | Every 15 minutes | Frequent polling or sync checks |
| `0 8 * * *` | Every day at 08:00 | Daily digest emails |
| `0 9 * * 1` | Every Monday at 09:00 | Weekly summary reports |
| `0 22 * * 0` | Every Sunday at 22:00 | Weekly database cleanup |
| `0 7 1 * *` | 1st of every month at 07:00 | Monthly billing / invoices |

**Libraries demonstrated:** `node-cron` (JavaScript), `APScheduler` (Python), and built-in scheduled triggers in **Inngest**.

---

## 4. The Production Worker Resilience Kit

1. **Retries with Backoff:**
   - Do not hammer a failing downstream server immediately. Grow the delay between attempts (e.g., retry after 5s, then 30s) because *"a struggling service needs air."*
   - Always bound retry counts explicitly in code (e.g., `retries: 2`).
2. **Retry Only the Right Errors:**
   - **Retry:** `503` / `5xx` (server errors), `429` (Too Many Requests / rate limit), network drops, timeouts.
   - **Never Retry:** `400` (Bad Request), invalid payloads, or non-existent IDs. Retrying broken input produces the exact same error every time.
3. **Concurrency Limits:**
   - Explicitly limit how many jobs run simultaneously so traffic spikes or repeated user clicks cannot overwhelm your server or exhaust API quotas.
4. **Failure Alerting & Separate Process Visibility:**
   - Because workers run in a separate terminal/process away from the user's browser, structured logging and alerting on exhausted retries are mandatory so failures do not go silent.

---

## 5. Idempotency: Assume Your Job Will Run Twice

> *"There are only two hard problems in distributed systems: (1) exactly-once delivery, (2) guaranteed message ordering, and (1) exactly-once delivery."*

**Why duplicate runs happen:** A worker finishes sending an email or charging a card and crashes **1 millisecond** before reporting `done` back to the queue. From the queue's perspective, the job failed—so it retries it. Production queues provide **at-least-once** delivery, not exactly-once.

- **Idempotent example:** An **elevator button**—pressing it 10 times still summons one elevator.
- **Non-idempotent example:** An **Add to Cart button**—pressing it 10 times adds 10 items.

### Three Practical Idempotency Techniques
1. **Check First:** The first line of the job checks whether the report/email is already marked `done`; if yes, exit immediately.
2. **One Unique Key Per Job:** Assign a deterministic key (e.g., `welcome-email-user-42`) backed by a database `UNIQUE` constraint so duplicates are rejected at the storage layer.
3. **Set, Don't Add:** Design updates as absolute assignments (`SET status = 'paid'`, safe to repeat) rather than relative increments (`ADD 10 points`, dangerous to repeat).

---

## 6. Durable Workflows & Checkpointing for AI Pipelines

AI calls belong in background jobs for three reasons:
1. **Slow:** Reasoning models routinely run 30–60+ seconds—past default web-host timeouts.
2. **Flaky:** Receiving `429` rate limits from model providers is normal load shedding, not a bug in your code; workers handle backoff cleanly.
3. **Expensive:** Every token costs real money; crashed requests that silently re-run from scratch burn budget.

### Why Checkpointing Matters
Real production AI work is rarely a single prompt call—it is a multi-step pipeline (for example: *clean text → summarize → extract action items → draft email*).

Without durable workflows, if Step 4 fails or the worker is killed mid-job, a plain retry re-executes Steps 1, 2, and 3—wasting latency and paying for the same LLM calls twice.

With **durable step checkpointing** (demonstrated using **Inngest** `step.run` / `step.sleep`):
- Each completed step persists its output as a checkpoint.
- If the worker crashes or is killed mid-job and restarts, the workflow engine replays completed steps from stored state and **resumes exactly at the failed step** without redoing earlier work.

---

## 7. Production Ecosystem Map

| Tool / Concept | What It Actually Is | When You Hear About It |
| :--- | :--- | :--- |
| **Redis** | Ultra-fast in-memory data store | Where classic queue libraries (**BullMQ**, **Celery**, **Sidekiq**) store their job lists. |
| **RabbitMQ** | Dedicated message broker | Built specifically to receive messages, route them to workers, and track acknowledgements. |
| **Kafka** | Distributed append-only **event log** | Massive scale (e.g., Slack placing Kafka in front of 1.4B jobs/day). *One-line difference:* a queue hands a job out and deletes it; a log writes events in order and keeps them so multiple readers can replay at their own speed. |
| **Inngest** | High-level durable workflow & queue platform | Simplifies event-driven steps, retries, cron triggers, and checkpointing without manually wiring Redis/brokers. |
| **Serverless / Edge Functions** | On-demand cloud compute (AWS Lambda, Supabase Edge, Cloudflare Workers, Vercel Functions) | Code wakes up, executes, and disappears—but has hard **time limits** (e.g., Lambda max 15 min; Edge functions even shorter). *Rule:* a serverless function is **where** code runs; a job system decides **when** it runs, retries it, and remembers what finished. |
| **Event-Driven Architecture** | Systems announcing events (`report/requested`) instead of tight direct calls | Decouples API handlers from background consumers, cron schedules, and webhooks. |

---

## 8. Connection to Our Backend Codebase & Next Assignment

- **Builds directly on `BE-07` ([`BE-01-crud-api`](../BE-01-crud-api/README.md)):** Our synchronous `POST /enrich` endpoint already enforces explicit timeouts (12s), bounded retries on `429`/`5xx`, and fast rejection on `400`/`401`. Moving multi-step or slow LLM enrichment behind a `202 Accepted` + worker queue with checkpoints is the exact next architectural tier.
- **Upcoming assignment preview:** The session closes by previewing the paired assignment—building your own background job (such as asynchronous PDF report generation or email delivery) with proper acceptance (`202`), polling, idempotency, and retries.
