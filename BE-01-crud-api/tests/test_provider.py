"""Bounded retry policy tests; no external provider requests are made."""

from types import SimpleNamespace

import pytest

import src.llm.provider as provider


class FakeStatusError(Exception):
    def __init__(self, status_code: int, retry_after: str | None = None):
        self.status_code = status_code
        self.response = SimpleNamespace(headers={"retry-after": retry_after} if retry_after else {})


def _success_response():
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content='{"ok":true}'))],
        model="actual-model",
        usage=SimpleNamespace(prompt_tokens=4, completion_tokens=3),
    )


def _configure(monkeypatch, outcomes):
    calls = []

    class FakeCompletions:
        def create(self, **kwargs):
            calls.append(kwargs)
            outcome = outcomes.pop(0)
            if isinstance(outcome, Exception):
                raise outcome
            return outcome

    fake_client = SimpleNamespace(chat=SimpleNamespace(completions=FakeCompletions()))
    monkeypatch.setattr(provider, "OpenAI", lambda **kwargs: fake_client)
    monkeypatch.setenv("LLM_BASE_URL", "https://provider.invalid/v1")
    monkeypatch.setenv("LLM_API_KEY", "test-secret")
    monkeypatch.setenv("LLM_MODEL", "openrouter/free")
    monkeypatch.setenv("LLM_JSON_MODE", "1")
    return calls


def test_retries_one_429_with_short_retry_after(monkeypatch):
    monkeypatch.setattr(provider, "APIStatusError", FakeStatusError)
    sleeps = []
    monkeypatch.setattr(provider.time, "sleep", sleeps.append)
    calls = _configure(monkeypatch, [FakeStatusError(429, "1"), _success_response()])

    result = provider.complete([{"role": "user", "content": "test"}])

    assert len(calls) == 2
    assert sleeps == [1.0]
    assert result.model == "actual-model"
    assert result.prompt_tokens == 4
    assert calls[0]["response_format"] == {"type": "json_object"}


def test_does_not_retry_authentication_error(monkeypatch):
    monkeypatch.setattr(provider, "APIStatusError", FakeStatusError)
    calls = _configure(monkeypatch, [FakeStatusError(401)])

    with pytest.raises(provider.ProviderRequestError) as error:
        provider.complete([{"role": "user", "content": "test"}])

    assert error.value.status_code == 401
    assert len(calls) == 1


def test_does_not_wait_out_a_long_retry_after(monkeypatch):
    assert provider._retry_delay("900", 0) is None
    assert provider._retry_delay("1", 0) == 1
    assert provider._retry_delay(None, 0) is not None
