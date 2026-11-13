# BE-S5 Workshop: Scraping in Practice — From Messy HTML to Clean Data

## Session details

- **Track:** Backend AI Engineering
- **Date:** August 11, 2026, 3:30 PM
- **Format:** Code review
- **Portal duration:** 80 minutes
- **Recording:** [How Websites Really Work — Taking Pages Apart with Web Scraping](https://youtu.be/aQZKJOqrg2Q) (YouTube player metadata reports 51:11)
- **Paired assignment resource:** [The Polite Scraper](../scraper/README.md)
- **Presentation:** `Web scraping in practice - Presentation_8.html`, downloaded from the logged-in FlyRank portal and reviewed for this note.

## The main idea

A scraper is another web client: it requests a page, reads the response with code, and keeps records. The session uses scraping to teach how the web works, not to imply every project needs a scraper. Before writing a parser, determine where the needed data lives, whether access is allowed, and what the response tells the client to do next.

The lecture frames the work as **fetch → extract → normalize → validate → store → report**. A request returning `200 OK` is not proof that a scrape succeeded: a changed selector can produce zero records every night without causing an HTTP error. Validation and run reporting make that failure visible.

## Find the data before choosing a tool

The slides identify four places a page's data can live, ordered from simplest to most expensive to collect:

1. **Initial HTML:** the server response already contains the value. Inspect with View Source (`Ctrl+U`); use one HTTP request and an HTML parser.
2. **Embedded JSON:** data is inside a script tag, for example JSON-LD, `var data = [...]`, or `__NEXT_DATA__`. Fetch the page and parse the JSON.
3. **The page's own endpoint:** JavaScript requests the data from a URL, often as JSON. Use DevTools Network → Fetch/XHR to find the request and inspect its response.
4. **Rendered DOM only:** the value appears only after JavaScript runs. Use a real browser only when the first three sources do not contain it, or permitted interaction/login is required.

View Source shows what the server sent; the Elements panel shows the DOM after JavaScript ran. A selector copied from Elements may not match the original response. The lecture's triage is: (1) check initial HTML, (2) check script-tag JSON, (3) check Fetch/XHR requests. The first “yes” is the cheapest correct approach. If all three are “no”, consider browser automation.

For the Network Panel demo, filter to Fetch/XHR, inspect a request, scroll to trigger another request, and follow the server's pagination signal. The slides recommend “Copy as cURL” to understand and reproduce a request when permitted.

## Permission, safety, and polite requests

The presentation says several rule sets may apply—site terms, copyright, computer-access rules, and privacy law—and explicitly says the session is not legal advice. Its practical rule is to ask “may I?” before “how do I?”:

- A public practice sandbox built for scraping is appropriate for bounded practice; still rate-limit requests.
- A public page is not automatically free to collect. Check terms and minimize collection.
- Login/paywall content requires an authorized account and explicit approval.
- Personal data such as names, photos, or employers is high risk; stop and get advice.
- A 403, challenge, or hard limit means stop. Do not copy browser headers to evade a block.
- `robots.txt` is a machine-readable request: read and respect it, but do not mistake it for either a law or a permission slip.
- Tokens are secrets. Never hardcode, paste, or commit them; rotate a token exposed in Git history.

## Pagination, extraction, and data quality

The slides distinguish common pagination schemes:

- **Page number:** follow the page parameter, while recognizing that records may shift between pages.
- **Offset and limit:** use the total/stop condition; do not assume a fixed page count.
- **Cursor:** send the opaque cursor back unchanged; never invent one.

For all three, obey the response's stop signal—such as `has_next`, `next`, or `has_more`—rather than hard-coding a page count.

Normalize scraped values into typed fields while retaining their original text and provenance. Examples in the deck include converting `£51.77` to amount `51.77` plus currency `GBP`, mapping the CSS class `Three` to rating `3`, extracting stock status/count from “In stock (22 available)”, and resolving a relative `href` against its source URL. Keep raw and cleaned values together so later changes can be traced.

Validate each record before storage. Quarantine invalid rows with readable reasons while preserving valid rows; one bad row should neither crash the run nor silently enter clean data. Retry according to the failure:

| Response/failure | Guidance from the presentation |
| :--- | :--- |
| Network timeout | Retry; the request may be sound and the connection transient. |
| `429` | Wait and obey `Retry-After`, which may be seconds or an HTTP date. |
| `500` / `503` | Retry with growing pauses, such as 1s, 2s, 4s. |
| `404` | Do not retry; the resource is not there. |
| `401` / `403` | Stop; do not hammer or evade the restriction. |

The lecture recommends monitoring record count, missing-field rate, schema failures, and freshness. Track “last run” separately from “last successful run”. Make reruns idempotent by merging on a stable identifier, such as a canonical URL, rather than a display name.

## When browser automation is justified

The presentation compares plain HTTP requests with Playwright, Puppeteer, and Selenium. A browser runs JavaScript and can scroll/click, but costs more memory and time per page and can leave crashed tabs or zombie processes. Choose it when the data truly exists only after JavaScript execution, when permitted logged-in interaction is required, or for UI testing. If using it, begin with one or two workers, measure, and block unnecessary images/fonts/analytics. Otherwise use the simpler HTTP request path. The slides recommend Playwright for learners who need a starting point.

## Lecture assignment map and this repository's scope

The presentation maps its lesson to these stages: Stage 0, inspect three pages without code; Stage 1, collect 60 Books to Scrape records with provenance; Stage 2, normalize/validate and intentionally break a validator; Stage 3, find the Quotes to Scrape endpoint behind infinite scroll and collect 100 quotes; Stage 4, add polite retries, idempotence, and a run report; Stage 5, publish a repo another person can run; plus an optional AI rematch.

This repository's [BE-05 implementation guide](../scraper/README.md) documents a narrower/different slice: it collects 60 books from three **static, paginated Books to Scrape catalogue pages**, including detail pages, validation, caching, failure handling, and reports. It uses the catalogue's actual next-page link. It does **not** implement the lecture's Quotes to Scrape endpoint/infinite-scroll exercise or the optional AI rematch. Do not treat the presence of the workshop notes as evidence that every lecture assignment stage was completed. The scraper README remains the canonical source for what this implementation does and its run instructions/evidence.

## Recording chapters

- [0:00 — Intro and why scraping](https://youtu.be/aQZKJOqrg2Q?t=0)
- [4:02 — Is scraping legal? The grey area](https://youtu.be/aQZKJOqrg2Q?t=242)
- [6:56 — What a scraper is and the pipeline](https://youtu.be/aQZKJOqrg2Q?t=416)
- [11:43 — Classify the target before writing code](https://youtu.be/aQZKJOqrg2Q?t=703)
- [14:13 — Four places data lives on a page](https://youtu.be/aQZKJOqrg2Q?t=853)
- [20:22 — Find a hidden API in the Network panel](https://youtu.be/aQZKJOqrg2Q?t=1222)
- [22:13 — Pagination and its stop rule](https://youtu.be/aQZKJOqrg2Q?t=1333)
- [26:16 — Permission, security, and secrets](https://youtu.be/aQZKJOqrg2Q?t=1576)
- [31:15 — HTTP versus browser automation](https://youtu.be/aQZKJOqrg2Q?t=1875)
- [36:09 — Normalize, validate, status codes, and the silent zero](https://youtu.be/aQZKJOqrg2Q?t=2169)
- [49:02 — Assignment and wrap-up](https://youtu.be/aQZKJOqrg2Q?t=2942)

## Sources and limits

- [FlyRank portal event page](https://internship.flyrank.ai/intern/events/be-s5) (login may be required) — its attached Presentation_8 HTML deck contains slide content and instructor speaker notes. The user supplied the downloaded attachment for this review; it is not copied into this repository.
- [FlyRank recording and description](https://youtu.be/aQZKJOqrg2Q) — public description and chapter markers.
- [`The Polite Scraper` implementation guide](../scraper/README.md) — the project compared with the lecture's assignment map.

This is a structured summary of the presentation, its embedded speaker notes, the portal description, and recording chapters—not a verbatim transcript of the video. YouTube caption retrieval returned rate limits/empty responses during research, so spoken material outside the deck and public description has not been transcribed or independently verified.
