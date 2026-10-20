// ===========================================================================
// ERROR-HANDLING MIDDLEWARE — one place that turns domain errors into HTTP.
// ===========================================================================
// The service throws meaning ("this is invalid", "this wasn't found"); this
// middleware decides the status code. Because it lives in ONE place, every
// route gets consistent error responses for free — no repeated 400/404 code.
const { NotFoundError, ValidationError } = require('../errors');

function errorHandler(err, req, res, next) { // eslint-disable-line no-unused-vars
  if (err instanceof ValidationError) {
    return res.status(400).json({ error: err.message });
  }
  if (err instanceof NotFoundError) {
    return res.status(404).json({ error: err.message });
  }

  // Anything we didn't expect is a real server bug.
  console.error(err);
  return res.status(500).json({ error: 'Internal server error' });
}

module.exports = { errorHandler };
