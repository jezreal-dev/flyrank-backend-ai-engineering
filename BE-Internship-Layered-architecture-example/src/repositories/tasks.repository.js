// ===========================================================================
// REPOSITORY LAYER — the ONLY file that knows *where* tasks are stored.
// ===========================================================================
// Right now that's a list in memory (exactly like Assignment 1). But this is
// the single file you rewrite to move to a real database:
//   - Assignment 2 (SQLite):   these functions run SELECT / INSERT / UPDATE / DELETE
//   - Assignment 3 (Postgres): same functions, a different driver
// The routes and the service NEVER change, because they only ever call
// findAll / findById / create / update / remove — they don't care what's behind them.
// The functions return COPIES, the way a database hands you fresh rows.

const SEED_TASKS = [
  { id: 1, title: 'Buy groceries', done: false },
  { id: 2, title: 'Walk the dog', done: true },
  { id: 3, title: 'Read a book', done: false },
];

let tasks = SEED_TASKS.map((task) => ({ ...task }));

function findAll() {
  return tasks.map((task) => ({ ...task }));
}

function findById(id) {
  const task = tasks.find((t) => t.id === id);
  return task ? { ...task } : null;
}

function create({ title, done }) {
  const id = tasks.length === 0 ? 1 : Math.max(...tasks.map((t) => t.id)) + 1;
  const task = { id, title, done };
  tasks.push(task);
  return { ...task };
}

function update(id, changes) {
  const task = tasks.find((t) => t.id === id);
  if (!task) return null;
  Object.assign(task, changes);
  return { ...task };
}

function remove(id) {
  const index = tasks.findIndex((t) => t.id === id);
  if (index === -1) return false;
  tasks.splice(index, 1);
  return true;
}

function reset() {
  tasks = SEED_TASKS.map((task) => ({ ...task }));
  return findAll();
}

module.exports = { findAll, findById, create, update, remove, reset };
