"""
Typing indicator heartbeat service.

WhatsApp's typing indicator expires ~25s after being set. Since LLM
reasoning (especially with a vision call in the mix) can plausibly exceed
that, a single fire-and-forget call isn't enough for the "keep typing
active during LLM reasoning" requirement. This service re-sends the
typing signal on an interval until explicitly stopped by the Dispatcher
or Handover node.
"""
import asyncio

from app.config.settings import get_settings
from app.services.whatsapp_client import WhatsAppClient
from app.utils.logger import get_logger
from app.utils.task_registry import task_registry

log = get_logger(__name__)


class TypingHeartbeatService:
    def __init__(self, whatsapp_client: WhatsAppClient) -> None:
        self._client = whatsapp_client
        self._interval = get_settings().typing_heartbeat_interval_seconds
        # Track the anchor message ID per session so the heartbeat loop can
        # keep re-sending typing_indicator against the correct inbound message.
        self._anchor_message_ids: dict[str, str] = {}

    async def start(self, session_id: str, meta_message_id: str) -> None:
        self._anchor_message_ids[session_id] = meta_message_id
        task_registry.spawn(
            f"typing:{session_id}",
            self._heartbeat_loop(session_id),
            on_error_log="Typing heartbeat loop crashed",
        )

    async def stop(self, session_id: str) -> None:
        task_registry.cancel(f"typing:{session_id}")
        self._anchor_message_ids.pop(session_id, None)

    async def _heartbeat_loop(self, session_id: str) -> None:
        # Fire once immediately, then keep re-firing on an interval until cancelled.
        while True:
            meta_message_id = self._anchor_message_ids.get(session_id)
            if meta_message_id is None:
                return
            try:
                await self._client.send_typing_indicator(meta_message_id)
            except Exception as exc:  # noqa: BLE001 — a missed heartbeat tick shouldn't kill the loop
                log.warning(f"Typing heartbeat tick failed for session {session_id}: {exc!r}")
            await asyncio.sleep(self._interval)
