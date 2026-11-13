# BE-S5 Workshop: Scraping in Practice — From Messy HTML to Clean Data

## Session details

- **Track:** Backend AI Engineering
- **Portal title:** Workshop: Scraping in practice — from messy HTML to clean data
- **Date:** August 11, 2026, 3:30 PM
- **Format:** Code review
- **Portal duration:** 80 minutes
- **Recording:** [How Websites Really Work — Taking Pages Apart with Web Scraping](https://youtu.be/aQZKJOqrg2Q) (YouTube player metadata reports 51:11)
- **Paired assignment:** [BE-05 — The Polite Scraper](../scraper/README.md)

The portal summary and the recording frame scraping as a way to understand how web pages deliver data: initial HTML, later network requests, pagination, HTTP responses, and browser-side rendering. The session emphasizes deciding what kind of source you have before choosing a tool. A browser automation library is useful when the page genuinely depends on JavaScript or interaction; it is unnecessary when the response already contains the data.

## Main ideas

### Inspect the source before choosing a scraper

Start by classifying the target. Check whether access is permitted, whether an official API or dataset is available, and whether the desired data appears in the initial response or arrives through later browser requests. The session demonstrates using the browser DevTools Network panel to find a hidden API response. Its chapter at 14:13 introduces a four-location framework for page data; the portal's attached HTML presentation was not available in the local project, so this note does not guess the framework's exact labels.

### Use pagination the site actually provides

Inspect the page's next-page control and follow its link. Do not assume that every site numbers pages or constructs the next URL the same way. The paired scraper applies this by parsing the catalogue's `next` link and resolving it with `urljoin`.

### Treat scraping as a pipeline

The session's pipeline is **fetch → extract → normalize → validate → store → report**. Keeping those jobs distinct helps catch silent failures: a successful HTTP response can still contain no useful records, and extracted strings can still be malformed data.

### Make requests predictable and polite

Use explicit timeouts, inspect status codes, keep request volume bounded, and isolate page failures so one broken page does not discard an entire run. Cache responses when repeated fetches are unnecessary. Select browser automation only when the content or interaction requires a browser.

### Check permission and protect the system

The session raises legal and ethical limits, permission, secrets, and the security risks involved in collecting data. For a real target, check its terms and access rules; do not treat a missing `robots.txt` as permission. Keep credentials out of scraped content and logs, and validate collected data before storing or using it.

## How BE-05 applies the lesson

| Workshop idea | Implementation in The Polite Scraper |
| :--- | :--- |
| Classify the target | `books.toscrape.com` serves the catalogue cards in static HTML, so the project uses `requests` and Beautiful Soup rather than launching Playwright or Selenium. |
| Follow pagination | `parse_catalogue_page()` extracts the actual next-page link and resolves relative URLs with `urljoin`. |
| Fetch politely | `PoliteFetcher` sets an identifying User-Agent, uses a 10-second timeout, waits at least 550 ms between live requests, retries selected transient failures once, and caches responses. |
| Extract and normalize | `parser.py` reads the book detail pages; `schemas.py` converts price text to a number and validates each `BookRecord` with Pydantic. |
| Store and report | `main.py` writes JSON/CSV records, error details, run metrics, and page hashes so a partial failure or unchanged rerun is visible. |

The implementation guide, commands, output examples, limitations, and test details live in [`scraper/README.md`](../scraper/README.md). This workshop note records the lesson and its connection to the project rather than repeating that guide.

## Recording chapters

- [0:00 — Intro and why scraping](https://youtu.be/aQZKJOqrg2Q?t=0)
- [4:02 — Legal grey area](https://youtu.be/aQZKJOqrg2Q?t=242)
- [6:56 — What a scraper is and the pipeline](https://youtu.be/aQZKJOqrg2Q?t=416)
- [11:43 — Classify the target first](https://youtu.be/aQZKJOqrg2Q?t=703)
- [14:13 — Four places data can live](https://youtu.be/aQZKJOqrg2Q?t=853)
- [20:22 — Find a hidden API in the Network panel](https://youtu.be/aQZKJOqrg2Q?t=1222)
- [22:13 — Pagination](https://youtu.be/aQZKJOqrg2Q?t=1333)
- [26:16 — Permission, security, and secrets](https://youtu.be/aQZKJOqrg2Q?t=1576)
- [31:15 — Scraping methods and browser automation tools](https://youtu.be/aQZKJOqrg2Q?t=1875)
- [36:09 — Normalize, validate, status codes, and silent zero](https://youtu.be/aQZKJOqrg2Q?t=2169)
- [49:02 — Assignment and wrap-up](https://youtu.be/aQZKJOqrg2Q?t=2942)

## Sources and limits

- [FlyRank internship schedule](https://internship.flyrank.ai/intern/schedule) — sign-in may be required; session metadata and summary were supplied from the portal by the user.
- [FlyRank recording](https://youtu.be/aQZKJOqrg2Q) — public description and chapter markers.
- [`The Polite Scraper` implementation guide](../scraper/README.md) — the paired project in this repository.

The recording page exposes a YouTube-generated caption track, but caption downloads were rate-limited during research. The portal's `Presentation_8.html` attachment was also not available outside the logged-in page. Accordingly, this is a concise summary of the available event description, recording metadata/chapters, and the implemented project—not a transcript or a claim to reproduce the presentation's exact four-part taxonomy.
