-- ============================================================================
-- FlyRank Backend AI Engineering - Week 3 (BE-04)
-- Database Initialization & Schema Definition for PostgreSQL
-- ============================================================================

-- Create the tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    done BOOLEAN NOT NULL DEFAULT FALSE
);

-- Index on done column to optimize status filtering
CREATE INDEX IF NOT EXISTS idx_tasks_done ON tasks(done);

-- Seed initial starter tasks only if table is empty
INSERT INTO tasks (title, done)
SELECT 'Read the FastAPI docs', TRUE
WHERE NOT EXISTS (SELECT 1 FROM tasks);

INSERT INTO tasks (title, done)
SELECT 'Build a CRUD API', FALSE
WHERE (SELECT COUNT(*) FROM tasks) = 1;

INSERT INTO tasks (title, done)
SELECT 'Test every endpoint with curl', FALSE
WHERE (SELECT COUNT(*) FROM tasks) = 2;
