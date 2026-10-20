// ===========================================================================
// ROUTE (HTTP) LAYER — the thin translator between HTTP and the service.
// ===========================================================================
// Each handler does only three things: read what it needs from the request,
// call the service, and shape the HTTP response (status code + JSON). No
// business rules, no data access. If the service throws, we hand the error to
// Express with next(err) and the error-handler middleware sets the status code.

const express = require('express');
const service = require('../services/tasks.service');

const router = express.Router();

// Read: list (with optional ?done= and ?search= extras)
router.get('/tasks', (req, res, next) => {
  try {
    const tasks = service.listTasks({ done: req.query.done, search: req.query.search });
    res.json(tasks);
  } catch (err) {
    next(err);
  }
});

// Extra: stats
router.get('/stats', (req, res, next) => {
  try {
    res.json(service.getStats());
  } catch (err) {
    next(err);
  }
});

// Extra: reset to the seed tasks
router.post('/reset', (req, res, next) => {
  try {
    res.json(service.resetTasks());
  } catch (err) {
    next(err);
  }
});

// Create
router.post('/tasks', (req, res, next) => {
  try {
    const task = service.createTask(req.body ?? {});
    res.status(201).json(task);
  } catch (err) {
    next(err);
  }
});

// Read: single task
router.get('/tasks/:id', (req, res, next) => {
  try {
    res.json(service.getTask(Number(req.params.id)));
  } catch (err) {
    next(err);
  }
});

// Update
router.put('/tasks/:id', (req, res, next) => {
  try {
    res.json(service.updateTask(Number(req.params.id), req.body ?? {}));
  } catch (err) {
    next(err);
  }
});

// Delete
router.delete('/tasks/:id', (req, res, next) => {
  try {
    service.deleteTask(Number(req.params.id));
    res.status(204).send();
  } catch (err) {
    next(err);
  }
});

module.exports = router;
