"""
HTML Parser for Catalogue Pages & Book Detail Pages (Stages 2 and 3).
- Uses BeautifulSoup and urllib.parse.urljoin (never string concatenation).
- Extracts book detail links and the 'next' pagination link from catalogue pages.
- Extracts raw 8-field book records from individual book detail pages.
"""

from datetime import datetime, timezone
import re
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

STAR_RATING_WORDS = {"One", "Two", "Three", "Four", "Five"}


def parse_catalogue_page(html: str, page_url: str) -> Tuple[List[str], Optional[str]]:
    """
    Parse one catalogue listing page.

    Returns:
        (book_urls, next_page_url)
        - book_urls: list of full canonical https:// URLs for each book on the page.
        - next_page_url: full URL of the next catalogue page, or None if no next link exists.
    """
    soup = BeautifulSoup(html, "html.parser")
    book_urls: List[str] = []

    for pod in soup.select("article.product_pod"):
        link_tag = pod.select_one("h3 a")
        if link_tag and link_tag.get("href"):
            full_book_url = urljoin(page_url, str(link_tag["href"]).strip())
            book_urls.append(full_book_url)

    next_tag = soup.select_one("ul.pager li.next a")
    next_page_url: Optional[str] = None
    if next_tag and next_tag.get("href"):
        next_page_url = urljoin(page_url, str(next_tag["href"]).strip())

    return book_urls, next_page_url


def book_url_to_cache_filename(book_url: str) -> str:
    """
    Convert a book detail URL like
    'https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html'
    into a deterministic relative cache path 'books/a-light-in-the-attic_1000.html'.
    """
    parsed = urlparse(book_url)
    parts = [p for p in parsed.path.split("/") if p and p != "index.html"]
    slug = parts[-1] if parts else "unknown-book"
    safe_slug = re.sub(r"[^a-zA-Z0-9._-]", "_", slug)
    return f"books/{safe_slug}.html"


def parse_book_detail_page(
    html: str,
    product_url: str,
    source_page: str,
    fetched_at: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Parse a book detail page (`article.product_page`) into the raw 8-field record:
      - title
      - product_url
      - price_text
      - availability_text
      - rating_text
      - description (None if missing)
      - source_page
      - fetched_at (ISO-8601 UTC timestamp ending with 'Z')
    """
    soup = BeautifulSoup(html, "html.parser")
    article = soup.select_one("article.product_page")
    if article is None:
        raise ValueError(f"Missing article.product_page in {product_url}")

    product_main = article.select_one("div.product_main") or article

    title_tag = product_main.select_one("h1")
    title = title_tag.get_text(strip=True) if title_tag else ""

    price_tag = product_main.select_one("p.price_color")
    price_text = price_tag.get_text(strip=True) if price_tag else ""

    avail_tag = product_main.select_one("p.instock.availability") or product_main.select_one("p.availability")
    availability_text = " ".join(avail_tag.get_text(strip=True).split()) if avail_tag else ""

    rating_text = ""
    rating_tag = product_main.select_one("p.star-rating")
    if rating_tag:
        classes = rating_tag.get("class") or []
        if isinstance(classes, str):
            classes = classes.split()
        for cls in classes:
            if cls in STAR_RATING_WORDS:
                rating_text = cls
                break

    description: Optional[str] = None
    desc_header = article.select_one("#product_description")
    if desc_header:
        desc_p = desc_header.find_next_sibling("p")
        if desc_p:
            text = desc_p.get_text(strip=True)
            description = text if text else None

    if fetched_at is None:
        fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "title": title,
        "product_url": product_url,
        "price_text": price_text,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": fetched_at,
    }
