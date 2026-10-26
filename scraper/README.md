# BE-05 (Assignment A9): The Polite Scraper

A polite, deterministic Python scraping pipeline that collects the first 3 catalogue pages (60 book detail pages) from the [Books to Scrape](https://books.toscrape.com) sandbox, normalizes raw prices and relative URLs, validates every record against a strict Pydantic schema, survives broken pages without crashing, and writes a transparent `run-report.json`.

---

## 1. Target Classification (Stage 0 Check)

- **Target Site**: [Books to Scrape (`https://books.toscrape.com`)](https://books.toscrape.com)
- **Why This Site Is Permitted**: Directly confirmed on [toscrape.com](https://toscrape.com) that *Books to Scrape* is an explicit public scraping sandbox built by Zyte (formerly Scrapinghub) specifically so developers can practice web scraping safely.
- **`robots.txt` Check Result**: Requested `https://books.toscrape.com/robots.txt` once (`GET` with identifying `User-Agent`). The server returned **`HTTP 404 Not Found` — no robots file found**. As required by professional scraping standards, a missing `robots.txt` file is not automatic permission; permission here comes explicitly from the site owner's sandbox notice on `toscrape.com`.
- **Collection Scope**: Strictly bounded to the **first 3 catalogue pages** (`catalogue/page-1.html`, `page-2.html`, `page-3.html`) and the **60 book detail pages** linked from those three pages.
- **Data Collected**: Public book catalogue fields only (`title`, `product_url`, `price_text`, `price_gbp`, `availability_text`, `rating_text`, `description`, `source_page`, and `fetched_at` provenance metadata). No personal data (PII), user accounts, or login-protected pages exist or are touched.
- **Why This Scope Is Appropriate**: Collecting 3 catalogue pages and 60 static HTML detail pages with a 500ms+ delay and local disk caching places negligible load on a dedicated public sandbox.

> **Mandatory Pledge**:  
> *"I will not reuse this code on another site without checking its rules and terms first."*
