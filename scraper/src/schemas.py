"""
Stage 4: Normalization & Pydantic Schema Validation.
- Converts raw `price_text` (e.g. "£51.77") into numeric `price_gbp` (float > 0).
- Validates every normalized record against the strict BookRecord schema.
- Separates valid records (`output/books.json`) from invalid records (`output/errors.json`).
"""

from datetime import datetime
import re
from typing import Any, Dict, List, Literal, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field, field_validator

ValidRating = Literal["One", "Two", "Three", "Four", "Five"]


class BookRecord(BaseModel):
    """Strict schema for a cleaned, validated book record."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=1)
    product_url: str = Field(..., min_length=1)
    price_gbp: float = Field(..., gt=0)
    availability_text: str = Field(..., min_length=1)
    rating_text: ValidRating
    description: Optional[str] = None
    source_page: str = Field(..., min_length=1)
    fetched_at: str = Field(..., min_length=1)

    @field_validator("title", "availability_text")
    @classmethod
    def must_not_be_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Field must be a non-empty string")
        return cleaned

    @field_validator("product_url", "source_page")
    @classmethod
    def must_start_with_https(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned.startswith("https://"):
            raise ValueError(f"URL must start with https:// (got '{cleaned}')")
        return cleaned

    @field_validator("fetched_at")
    @classmethod
    def must_be_valid_iso8601(cls, value: str) -> str:
        cleaned = value.strip()
        # Accept trailing 'Z' as UTC ISO-8601
        iso_candidate = cleaned[:-1] + "+00:00" if cleaned.endswith("Z") else cleaned
        try:
            datetime.fromisoformat(iso_candidate)
        except ValueError as exc:
            raise ValueError(f"Invalid ISO-8601 timestamp '{cleaned}'") from exc
        return cleaned


def parse_price_gbp(price_text: str) -> float:
    """
    Turn a messy price string like '£51.77' or 'Â£51.77' into a float 51.77.
    Raises ValueError if no positive numeric price can be parsed.
    """
    if not isinstance(price_text, str):
        raise ValueError(f"Expected string price_text, got {type(price_text).__name__}")
    cleaned = price_text.replace("Â", "").replace("£", "").replace(",", "").strip()
    match = re.fullmatch(r"\d+(?:\.\d+)?", cleaned)
    if not match:
        raise ValueError(f"Cannot parse numeric GBP price from '{price_text}'")
    value = round(float(cleaned), 2)
    if value <= 0:
        raise ValueError(f"Price must be > 0, got {value}")
    return value


def normalize_raw_record(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform a raw Stage 3 record into a normalized candidate dict for BookRecord validation.
    """
    price_gbp = parse_price_gbp(str(raw.get("price_text", "")))
    desc = raw.get("description")
    if isinstance(desc, str):
        desc = desc.strip() or None

    return {
        "title": str(raw.get("title", "")).strip(),
        "product_url": str(raw.get("product_url", "")).strip(),
        "price_gbp": price_gbp,
        "availability_text": " ".join(str(raw.get("availability_text", "")).split()),
        "rating_text": str(raw.get("rating_text", "")).strip(),
        "description": desc,
        "source_page": str(raw.get("source_page", "")).strip(),
        "fetched_at": str(raw.get("fetched_at", "")).strip(),
    }


def validate_and_deduplicate_records(
    raw_records: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Normalize, validate, and deduplicate raw records by canonical `product_url`.

    Returns:
        (valid_records_list, error_records_list)
        - Preserves discovery order while ensuring idempotency (1 record per canonical product_url).
    """
    valid_by_url: Dict[str, Dict[str, Any]] = {}
    errors: List[Dict[str, Any]] = []

    for raw in raw_records:
        try:
            normalized = normalize_raw_record(raw)
            validated = BookRecord.model_validate(normalized)
            record_dict = validated.model_dump()
            # Idempotent deduplication keyed by canonical product_url
            valid_by_url[record_dict["product_url"]] = record_dict
        except Exception as exc:
            errors.append(
                {
                    "product_url": raw.get("product_url"),
                    "source_page": raw.get("source_page"),
                    "reason": str(exc),
                    "raw_record": raw,
                }
            )

    return list(valid_by_url.values()), errors
