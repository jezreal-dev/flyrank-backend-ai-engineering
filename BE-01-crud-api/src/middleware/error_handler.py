"""
Error-Handling Middleware — Centralized Domain-to-HTTP Error Mapper

Matches `src/middleware/error-handler.js` from the FlyRank Layered Architecture repo:
Maps domain exceptions (`ValidationError` -> 400, `NotFoundError` -> 404) in one
single place so route handlers stay thin and never repeat 400/404 response code.
"""

from fastapi import FastAPI, Request
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.errors import NotFoundError, ValidationError


def register_error_handlers(app: FastAPI) -> None:
    """Attach domain exception handlers to the FastAPI application."""

    @app.exception_handler(ValidationError)
    async def validation_error_handler(_request: Request, exc: ValidationError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"error": str(exc)})

    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        if request.url.path == "/enrich":
            fields = []
            for error in exc.errors():
                location = [str(part) for part in error.get("loc", ()) if part != "body"]
                fields.append({
                    "field": ".".join(location) or "body",
                    "message": error.get("msg", "Invalid value"),
                })
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid request", "fields": fields},
            )
        return await request_validation_exception_handler(request, exc)

    @app.exception_handler(NotFoundError)
    async def not_found_error_handler(_request: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"error": str(exc)})
