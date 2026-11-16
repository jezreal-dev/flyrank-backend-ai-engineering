"""OpenAI-compatible provider adapter for OpenRouter."""

from dataclasses import dataclass
import os

from openai import APIConnectionError, APIStatusError, APITimeoutError, OpenAI, OpenAIError


class ProviderConfigurationError(RuntimeError):
    """The provider cannot be called because required settings are missing."""


class ProviderTimeoutError(RuntimeError):
    """The provider request exceeded its client timeout."""


class ProviderRequestError(RuntimeError):
    """The provider rejected or failed a request."""

    def __init__(self, message: str, *, status_code: int | None = None, retry_after: str | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.retry_after = retry_after


@dataclass(frozen=True)
class ModelReply:
    content: str
    model: str
    prompt_tokens: int
    completion_tokens: int


def complete(messages: list[dict[str, str]]) -> ModelReply:
    """Send one bounded chat-completion request and return its measured response."""
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

    client = OpenAI(base_url=base_url, api_key=api_key, timeout=15.0, max_retries=0)
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0,
            max_tokens=256,
        )
    except APITimeoutError as exc:
        raise ProviderTimeoutError("The model provider timed out.") from exc
    except APIStatusError as exc:
        retry_after = exc.response.headers.get("retry-after")
        raise ProviderRequestError(
            "The model provider returned an error.",
            status_code=exc.status_code,
            retry_after=retry_after,
        ) from exc
    except (APIConnectionError, OpenAIError) as exc:
        raise ProviderRequestError("Could not connect to the model provider.") from exc

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
    )
