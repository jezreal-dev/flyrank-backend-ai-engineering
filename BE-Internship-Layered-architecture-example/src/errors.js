// Domain errors. The service layer throws these when a business rule fails.
// They carry MEANING ("not found", "invalid input") but know nothing about HTTP —
// it's the error-handler middleware that maps them to 404 / 400 status codes.

class NotFoundError extends Error {
  constructor(message) {
    super(message);
    this.name = 'NotFoundError';
  }
}

class ValidationError extends Error {
  constructor(message) {
    super(message);
    this.name = 'ValidationError';
  }
}

module.exports = { NotFoundError, ValidationError };
