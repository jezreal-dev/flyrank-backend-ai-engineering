"""
Supabase Client Initialization & Configuration Module
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import Client, create_client

# Load environment variables from .env
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

_client: Client | None = None


def get_supabase_client() -> Client:
    """Return the initialized Supabase client singleton."""
    global _client
    if _client is not None:
        return _client

    url = os.getenv("SUPABASE_URL", SUPABASE_URL)
    key = os.getenv("SUPABASE_KEY", SUPABASE_KEY)

    if not url or not key:
        raise ValueError(
            "SUPABASE_URL and SUPABASE_KEY must be configured in your .env file."
        )

    _client = create_client(url, key)
    return _client
