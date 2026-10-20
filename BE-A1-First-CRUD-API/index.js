// Task API — a small in-memory CRUD server for a to-do list.
// Stages 0–6 of the W2 assignment, plus the optional extras.
const express = require('express');
const swaggerUi = require('swagger-ui-express');
const openapi = require('./openapi.json');
const app = express();
const port = 3000;

// Express needs this to parse JSON request bodies.
app.use(express.json());

// ---------------------------------------------------------------------------
// "Database" — just a list in memory. Gone when the server restarts.
// (That data loss is the whole point of next week's database lesson.)
// ---------------------------------------------------------------------------
const SEED_TASKS = [
  { id: 1, title: 'Buy groceries', done: false },
  { id: 2, title: 'Walk the dog', done: true },
  { id: 3, title: 'Read a book', done: false },
];

const tasks = SEED_TASKS.map((task) => ({ ...task }));

function resetTasks() {
  tasks.length = 0;
  tasks.push(...SEED_TASKS.map((task) => ({ ...task })));
}

// ---------------------------------------------------------------------------
// Stage 5 — Swagger UI at /docs
// ---------------------------------------------------------------------------
app.use('/docs', swaggerUi.serve, swaggerUi.setup(openapi));

// ---------------------------------------------------------------------------
// Stage 1 — the front door
// ---------------------------------------------------------------------------
app.get('/', (req, res) => {
  res.json({
    name: 'Task API',
    version: '1.0',
    endpoints: ['/tasks', '/stats', '/reset'],
  });
});

app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

// ---------------------------------------------------------------------------
// Stage 2 — Read: list + single task (with optional filtering/search extras)
// ---------------------------------------------------------------------------
app.get('/tasks', (req, res) => {
  let result = tasks;

  // Extras: GET /tasks?done=true  → only finished (or only open) tasks.
  if (req.query.done !== undefined) {
    if (req.query.done !== 'true' && req.query.done !== 'false') {
      return res.status(400).json({ error: 'done must be true or false' });
    }
    const done = req.query.done === 'true';
    result = result.filter((t) => t.done === done);
  }

  // Extras: GET /tasks?search=milk → tasks whose title contains the word.
  if (req.query.search !== undefined) {
    const word = String(req.query.search).trim();
    if (word === '') {
      return res.status(400).json({ error: 'search must not be empty' });
    }
    const lower = word.toLowerCase();
    result = result.filter((t) => t.title.toLowerCase().includes(lower));
  }

  res.json(result);
});

// ---------------------------------------------------------------------------
// Extras — stats. Declared before "/tasks/:id" so "stats" isn't read as an id.
// ---------------------------------------------------------------------------
app.get('/stats', (req, res) => {
  const done = tasks.filter((t) => t.done).length;
  res.json({
    total: tasks.length,
    done,
    open: tasks.length - done,
  });
});

// Extras — reset back to the 3 example tasks. Handy for demos.
app.post('/reset', (req, res) => {
  resetTasks();
  res.json(tasks);
});

// ---------------------------------------------------------------------------
// Stage 3 — Create
// ---------------------------------------------------------------------------
app.post('/tasks', (req, res) => {
  const { title } = req.body;

  if (title === undefined || title === null || String(title).trim() === '') {
    return res.status(400).json({ error: 'title is required and cannot be empty' });
  }

  const id = tasks.length === 0 ? 1 : Math.max(...tasks.map((t) => t.id)) + 1;
  const task = { id, title: String(title).trim(), done: false };

  tasks.push(task);
  res.status(201).json(task);
});

app.get('/tasks/:id', (req, res) => {
  const id = Number(req.params.id);
  const task = tasks.find((t) => t.id === id);

  if (!task) {
    return res.status(404).json({ error: `Task ${id} not found` });
  }

  res.json(task);
});

// ---------------------------------------------------------------------------
// Stage 4 — Update & Delete
// ---------------------------------------------------------------------------
app.put('/tasks/:id', (req, res) => {
  const id = Number(req.params.id);
  const task = tasks.find((t) => t.id === id);

  if (!task) {
    return res.status(404).json({ error: `Task ${id} not found` });
  }

  const { title, done } = req.body ?? {};
  const hasTitle = Object.prototype.hasOwnProperty.call(req.body ?? {}, 'title');
  const hasDone = Object.prototype.hasOwnProperty.call(req.body ?? {}, 'done');

  if (!hasTitle && !hasDone) {
    return res.status(400).json({ error: 'request body must include title and/or done' });
  }

  if (hasTitle) {
    if (title === null || String(title).trim() === '') {
      return res.status(400).json({ error: 'title cannot be empty' });
    }
    task.title = String(title).trim();
  }

  if (hasDone) {
    if (typeof done !== 'boolean') {
      return res.status(400).json({ error: 'done must be a boolean' });
    }
    task.done = done;
  }

  res.json(task);
});

app.delete('/tasks/:id', (req, res) => {
  const id = Number(req.params.id);
  const index = tasks.findIndex((t) => t.id === id);

  if (index === -1) {
    return res.status(404).json({ error: `Task ${id} not found` });
  }

  tasks.splice(index, 1);
  res.status(204).send();
});

// ---------------------------------------------------------------------------
// Stage 0 — start the server
// ---------------------------------------------------------------------------
app.listen(port, () => {
  console.log(`CRUD API listening on port ${port}`);
});
