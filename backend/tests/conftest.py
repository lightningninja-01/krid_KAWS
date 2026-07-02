"""
Shared pytest fixtures. Sets required env vars before any app module is
imported, since Settings() validates required fields at instantiation and
get_settings() is process-wide cached.
"""
import os

os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017")
os.environ.setdefault("GEMINI_API_KEY", "test-key")
os.environ.setdefault("META_APP_SECRET", "test-app-secret")
os.environ.setdefault("META_WEBHOOK_VERIFY_TOKEN", "test-verify-token")
os.environ.setdefault("META_ACCESS_TOKEN", "test-access-token")
os.environ.setdefault("META_PHONE_NUMBER_ID", "test-phone-number-id")

import asyncio

import pytest


@pytest.fixture(autouse=True)
def _skip_real_sleep(monkeypatch):
    """Retry backoff uses real asyncio.sleep — no need to actually wait in tests."""

    async def _instant_sleep(_seconds: float) -> None:
        return None

    monkeypatch.setattr(asyncio, "sleep", _instant_sleep)
