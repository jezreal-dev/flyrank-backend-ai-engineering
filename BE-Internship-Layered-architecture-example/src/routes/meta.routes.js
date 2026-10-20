// The API's "front door" routes: what this API is, and whether it's alive.
// These are simple enough to answer directly — no service needed.
const express = require('express');

const router = express.Router();

router.get('/', (req, res) => {
  res.json({
    name: 'Task API',
    version: '1.0',
    endpoints: ['/tasks', '/stats', '/reset'],
  });
});

router.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

module.exports = router;
