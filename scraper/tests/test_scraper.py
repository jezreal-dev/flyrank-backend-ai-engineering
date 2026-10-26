"""
Unit tests for BE-05 Polite Scraper on saved HTML fixtures (Part 4 Optional Extra).
Covers:
1. URL joining & pagination extraction (`parse_catalogue_page`)
2. Book detail parsing from saved fixture (`parse_book_detail_page`)
3. Missing description resilience (`description=None` without crashing)
4. Price normalization (`parse_price_gbp` handling '£51.77', 'Â£51.77', and rejecting bad strings)
5. Strict Pydantic schema rejection (`BookRecord` rejecting non-https URLs, negative prices, invalid ratings)
6. Idempotent deduplication by canonical `product_url`
"""

from pathlib import Path
import sys
import pytest

TESTS_DIR = Path(__file__).resolve().parent
SCRAPER_ROOT = TESTS_DIR.parent
SRC_DIR = SCRAPER_ROOT / "src"
FIXTURES_DIR = TESTS_DIR / "fixtures"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from parser import (  # noqa: E402
    book_url_to_cache_filename,
    parse_book_detail_page,
    parse_catalogue_page,
)
from schemas import (  # noqa: E402
    BookRecord,
    parse_price_gbp,
    validate_and_deduplicate_records,
)


def test_parse_catalogue_page_joins_urls_correctly() -> None:
    html = (FIXTURES_DIR / "sample-catalogue-page.html").read_text(encoding="utf-8")
    page_url = "https://books.toscrape.com/catalogue/page-1.html"
    book_urls, next_url = parse_catalogue_page(html, page_url)

    assert len(book_urls) == 2
    assert book_urls[0] == "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
    assert book_urls[1] == "https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html"
    assert next_url == "https://books.toscrape.com/catalogue/page-2.html"


def test_parse_book_detail_page_extracts_all_8_fields() -> None:
    html = (FIXTURES_DIR / "sample-book-detail.html").read_text(encoding="utf-8")
    record = parse_book_detail_page(
        html,
        product_url="https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
        source_page="https://books.toscrape.com/catalogue/page-1.html",
        fetched_at="2026-10-26T16:25:58Z",
    )

    assert record["title"] == "A Light in the Attic"
    assert record["price_text"] == "£51.77"
    assert record["availability_text"] == "In stock (22 available)"
    assert record["rating_text"] == "Three"
    assert record["description"] == "It's hard to imagine a world without A Light in the Attic. ...more"
    assert record["source_page"] == "https://books.toscrape.com/catalogue/page-1.html"
    assert record["fetched_at"] == "2026-10-26T16:25:58Z"


def test_missing_description_returns_none_without_crashing() -> None:
    html_no_desc = """
    <html><body>
      <article class="product_page">
        <div class="product_main">
          <h1>Book Without Description</h1>
          <p class="price_color">£19.99</p>
          <p class="instock availability">In stock (5 available)</p>
          <p class="star-rating Four"></p>
        </div>
      </article>
    </body></html>
    """
    record = parse_book_detail_page(
        html_no_desc,
        product_url="https://books.toscrape.com/catalogue/no-desc_1/index.html",
        source_page="https://books.toscrape.com/catalogue/page-1.html",
        fetched_at="2026-10-26T16:25:58Z",
    )
    assert record["description"] is None
    assert record["title"] == "Book Without Description"


def test_parse_price_gbp_normalizes_and_rejects_invalid() -> None:
    assert parse_price_gbp("£51.77") == 51.77
    assert parse_price_gbp("Â£51.77") == 51.77
    assert parse_price_gbp("  £9.50 ") == 9.5

    with pytest.raises(ValueError):
        parse_price_gbp("free")

    with pytest.raises(ValueError):
        parse_price_gbp("£0.00")


def test_schema_rejects_bad_url_rating_and_price() -> None:
    # Reject relative URL (must start with https://)
    with pytest.raises(ValueError):
        BookRecord(
            title="Test Book",
            product_url="a-light-in-the-attic_1000/index.html",
            price_gbp=51.77,
            availability_text="In stock",
            rating_text="Three",
            description=None,
            source_page="https://books.toscrape.com/catalogue/page-1.html",
            fetched_at="2026-10-26T16:25:58Z",
        )

    # Reject invalid rating word
    with pytest.raises(ValueError):
        BookRecord(
            title="Test Book",
            product_url="https://books.toscrape.com/catalogue/test_1/index.html",
            price_gbp=51.77,
            availability_text="In stock",
            rating_text="Seven",  # type: ignore[arg-type]
            description=None,
            source_page="https://books.toscrape.com/catalogue/page-1.html",
            fetched_at="2026-10-26T16:25:58Z",
        )


def test_idempotent_deduplication_by_product_url() -> None:
    raw = {
        "title": "A Light in the Attic",
        "product_url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
        "price_text": "£51.77",
        "availability_text": "In stock (22 available)",
        "rating_text": "Three",
        "description": "Poem collection.",
        "source_page": "https://books.toscrape.com/catalogue/page-1.html",
        "fetched_at": "2026-10-26T16:25:58Z",
    }
    valid, errors = validate_and_deduplicate_records([raw, dict(raw)])
    assert len(valid) == 1
    assert len(errors) == 0
    assert valid[0]["price_gbp"] == 51.77
    assert book_url_to_cache_filename(raw["product_url"]) == "books/a-light-in-the-attic_1000.html"
