"""
Polite HTTP Fetcher & Local Disk Cache (Stages 1, 2, 3, and 5).
- Sends an honest identifying User-Agent header.
- Enforces an explicit request timeout (10 seconds).
- Checks HTTP status codes strictly (only 200 is cached and parsed).
- Waits >= 500ms between live network requests (0ms delay on local cache hits).
- Retries once on transient timeout / 5xx server errors; never retries 404 or 403.
"""

from pathlib import Path
import time
from typing import Tuple
import requests

USER_AGENT = "FlyRankInternship-A9/1.0 (+https://github.com/jezreal-dev/flyrank-backend-ai-engineering)"
REQUEST_TIMEOUT_SECONDS = 10.0
POLITE_DELAY_SECONDS = 0.55


class FetchError(Exception):
    """Raised when a page cannot be fetched politely."""

    def __init__(self, url: str, reason: str, status_code: int | None = None):
        super().__init__(f"{url} -> {reason}")
        self.url = url
        self.reason = reason
        self.status_code = status_code


class PoliteFetcher:
    def __init__(
        self,
        cache_dir: Path,
        user_agent: str = USER_AGENT,
        timeout: float = REQUEST_TIMEOUT_SECONDS,
        delay_seconds: float = POLITE_DELAY_SECONDS,
    ) -> None:
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.user_agent = user_agent
        self.timeout = timeout
        self.delay_seconds = delay_seconds
        self.last_network_request_at: float | None = None
        self.pages_fetched: int = 0
        self.cache_hits: int = 0

    def _wait_politely(self) -> None:
        if self.last_network_request_at is not None:
            elapsed = time.monotonic() - self.last_network_request_at
            if elapsed < self.delay_seconds:
                time.sleep(self.delay_seconds - elapsed)

    def fetch_or_cache(self, url: str, cache_filename: str, verbose: bool = True) -> Tuple[str, str]:
        """
        Returns (html_text, source_status) where source_status is 'FETCH' or 'CACHE HIT'.
        Raises FetchError on non-200 or network failure.
        """
        cache_path = self.cache_dir / cache_filename
        cache_path.parent.mkdir(parents=True, exist_ok=True)

        if cache_path.is_file():
            html = cache_path.read_text(encoding="utf-8")
            self.cache_hits += 1
            if verbose:
                print(f"CACHE HIT | {cache_filename} | size={len(html.encode('utf-8'))} bytes | url={url}")
            return html, "CACHE HIT"

        headers = {"User-Agent": self.user_agent}
        max_attempts = 2

        for attempt in range(1, max_attempts + 1):
            self._wait_politely()
            try:
                resp = requests.get(url, headers=headers, timeout=self.timeout)
                self.last_network_request_at = time.monotonic()
            except (requests.Timeout, requests.ConnectionError) as exc:
                self.last_network_request_at = time.monotonic()
                if attempt < max_attempts:
                    time.sleep(1.0)
                    continue
                raise FetchError(url, f"Network timeout/connection error after {attempt} attempts: {exc}") from exc

            # Never retry 404 (not found) or 403 (forbidden)
            if resp.status_code in (403, 404):
                raise FetchError(url, f"HTTP {resp.status_code} (non-retryable client error)", status_code=resp.status_code)

            # Retry once on 5xx server error
            if 500 <= resp.status_code < 600:
                if attempt < max_attempts:
                    time.sleep(1.0)
                    continue
                raise FetchError(url, f"HTTP {resp.status_code} server error after {attempt} attempts", status_code=resp.status_code)

            if resp.status_code != 200:
                raise FetchError(url, f"Unexpected HTTP status {resp.status_code}", status_code=resp.status_code)

            # Decode explicitly as UTF-8 so '£' never turns into 'Â£'
            resp.encoding = "utf-8"
            html = resp.text
            cache_path.write_text(html, encoding="utf-8")
            self.pages_fetched += 1
            if verbose:
                print(f"FETCH     | {cache_filename} | status=200 | size={len(html.encode('utf-8'))} bytes | url={url}")
            return html, "FETCH"

        raise FetchError(url, "Exhausted fetch attempts")
