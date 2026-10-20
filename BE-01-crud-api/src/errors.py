"""
Domain Errors — Service Layer Exceptions

Matches the layered architecture pattern (`src/errors.js`):
The service layer raises these domain exceptions when a business rule fails.
They carry domain meaning ("not found", "invalid input") without knowing anything
about HTTP or FastAPI. The error-handler middleware maps them to HTTP 400 / 404.
"""


class NotFoundError(Exception):
    """Raised when a requested task ID does not exist in the repository."""


class ValidationError(Exception):
    """Raised when request data violates a business or validation rule."""
