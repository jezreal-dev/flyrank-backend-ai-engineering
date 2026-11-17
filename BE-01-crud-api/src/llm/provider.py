"""OpenAI-compatible provider adapter for OpenRouter."""

from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import os
import random
import time

from openai import APIConnectionError, APIStatusError, APITimeoutError, OpenAI, OpenAIError


class ProviderConfigurationError(RuntimeError):
    """The provider cannot be called because required settings are missing."""


class ProviderTimeoutError(RuntimeError):
    """The provider request exceeded its client timeout."""


class ProviderRequestError(RuntimeError):
    """The provider rejected or failed a request."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        retry_after: str | None = None,
        error_type: str | None = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.retry_after = retry_after
        self.error_type = error_type


@dataclass(frozen=True)
class ModelReply:
    content: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    cost_usd: float | None = None


def complete(messages: list[dict[str, str]]) -> ModelReply:
    """Send a bounded request, retrying one transient failure at most once."""
    base_url = os.getenv("LLM_BASE_URL", "").strip()
    api_key = os.getenv("LLM_API_KEY", "").strip()
    model = os.getenv("LLM_MODEL", "").strip()
    missing = [name for name, value in (
        ("LLM_BASE_URL", base_url),
        ("LLM_API_KEY", api_key),
        ("LLM_MODEL", model),
    ) if not value]
    if missing:
        raise ProviderConfigurationError("Missing provider setting(s): " + ", ".join(missing))

    client = OpenAI(base_url=base_url, api_key=api_key, timeout=12.0, max_retries=0)
    json_mode = os.getenv("LLM_JSON_MODE", "1").strip().lower() not in {"0", "false", "no", "off"}
    response = None
    for attempt in range(2):
        try:
            request_options = {
                "model": model,
                "messages": messages,
                "temperature": 0,
                "max_tokens": 256,
            }
            if json_mode:
                request_options["response_format"] = {"type": "json_object"}
            response = client.chat.completions.create(
                **request_options,
            )
            break
        except APITimeoutError as exc:
            if attempt == 0:
                time.sleep(random.uniform(0.5, 1.5))
                continue
            raise ProviderTimeoutError("The model provider timed out after one retry.") from exc
        except APIStatusError as exc:
            retry_after = exc.response.headers.get("retry-after")
            transient = exc.status_code == 429 or 500 <= exc.status_code <= 599
            delay = _retry_delay(retry_after, attempt)
            if attempt == 0 and transient and delay is not None:
                time.sleep(delay)
                continue
            raise ProviderRequestError(
                "The model provider returned an error.",
                status_code=exc.status_code,
                retry_after=retry_after,
            ) from exc
        except APIConnectionError as exc:
            if attempt == 0:
                time.sleep(random.uniform(0.5, 1.5))
                continue
            raise ProviderRequestError(
                "Could not connect to the model provider after one retry.",
                error_type=type(exc).__name__,
            ) from exc
        except OpenAIError as exc:
            raise ProviderRequestError(
                "The model provider request failed.",
                error_type=type(exc).__name__,
            ) from exc

    if response is None:
        raise ProviderRequestError("The model provider request failed without a response.")

    choices = getattr(response, "choices", [])
    content = choices[0].message.content if choices else None
    if not isinstance(content, str) or not content.strip():
        raise ProviderRequestError("The model provider returned no text content.")

    usage = getattr(response, "usage", None)
    return ModelReply(
        content=content,
        model=getattr(response, "model", model) or model,
        prompt_tokens=getattr(usage, "prompt_tokens", 0) or 0,
        completion_tokens=getattr(usage, "completion_tokens", 0) or 0,
        cost_usd=getattr(usage, "cost", None),
    )


def _retry_delay(retry_after: str | None, attempt: int) -> float | None:
    """Honor short Retry-After hints; long waits are surfaced instead of blocking."""
    if retry_after:
        try:
            delay = float(retry_after)
        except ValueError:
            try:
                parsed = parsedate_to_datetime(retry_after)
                delay = (parsed - datetime.now(timezone.utc)).total_seconds()
            except (TypeError, ValueError, OverflowError):
                return None
        if delay < 0:
            delay = 0
        return delay if delay <= 2 else None
    return random.uniform(0.5, 1.5) * (attempt + 1)
