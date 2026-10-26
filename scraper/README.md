# BE-05 (Assignment A9): The Polite Scraper

A small, polite, fault-tolerant web scraping pipeline built in **Python** (`requests`, `beautifulsoup4`, `pydantic`) that collects the first **3 catalogue pages (60 books)** from [`https://books.toscrape.com`](https://books.toscrape.com), visits every individual book detail page politely, normalizes messy HTML text like `"£51.77"` into numeric `price_gbp` (`51.77`), validates every record against a strict **Pydantic** schema, and survives broken pages without crashing.

---

## 1. Lane & Tech Stack

- **Chosen Lane**: Python (`Python 3.10+`)
- **HTTP Client**: `requests` (explicit `User-Agent`, `10.0s` timeout, explicit `UTF-8` response decoding)
- **HTML Parser**: `beautifulsoup4` (`BeautifulSoup` + `urllib.parse.urljoin`)
- **Schema Validation**: `pydantic` v2 (`BookRecord` model)
- **Testing**: `pytest` (unit tests against saved HTML fixtures)

---

## 2. Stage 0: Target Classification

| Check | Result |
| :--- | :--- |
| **Target URL** | `https://books.toscrape.com/catalogue/page-1.html` |
| **Classification** | **Static HTML** (`200 OK`, all `<article class="product_pod">` cards and `<article class="product_page">` details are rendered directly by the server in the initial HTML payload; zero client-side XHR/Fetch calls required) |
| **`robots.txt` Check** | `https://books.toscrape.com/robots.txt` returns **HTTP 404 (`no robots file found`)**. Because a missing `robots.txt` is **not** automatic permission, scraping permission comes from the explicit public sandbox notice on `toscrape.com` |
| **Login / Paywall** | **No** (public scraping sandbox) |
| **PII Collected** | **No** (fictional bookstore catalogue metadata only) |

### Why We Did NOT Need a Headless Browser (`Playwright` / `Puppeteer`)
Inspecting the raw HTTP response of `https://books.toscrape.com/catalogue/page-1.html` (`curl -s ... | grep product_pod`) shows 20 `<article class="product_pod">` elements already present in the initial server-rendered HTML, and each book detail page renders its `<h1>`, `.price_color`, `.instock.availability`, `.star-rating`, and `#product_description` statically. Launching a headless Chromium instance via Playwright or Puppeteer would waste 10–20× more CPU, RAM, and bandwidth to parse DOM nodes that plain `requests` + `BeautifulSoup` can parse in milliseconds.

---

## 3. Politeness Rules

1. **Identify Ourselves Honestly**: Every HTTP request sends:
   ```text
   User-Agent: FlyRankInternship-A9/1.0 (+https://github.com/jezreal-dev/flyrank-backend-ai-engineering)
   ```
2. **Explicit Request Timeout**: Every `requests.get()` call enforces `timeout=10.0` seconds so a hung socket never blocks the pipeline indefinitely.
3. **Strict Status Code Handling & Smart Retries**:
   - Only HTTP `200 OK` responses are cached and parsed.
   - Transient network timeouts / `ConnectionError` and `5xx` server errors are retried **at most once** after a `1.0s` wait.
   - Client errors (`404 Not Found` and `403 Forbidden`) are **never retried**—they fail fast, log the reason, and skip to the next URL.
4. **Rate Limiting (`>= 500ms` Delay)**: The fetcher enforces a minimum `550ms` (`0.55s`) pause between consecutive live network requests.
5. **Local Disk Cache (`cache/`)**: Every fetched HTML page is saved under `cache/` (`cache/catalogue-page-1.html`, `cache/books/<slug>.html`). Subsequent runs read from disk (`CACHE HIT`) with zero network traffic and `0ms` delay. `cache/` is gitignored so cached HTML never bloats the repository.

---

## 4. Install & Run Commands (Under 5 Minutes)

```bash
# 1. Navigate to the scraper directory
cd scraper

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the scraper pipeline
python src/main.py
```

Optional CLI flags:
- `python src/main.py` — Runs the full 3-page (60-book) pipeline **plus** 1 injected broken URL (`https://books.toscrape.com/catalogue/broken-book_9999/index.html`) to prove Stage 5 fault tolerance (`valid_records: 60, failed_pages: 1`).
- `python src/main.py --no-broken-url` — Runs only the 60 discovered catalogue book URLs (`valid_records: 60, failed_pages: 0`).

---

## 5. Output Files & Schema

All outputs are written to `scraper/output/`:

| File | Purpose |
| :--- | :--- |
| [`output/books.json`](output/books.json) | 60 cleaned, validated, idempotently deduplicated book records (keyed by canonical `product_url`) |
| [`output/books.csv`](output/books.csv) | Spreadsheet-ready CSV export of the 60 validated book records |
| [`output/errors.json`](output/errors.json) | Structured log of any invalid records or failed/skipped page URLs with exact error reasons |
| [`output/run-report.json`](output/run-report.json) | Machine-readable run telemetry (`start_time`, `duration_seconds`, `pages_fetched`, `cache_hits`, `valid_records`, `invalid_records`, `failed_pages`) |

### `BookRecord` Schema (`src/schemas.py`)

| Field | Type | Validation Rule |
| :--- | :--- | :--- |
| `title` | `str` | Non-empty trimmed string from the detail page `<h1>` (never the truncated `"..."` card title) |
| `product_url` | `str` | Canonical URL starting with `https://` (resolved via `urllib.parse.urljoin`) |
| `price_gbp` | `float` | Real number `> 0` parsed from `price_text` (e.g. `"£51.77"` $\rightarrow$ `51.77`) |
| `availability_text` | `str` | Non-empty trimmed availability string (e.g. `"In stock (22 available)"`) |
| `rating_text` | `Literal["One", "Two", "Three", "Four", "Five"]` | Extracted from `<p class="star-rating ...">` |
| `description` | `str \| None` | Full product description text, or `null` if missing on the page |
| `source_page` | `str` | Catalogue page URL (`https://...`) where the book was discovered |
| `fetched_at` | `str` | Valid ISO-8601 UTC timestamp (`YYYY-MM-DDTHH:MM:SSZ`) |

---

## 6. Real `run-report.json` Output

### Cold Run (Live Fetch of 3 Catalogue Pages + 60 Detail Pages + 1 Broken URL)
```json
{
  "start_time": "2026-10-26T16:25:42Z",
  "duration_seconds": 46.812,
  "pages_fetched": 63,
  "cache_hits": 0,
  "valid_records": 60,
  "invalid_records": 0,
  "failed_pages": 1
}
```

### Warm Rerun from Local Cache (Idempotency + Fault-Tolerance Verification)
```json
{
  "start_time": "2026-10-26T16:29:55Z",
  "duration_seconds": 1.639,
  "pages_fetched": 0,
  "cache_hits": 63,
  "valid_records": 60,
  "invalid_records": 0,
  "failed_pages": 1
}
```

---

## 7. Ethics Note

- **What I checked before scraping**: Before writing a single line of collection code, I inspected `https://books.toscrape.com/robots.txt` (which returned HTTP `404`) and verified on `https://toscrape.com` that the domain is an intentional public sandbox built specifically for scraping practice, requires no authentication, and contains zero personal data.
- **What I would refuse to scrape on a real site**: On a production website, I would refuse to scrape any path disallowed by `robots.txt` or Terms of Service, any endpoint behind a login wall, session cookie, or paywall, any CAPTCHA/Cloudflare-protected page, or any page containing Personally Identifiable Information (PII) such as user profiles, email addresses, phone numbers, or private messages.

---

## 8. Honest Limitation

- **What is still fragile or unfinished**:
  1. **CSS Selector Coupling**: `parse_catalogue_page()` and `parse_book_detail_page()` rely on Oscar e-commerce CSS selectors (`article.product_pod h3 a`, `ul.pager li.next a`, `article.product_page`, `#product_description + p`). If the site redesigns its template or renames classes, extraction will fail (though Pydantic validation and `errors.json` will catch it immediately instead of silently writing corrupt rows).
  2. **Cache Invalidation TTL**: Currently, cached HTML files in `cache/` persist until manually deleted (`rm -rf cache/`). In a scheduled production pipeline, cached pages should expire based on a configurable TTL (e.g., 24 hours) or HTTP `ETag` / `Last-Modified` conditional requests.
