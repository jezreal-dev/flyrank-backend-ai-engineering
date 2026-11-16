"""Closed request and response contracts for the BE-07 enrichment endpoint."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

BookCategory = Literal["fiction", "nonfiction", "poetry", "comics", "other"]
QualityFlag = Literal["insufficient_text", "ambiguous_category"]


class BookEnrichmentRequest(BaseModel):
    """Only the scraped text needed for one classification decision."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str = Field(strict=True, min_length=1, max_length=200)
    description: str | None = Field(default=None, strict=True, max_length=2000)

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: str) -> str:
        if not value:
            raise ValueError("title must not be blank")
        return value

    @field_validator("description")
    @classmethod
    def blank_description_becomes_missing(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            return None
        return value


class BookEnrichmentResult(BaseModel):
    """Validated model result returned to API callers."""

    model_config = ConfigDict(extra="forbid")

    category: BookCategory
    summary: str = Field(min_length=1, max_length=300)
    quality_flags: list[QualityFlag] = Field(default_factory=list, max_length=2)

    @field_validator("summary")
    @classmethod
    def summary_must_be_short_and_nonblank(cls, value: str) -> str:
        cleaned = " ".join(value.split())
        if not cleaned:
            raise ValueError("summary must not be blank")
        if len(cleaned.split()) > 30:
            raise ValueError("summary must be at most 30 words")
        return cleaned
