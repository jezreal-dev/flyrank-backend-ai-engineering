"""Keep endpoint tests isolated from the local PostgreSQL configuration."""

import os
from pathlib import Path

import pytest

# Importing main.py initializes storage. An empty DATABASE_URL selects SQLite.
os.environ["DATABASE_URL"] = ""


@pytest.fixture

def app(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    import database
    from main import create_app

    monkeypatch.setattr(database, "DB_PATH", tmp_path / "tasks-test.db")
    monkeypatch.setenv("LLM_STUB", "1")
    monkeypatch.setenv("LLM_ENABLED", "true")
    return create_app()


@pytest.fixture

def client(app):
    from fastapi.testclient import TestClient

    with TestClient(app) as test_client:
        yield test_client
