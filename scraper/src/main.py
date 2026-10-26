#!/usr/bin/env python3
"""
BE-05 (Assignment A9): The Polite Scraper
Stage 1: Fetch once, cache once
"""

from pathlib import Path
from fetcher import PoliteFetcher

SCRAPER_ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = SCRAPER_ROOT / "cache"
START_PAGE_URL = "https://books.toscrape.com/catalogue/page-1.html"


def main() -> None:
    fetcher = PoliteFetcher(cache_dir=CACHE_DIR)
    fetcher.fetch_or_cache(START_PAGE_URL, "catalogue-page-1.html", verbose=True)


if __name__ == "__main__":
    main()
