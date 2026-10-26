#!/usr/bin/env python3
"""
BE-05 (Assignment A9): The Polite Scraper
Stages 1-6 + Part 4 Extras:
- Polite HTTP fetching with User-Agent, 10s timeout, >=500ms rate limit, smart retry, and local disk cache
- Multi-page catalogue discovery (3 pages, 60 unique book URLs) via urllib.parse.urljoin
- Full book detail extraction (8 raw fields)
- Price normalization ("£51.77" -> 51.77) & strict Pydantic schema validation
- Fault tolerance (per-page try/except isolation + 1 injected broken URL test)
- Extras: CSV export (`output/books.csv`) and SHA-256 HTML change detection (`output/page-hashes.json`)
"""

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
from typing import Any, Dict, List, Tuple
from fetcher import FetchError, PoliteFetcher
from parser import (
    book_url_to_cache_filename,
    parse_book_detail_page,
    parse_catalogue_page,
)
from schemas import validate_and_deduplicate_records

SCRAPER_ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = SCRAPER_ROOT / "cache"
OUTPUT_DIR = SCRAPER_ROOT / "output"
START_PAGE_URL = "https://books.toscrape.com/catalogue/page-1.html"
MAX_CATALOGUE_PAGES = 3
BROKEN_TEST_URL = "https://books.toscrape.com/catalogue/broken-book_9999/index.html"

CSV_COLUMNS = [
    "title",
    "product_url",
    "price_gbp",
    "availability_text",
    "rating_text",
    "description",
    "source_page",
    "fetched_at",
]


def compute_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def discover_catalogue_books(
    fetcher: PoliteFetcher,
    page_hashes: Dict[str, str],
    start_url: str = START_PAGE_URL,
    max_pages: int = MAX_CATALOGUE_PAGES,
) -> Tuple[int, int, List[Tuple[str, str]], List[Dict[str, Any]]]:
    """
    Walk up to `max_pages` catalogue pages starting at `start_url` by following the
    page's 'next' link. Logs and records any failed catalogue page without crashing.
    """
    current_url: str | None = start_url
    catalogue_pages = 0
    total_discovered = 0
    seen_urls: Dict[str, str] = {}
    failed_pages: List[Dict[str, Any]] = []

    while current_url and catalogue_pages < max_pages:
        catalogue_pages += 1
        cache_name = f"catalogue-page-{catalogue_pages}.html"
        try:
            html, _ = fetcher.fetch_or_cache(current_url, cache_name, verbose=True)
            page_hashes[current_url] = compute_sha256(html)
            book_urls, next_url = parse_catalogue_page(html, current_url)
            total_discovered += len(book_urls)
            for book_url in book_urls:
                if book_url not in seen_urls:
                    seen_urls[book_url] = current_url
            current_url = next_url
        except Exception as exc:
            print(f"ERROR     | Failed catalogue page {current_url}: {exc}")
            failed_pages.append(
                {
                    "url": current_url,
                    "stage": "catalogue_discovery",
                    "reason": str(exc),
                }
            )
            break

    unique_pairs = list(seen_urls.items())
    return catalogue_pages, total_discovered, unique_pairs, failed_pages


