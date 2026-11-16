"""Make one small provider call to verify BE-07 environment configuration."""

from __future__ import annotations

import os
from pathlib import Path
import sys

from dotenv import load_dotenv
from openai import OpenAI

API_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(API_ROOT / ".env")


def main() -> int:
    base_url = os.getenv("LLM_BASE_URL", "").strip()
    api_key = os.getenv("LLM_API_KEY", "").strip()
    model = os.getenv("LLM_MODEL", "").strip()

    missing = [name for name, value in (
        ("LLM_BASE_URL", base_url),
        ("LLM_API_KEY", api_key),
        ("LLM_MODEL", model),
    ) if not value]
    if missing:
        print(
            "Missing setting(s): " + ", ".join(missing)
            + ". Add them to BE-01-crud-api/.env; never paste the key into Git.",
            file=sys.stderr,
        )
        return 2

    client = OpenAI(base_url=base_url, api_key=api_key, timeout=15.0, max_retries=0)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "Reply with exactly the word ready."}],
        temperature=0,
        max_tokens=8,
    )
    content = response.choices[0].message.content or ""
    print(content)
    if "ready" not in content.casefold():
        print("Provider responded, but the output did not contain 'ready'.", file=sys.stderr)
        return 1
    print(f"Provider call succeeded (model returned: {response.model}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
