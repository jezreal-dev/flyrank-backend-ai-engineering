#!/usr/bin/env python3
"""
BE-05 (Assignment A9): The Polite Scraper
Stage 2: Find all three pages (discover 60 unique book URLs across catalogue pages 1, 2, 3)
"""

from pathlib import Path
from typing import Dict, List, Tuple
from fetcher import PoliteFetcher
from parser import parse_catalogue_page

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

    Returns:
        (catalogue_pages_visited, total_discovered_links, unique_book_url_and_source_pairs)
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


def main() -> None:
    fetcher = PoliteFetcher(cache_dir=CACHE_DIR)
    catalogue_pages, discovered, unique_pairs = discover_catalogue_books(fetcher)
    print(
        f"catalogue_pages={catalogue_pages}, "
        f"discovered={discovered}, "
        f"unique_urls={len(unique_pairs)}"
    )


if __name__ == "__main__":
    main()
