"""BE-07 enrichment orchestration; live provider calls are added in Stage 2."""

import os

from src.llm.schemas import BookEnrichmentRequest, BookEnrichmentResult


class LiveProviderNotConfigured(RuntimeError):
    """Raised until the versioned prompt and live client are wired in Stage 2."""


def enrich_book(payload: BookEnrichmentRequest) -> BookEnrichmentResult:
    """Return a deterministic, schema-valid stub while the endpoint is built."""
    if os.getenv("LLM_STUB", "1").strip() == "1":
        return BookEnrichmentResult(
            category="other",
            summary="Stub response; the language model was not called.",
            quality_flags=["ambiguous_category"],
        )

    raise LiveProviderNotConfigured("Live model calls are added in the next build stage")
