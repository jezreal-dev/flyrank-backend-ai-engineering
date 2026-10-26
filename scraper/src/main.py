#!/usr/bin/env python3
"""
BE-05 (Assignment A9): The Polite Scraper
Stage 4: Clean it, check it, store it (normalize prices, validate with Pydantic, write idempotent JSON outputs)
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple
from fetcher import PoliteFetcher
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


def discover_catalogue_books(
    fetcher: PoliteFetcher,
    start_url: str = START_PAGE_URL,
    max_pages: int = MAX_CATALOGUE_PAGES,
) -> Tuple[int, int, List[Tuple[str, str]]]:
    """
    Walk up to `max_pages` catalogue pages starting at `start_url` by following the
    page's 'next' link.
    """
    current_url: str | None = start_url
    catalogue_pages = 0
    total_discovered = 0
    seen_urls: Dict[str, str] = {}

    while current_url and catalogue_pages < max_pages:
        catalogue_pages += 1
        cache_name = f"catalogue-page-{catalogue_pages}.html"
        html, _ = fetcher.fetch_or_cache(current_url, cache_name, verbose=False)
        book_urls, next_url = parse_catalogue_page(html, current_url)
        total_discovered += len(book_urls)
        for book_url in book_urls:
            if book_url not in seen_urls:
                seen_urls[book_url] = current_url
        current_url = next_url

    unique_pairs = list(seen_urls.items())
    return catalogue_pages, total_discovered, unique_pairs


def extract_all_raw_records(
    fetcher: PoliteFetcher,
    book_and_source_pairs: List[Tuple[str, str]],
) -> List[Dict[str, Any]]:
    """
    Fetch (or read from cache) each book detail page and extract its 8-field raw record.
    """
    raw_records: List[Dict[str, Any]] = []
    for book_url, source_page in book_and_source_pairs:
        cache_rel = book_url_to_cache_filename(book_url)
        html, _ = fetcher.fetch_or_cache(book_url, cache_rel, verbose=False)
        record = parse_book_detail_page(html, product_url=book_url, source_page=source_page)
        raw_records.append(record)
    return raw_records


def write_idempotent_outputs(
    output_dir: Path,
    valid_records: List[Dict[str, Any]],
    error_records: List[Dict[str, Any]],
) -> Tuple[Path, Path, int]:
    """
    Write `output/books.json` (keyed idempotently by canonical `product_url`)
    and `output/errors.json`.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    books_path = output_dir / "books.json"
    errors_path = output_dir / "errors.json"

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
    errors_path.write_text(json.dumps(error_records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return books_path, errors_path, len(final_books)


def main() -> None:
    fetcher = PoliteFetcher(cache_dir=CACHE_DIR)
    catalogue_pages, discovered, unique_pairs = discover_catalogue_books(fetcher)
    raw_records = extract_all_raw_records(fetcher, unique_pairs)
    valid_records, error_records = validate_and_deduplicate_records(raw_records)
    books_path, errors_path, stored_count = write_idempotent_outputs(
        OUTPUT_DIR, valid_records, error_records
    )

    print(
        f"catalogue_pages={catalogue_pages}, "
        f"discovered={discovered}, "
        f"valid_records={len(valid_records)}, "
        f"invalid_records={len(error_records)}, "
        f"stored_in_books_json={stored_count}"
    )
    print(f"Wrote {books_path} and {errors_path}")


if __name__ == "__main__":
    main()
