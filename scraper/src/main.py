#!/usr/bin/env python3
"""
BE-05 (Assignment A9): The Polite Scraper
Stage 3: Extract the raw records (visit all 60 book detail pages politely, cache each, extract 8 raw fields)
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

SCRAPER_ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = SCRAPER_ROOT / "cache"
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
        html, _ = fetcher.fetch_or_cache(current_url, cache_name, verbose=True)
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
        html, _ = fetcher.fetch_or_cache(book_url, cache_rel, verbose=True)
        record = parse_book_detail_page(html, product_url=book_url, source_page=source_page)
        raw_records.append(record)
    return raw_records


def main() -> None:
    fetcher = PoliteFetcher(cache_dir=CACHE_DIR)
    catalogue_pages, discovered, unique_pairs = discover_catalogue_books(fetcher)
    raw_records = extract_all_raw_records(fetcher, unique_pairs)

    if raw_records:
        print("\n--- SAMPLE RAW RECORD (1 of 60) ---")
        print(json.dumps(raw_records[0], indent=2, ensure_ascii=False))

    print(
        f"\ncatalogue_pages={catalogue_pages}, "
        f"discovered={discovered}, "
        f"unique_urls={len(unique_pairs)}, "
        f"detail_pages={len(raw_records)}"
    )


if __name__ == "__main__":
    main()
