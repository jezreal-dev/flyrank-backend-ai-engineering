-- =============================================================================
-- [Week 3 · Stage 4] LEARN YOUR FIRST SQL BY HAND (stage4_queries.sql)
-- Assignment: W3 · A2 — Connecting Your CRUD to the Database
-- Database:   tasks.db
-- =============================================================================

-- 1. List every task (returns all columns: id, title, done for every row)
SELECT * FROM tasks;

-- 2. Show only completed tasks (filters rows where done is 1 / True)
SELECT * FROM tasks WHERE done = 1;

-- 3. Count all tasks (returns a single number: total row count in tasks)
SELECT COUNT(*) FROM tasks;

-- 4. Mark every task as completed (updates done to 1 across all rows)
--    ⚠️ Note: Without a WHERE clause, UPDATE modifies EVERY row in the table!
UPDATE tasks SET done = 1;

-- 5. Delete all completed tasks (removes every row where done is 1)
DELETE FROM tasks WHERE done = 1;
