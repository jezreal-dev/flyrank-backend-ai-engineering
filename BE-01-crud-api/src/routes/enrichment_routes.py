"""HTTP route for enriching one scraped book record."""

from fastapi import APIRouter, HTTPException

from src.llm.schemas import BookEnrichmentRequest, BookEnrichmentResult
from src.llm.provider import ProviderConfigurationError, ProviderRequestError, ProviderTimeoutError
from src.llm.service import InvalidModelOutput, enrich_book

router = APIRouter()


@router.post(
    "/enrich",
    response_model=BookEnrichmentResult,
    summary="Classify and summarize a scraped book",
    tags=["Book enrichment"],
)
def enrich(payload: BookEnrichmentRequest) -> BookEnrichmentResult:
    """Make one bounded enrichment decision from a book title and description."""
    try:
        return enrich_book(payload)
    except ProviderConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ProviderTimeoutError as exc:
        raise HTTPException(status_code=504, detail=str(exc)) from exc
    except ProviderRequestError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except InvalidModelOutput as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
