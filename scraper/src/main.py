#!/usr/bin/env python3
"""
BE-05 (Assignment A9): The Polite Scraper
Target: https://books.toscrape.com (First 3 catalogue pages = 60 books)
Author: Jezreal Momoh
"""

BASE_URL = "https://books.toscrape.com/"
START_PAGE_URL = "https://books.toscrape.com/catalogue/page-1.html"
USER_AGENT = "FlyRankInternship-A9/1.0 (+https://github.com/jezreal-dev/flyrank-backend-ai-engineering)"


def main() -> None:
    print(f"Stage 0 Ready: Target={BASE_URL} | Scope=First 3 catalogue pages (60 books)")


if __name__ == "__main__":
    main()