def extract_all_raw_records(
    fetcher: PoliteFetcher,
    book_and_source_pairs: List[Tuple[str, str]],
    page_hashes: Dict[str, str],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Fetch (or read from cache) each book detail page and extract its 8-field raw record.
    Any broken page is logged and skipped so one bad page never kills the run.
    """
    raw_records: List[Dict[str, Any]] = []
    failed_pages: List[Dict[str, Any]] = []

    for book_url, source_page in book_and_source_pairs:
        cache_rel = book_url_to_cache_filename(book_url)
        try:
            html, _ = fetcher.fetch_or_cache(book_url, cache_rel, verbose=True)
            page_hashes[book_url] = compute_sha256(html)
            record = parse_book_detail_page(html, product_url=book_url, source_page=source_page)
            raw_records.append(record)
        except (FetchError, ValueError, Exception) as exc:
            print(f"SKIP      | Broken book page skipped: {book_url} | reason={exc}")
            failed_pages.append(
                {
                    "url": book_url,
                    "source_page": source_page,
                    "stage": "detail_extraction",
                    "reason": str(exc),
                }
            )

    return raw_records, failed_pages


def evaluate_change_detection(
    output_dir: Path, current_hashes: Dict[str, str]
) -> Tuple[int, int]:
    """
    Compare current SHA-256 HTML hashes against `output/page-hashes.json` from the previous run.
    Returns (changed_or_new_pages, unchanged_pages).
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    hashes_path = output_dir / "page-hashes.json"
    previous_hashes: Dict[str, str] = {}

    if hashes_path.is_file():
        try:
            loaded = json.loads(hashes_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                previous_hashes = {str(k): str(v) for k, v in loaded.items()}
        except json.JSONDecodeError:
            pass

    changed_pages = 0
    unchanged_pages = 0
    for url, sha in current_hashes.items():
        if previous_hashes.get(url) == sha:
            unchanged_pages += 1
        else:
            changed_pages += 1

    hashes_path.write_text(
        json.dumps(current_hashes, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return changed_pages, unchanged_pages


def write_csv_export(csv_path: Path, books: List[Dict[str, Any]]) -> None:
    """Write validated book records to `output/books.csv` for Excel/Google Sheets."""
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for book in books:
            writer.writerow({col: book.get(col) for col in CSV_COLUMNS})


def write_idempotent_outputs(
    output_dir: Path,
    valid_records: List[Dict[str, Any]],
    error_records: List[Dict[str, Any]],
    run_report: Dict[str, Any],
) -> Tuple[Path, Path, Path, Path, int]:
    """
    Write `output/books.json`, `output/books.csv`, `output/errors.json`, and `output/run-report.json`.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    books_path = output_dir / "books.json"
    csv_path = output_dir / "books.csv"
    errors_path = output_dir / "errors.json"
    report_path = output_dir / "run-report.json"

    merged_by_url: Dict[str, Dict[str, Any]] = {}
    if books_path.is_file():
        try:
            existing = json.loads(books_path.read_text(encoding="utf-8"))
            if isinstance(existing, list):
                for item in existing:
                    if isinstance(item, dict) and item.get("product_url"):
                        merged_by_url[str(item["product_url"])] = item
        except json.JSONDecodeError:
            pass

    for record in valid_records:
        merged_by_url[record["product_url"]] = record

    final_books = list(merged_by_url.values())
    books_path.write_text(json.dumps(final_books, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_csv_export(csv_path, final_books)
    errors_path.write_text(json.dumps(error_records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    report_path.write_text(json.dumps(run_report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return books_path, csv_path, errors_path, report_path, len(final_books)


def run_pipeline(inject_broken_url: bool = True) -> Dict[str, Any]:
    start_dt = datetime.now(timezone.utc)
    start_monotonic = time.monotonic()

    fetcher = PoliteFetcher(cache_dir=CACHE_DIR)
    page_hashes: Dict[str, str] = {}

    catalogue_pages, discovered, unique_pairs, cat_failures = discover_catalogue_books(
        fetcher, page_hashes=page_hashes
    )

    if inject_broken_url:
        unique_pairs.append((BROKEN_TEST_URL, START_PAGE_URL))

    raw_records, detail_failures = extract_all_raw_records(
        fetcher, unique_pairs, page_hashes=page_hashes
    )
    all_failed_pages = cat_failures + detail_failures

    valid_records, validation_errors = validate_and_deduplicate_records(raw_records)
    changed_pages, unchanged_pages = evaluate_change_detection(OUTPUT_DIR, page_hashes)
    duration_seconds = round(time.monotonic() - start_monotonic, 3)

    run_report: Dict[str, Any] = {
        "start_time": start_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "duration_seconds": duration_seconds,
        "pages_fetched": fetcher.pages_fetched,
        "cache_hits": fetcher.cache_hits,
        "valid_records": len(valid_records),
        "invalid_records": len(validation_errors),
        "failed_pages": len(all_failed_pages),
        "changed_pages": changed_pages,
        "unchanged_pages": unchanged_pages,
    }

    combined_errors = validation_errors + [
        {
            "product_url": fp["url"],
            "source_page": fp.get("source_page"),
            "reason": fp["reason"],
            "stage": fp["stage"],
        }
        for fp in all_failed_pages
    ]

    books_path, csv_path, errors_path, report_path, stored_count = write_idempotent_outputs(
        OUTPUT_DIR, valid_records, combined_errors, run_report
    )

    print("\n--- RUN REPORT ---")
    print(json.dumps(run_report, indent=2))
    print(
        f"catalogue_pages={catalogue_pages}, "
        f"discovered={discovered}, "
        f"stored_in_books_json={stored_count}, "
        f"csv={csv_path}, "
        f"report={report_path}"
    )
    return run_report


def main() -> None:
    parser = argparse.ArgumentParser(description="BE-05 Polite Book Scraper")
    parser.add_argument(
        "--no-broken-url",
        action="store_true",
        help="Disable injecting the test broken URL (https://books.toscrape.com/catalogue/broken-book_9999/index.html)",
    )
    args = parser.parse_args()
    run_pipeline(inject_broken_url=not args.no_broken_url)


if __name__ == "__main__":
    main()
