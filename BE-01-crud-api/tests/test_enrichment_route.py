"""Contract tests for the BE-07 stub endpoint and its input boundary."""

import pytest
from pydantic import ValidationError

from src.llm.schemas import BookEnrichmentRequest, BookEnrichmentResult


def test_request_accepts_scraper_record_fields() -> None:
    request = BookEnrichmentRequest(
        title="A Light in the Attic",
        description="A collection of poems for children.",
    )
    assert request.title == "A Light in the Attic"
    assert request.description == "A collection of poems for children."


def test_blank_description_is_treated_as_missing() -> None:
    request = BookEnrichmentRequest(title="A Book", description="   ")
    assert request.description is None


def test_output_rejects_category_outside_the_closed_list() -> None:
    with pytest.raises(ValidationError):
        BookEnrichmentResult(
            category="memoir",
            summary="A short summary.",
            quality_flags=[],
        )


def test_output_rejects_more_than_thirty_summary_words() -> None:
    with pytest.raises(ValidationError):
        BookEnrichmentResult(
            category="fiction",
            summary=" ".join(["word"] * 31),
            quality_flags=[],
        )


def test_stub_endpoint_returns_closed_schema(client) -> None:
    response = client.post(
        "/enrich",
        json={"title": "A Light in the Attic", "description": "A poetry collection."},
    )
    assert response.status_code == 200
    assert response.json() == {
        "category": "other",
        "summary": "Stub response; the language model was not called.",
        "quality_flags": ["ambiguous_category"],
    }


@pytest.mark.parametrize(
    ("payload", "field"),
    [
        ({"description": "Missing title."}, "title"),
        ({"title": "  "}, "title"),
        ({"title": 12}, "title"),
        ({"title": "A book", "description": "x" * 2001}, "description"),
        ({"title": "A book", "extra": "not allowed"}, "extra"),
    ],
)
def test_invalid_input_returns_400_with_field_name(client, payload, field) -> None:
    response = client.post("/enrich", json=payload)
    assert response.status_code == 400
    assert field in [item["field"] for item in response.json()["fields"]]


def test_live_mode_fails_cleanly_until_provider_is_wired(client, monkeypatch) -> None:
    monkeypatch.setenv("LLM_STUB", "0")
    response = client.post("/enrich", json={"title": "A Book"})
    assert response.status_code == 503
    assert "added in the next build stage" in response.json()["detail"]
