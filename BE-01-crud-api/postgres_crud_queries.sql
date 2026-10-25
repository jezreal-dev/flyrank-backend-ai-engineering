-- =============================================================================
-- [Week 3 · Assignment A3 / BE-04] PostgreSQL CRUD Reference Queries
-- Container: taskdb (PostgreSQL 16)
-- Database:  tasks
-- =============================================================================

-- 1. Read all tasks (GET /tasks)
SELECT id, title, done FROM tasks ORDER BY id ASC;

-- 2. Read single task with parameterized placeholder (GET /tasks/:id)
--    psycopg uses %s; SQL equivalent:
SELECT id, title, done FROM tasks WHERE id = 1;

-- 3. Create a new task with RETURNING clause (POST /tasks)
--    The RETURNING clause hands back the generated primary key id instantly:
INSERT INTO tasks (title, done)
VALUES ('Learn Docker Compose for AI pipelines', FALSE)
RETURNING id, title, done;

-- 4. Update task title and done status with RETURNING clause (PUT /tasks/:id)
UPDATE tasks
SET title = 'Learn Docker Compose for AI pipelines (Mastered)', done = TRUE
WHERE id = 4
RETURNING id, title, done;

-- 5. Delete task by id (DELETE /tasks/:id)
DELETE FROM tasks WHERE id = 4;

-- 6. Aggregate stats in a single query (GET /stats)
SELECT
    COUNT(*) AS total,
    COUNT(*) FILTER (WHERE done = TRUE) AS done,
    COUNT(*) FILTER (WHERE done = FALSE) AS open
FROM tasks;

-- 7. Reset tasks sequence and seed starter data (POST /reset)
DELETE FROM tasks;
ALTER SEQUENCE tasks_id_seq RESTART WITH 1;
INSERT INTO tasks (title, done) VALUES
    ('Read the FastAPI docs', TRUE),
    ('Build a CRUD API', FALSE),
    ('Test every endpoint with curl', FALSE);
