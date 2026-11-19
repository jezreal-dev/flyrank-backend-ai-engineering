# Prompt Given for AI Rematch

```text
Write a FastAPI backend that generates a weekly PDF sales report from an SQLite database of orders.
Include endpoints to generate and download the report.
```

## Observations & Pitfalls in AI-Generated Version

When prompted with a generic request, typical AI coding assistants make 5 classic production mistakes:

1. **Python-Side Aggregation instead of SQL Aggregation**:
   - The AI version queries `SELECT * FROM orders` into memory and computes revenue sums and group-bys using Python dictionaries and list comprehensions.
   - *Production impact*: On a dataset with 500,000 orders, this exhausts server memory and crashes with OOM.
   - *Our pipeline*: Pushes computation to SQLite engine with `SUM(amount)`, `strftime('%Y-%m-%d', created_at)`, and `GROUP BY ... ORDER BY ... LIMIT 5`.

2. **The Classic Page-Break Trap**:
   - The AI version generates basic HTML with default CSS. It does not set `@page { size: A4; margin: 15mm; }`, `tr { page-break-inside: avoid; }`, or `thead { display: table-header-group; }`.
   - *Production impact*: Multi-page tables get sliced horizontally right across a line of text, and subsequent pages have orphaned table headers.
   - *Our pipeline*: Applies print-specific CSS rules preventing row splits and repeating table headers on all 7 pages.

3. **Artifact Handling (Passing 20MB in JSON)**:
   - The AI version converts the PDF into a Base64 string and embeds it directly into the JSON response body (`{"filename": "report.pdf", "data": "JVBERi0xLjQK..."}`).
   - *Production impact*: Serializing large binaries into JSON inflates payload size by 33%, locks up CPU during JSON encoding, and violates REST architectural principles.
   - *Our pipeline*: Stores artifact to disk/storage and returns a lightweight metadata link (`POST /reports` -> `201 Created` + `{"file": "/reports/1/file"}`).

4. **Missing Idempotency (Ask Twice, Get Two)**:
   - The AI version generates a new file on every single click or network retry.
   - *Production impact*: If a user double-clicks or a webhook retries, the server burns CPU and disk generating duplicate reports.
   - *Our pipeline*: Re-checks existing reports generated for today and returns `200 OK` with existing ID, unless explicitly forced with `{"force": true}`.

5. **Synchronous Blocking vs. Async Job Queues**:
   - The AI version runs the entire generation loop inside the HTTP request thread.
   - *Production impact*: HTTP requests time out behind load balancers (e.g. AWS ALB 30s timeout, Cloudflare 100s timeout).
   - *Our pipeline*: Supports both synchronous generation and Inngest background event processing with `202 Accepted` + polling.
