"""
Tests for WhatsAppClient's retry policy — the specific behavior that
matters is: retry on 5xx/timeout, fail fast on 4xx.
"""
import httpx
import pytest
import respx

from app.exceptions.custom_exceptions import MetaAPIError
from app.services.whatsapp_client import WhatsAppClient


@pytest.fixture
def client():
    return WhatsAppClient()


class TestRetryPolicy:
    @respx.mock
    async def test_retries_on_server_error_then_succeeds(self, client):
        route = respx.post(url__regex=r".*/messages$").mock(
            side_effect=[
                httpx.Response(500, json={"error": "server exploded"}),
                httpx.Response(200, json={"messages": [{"id": "wamid.success"}]}),
            ]
        )

        message_id = await client.send_text("1555", "hello")

        assert message_id == "wamid.success"
        assert route.call_count == 2

    @respx.mock
    async def test_does_not_retry_on_client_error(self, client):
        route = respx.post(url__regex=r".*/messages$").mock(
            return_value=httpx.Response(400, json={"error": "invalid phone number"})
        )

        with pytest.raises(MetaAPIError):
            await client.send_text("1555", "hello")

        # A 4xx is a bad payload/auth issue — retrying is pointless, must fail on first attempt.
        assert route.call_count == 1

    @respx.mock
    async def test_gives_up_after_max_retries_on_persistent_server_error(self, client):
        route = respx.post(url__regex=r".*/messages$").mock(
            return_value=httpx.Response(503, json={"error": "unavailable"})
        )

        with pytest.raises(MetaAPIError):
            await client.send_text("1555", "hello")

        assert route.call_count == 3
