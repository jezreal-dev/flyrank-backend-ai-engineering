// ===========================================================================
// SERVICE LAYER — the business rules. Storage-agnostic and HTTP-agnostic.
// ===========================================================================
// This is where the *decisions* live: what makes input valid, how a new id is
// chosen, what "not found" means. It never touches req/res (that's the route's
// job) and never touches the tasks array (that's the repository's job) — it
// just calls the repository and throws domain errors when a rule is broken.

const repo = require('../repositories/tasks.repository');
const { NotFoundError, ValidationError } = require('../errors');

function listTasks({ done, search } = {}) {
  let result = repo.findAll();

  // Extra: filter by done=true / done=false
  if (done !== undefined) {
    if (done !== 'true' && done !== 'false') {
      throw new ValidationError('done must be true or false');
    }
    const wantDone = done === 'true';
    result = result.filter((t) => t.done === wantDone);
  }

  // Extra: search titles
  if (search !== undefined) {
    const word = String(search).trim();
    if (word === '') {
      throw new ValidationError('search must not be empty');
    }
    const lower = word.toLowerCase();
    result = result.filter((t) => t.title.toLowerCase().includes(lower));
  }

  return result;
}

function getTask(id) {
  const task = repo.findById(id);
  if (!task) {
    throw new NotFoundError(`Task ${id} not found`);
  }
  return task;
}

function createTask(body = {}) {
  const { title } = body;
  if (title === undefined || title === null || String(title).trim() === '') {
    throw new ValidationError('title is required and cannot be empty');
  }
  return repo.create({ title: String(title).trim(), done: false });
}

function updateTask(id, body = {}) {
  const hasTitle = Object.prototype.hasOwnProperty.call(body, 'title');
  const hasDone = Object.prototype.hasOwnProperty.call(body, 'done');

  if (!hasTitle && !hasDone) {
    throw new ValidationError('request body must include title and/or done');
  }

  const changes = {};

  if (hasTitle) {
    if (body.title === null || String(body.title).trim() === '') {
      throw new ValidationError('title cannot be empty');
    }
    changes.title = String(body.title).trim();
  }

  if (hasDone) {
    if (typeof body.done !== 'boolean') {
      throw new ValidationError('done must be a boolean');
    }
    changes.done = body.done;
  }

  const updated = repo.update(id, changes);
  if (!updated) {
    throw new NotFoundError(`Task ${id} not found`);
  }
  return updated;
}

function deleteTask(id) {
  const removed = repo.remove(id);
  if (!removed) {
    throw new NotFoundError(`Task ${id} not found`);
  }
}

function getStats() {
  const all = repo.findAll();
  const done = all.filter((t) => t.done).length;
  return { total: all.length, done, open: all.length - done };
}

function resetTasks() {
  return repo.reset();
}

module.exports = {
  listTasks,
  getTask,
  createTask,
  updateTask,
  deleteTask,
  getStats,
  resetTasks,
};
