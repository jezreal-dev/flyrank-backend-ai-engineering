"""
HTML Parser for Catalogue Pages & Book Detail Pages (Stages 2 and 3).
- Uses BeautifulSoup and urllib.parse.urljoin (never string concatenation).
- Extracts book detail links and the 'next' pagination link from catalogue pages.
"""

from typing import List, Optional, Tuple
from urllib.parse import urljoin
from bs4 import BeautifulSoup


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
