"""
Handover Node (bonus feature) — terminal node reached when the LLM's
sentiment score crosses the frustration threshold.

Deliberately sends a FIXED message rather than an LLM-generated one: you
never want a model improvising while a frustrated customer is mid-escalation.
Also deliberately a separate node from Dispatcher — Dispatcher's only job is
"send the AI's decided reply"; this node has a distinct side effect (session
status change + human-handoff message) that shouldn't be tangled into it.
"""
from typing import Any

from app.graph.dependencies import GraphDependencies
from app.graph.state import ConversationState
from app.models.message import Message, MessageSender, MessageStatus, MessageType
from app.models.session import SessionStatus
from app.utils.logger import get_logger

log = get_logger(__name__)

HANDOVER_MESSAGE = (
    "I understand this is frustrating, and I want to make sure you get the best help. "
    "I'm connecting you with a member of our team who will follow up with you shortly."
)


def build_handover_node(deps: GraphDependencies):
    async def handover(state: ConversationState) -> dict[str, Any]:
        tenant_id = state["tenant_id"]
        session_id = state["session_id"]
        customer_phone = state["customer_phone"]
        phone_number_id = state.get("phone_number_id")
        node_log = get_logger(__name__, tenant_id=tenant_id, session_id=session_id)

        await deps.session_repo.update_status(tenant_id, session_id, SessionStatus.NEEDS_HUMAN)

        try:
            meta_id = await deps.whatsapp_client.send_text(customer_phone, HANDOVER_MESSAGE, phone_number_id=phone_number_id)
            success, error_message = True, None
        except Exception as exc:  # noqa: BLE001
            node_log.error(f"Failed to send handover message: {exc!r}")
            meta_id, success, error_message = None, False, str(exc)

        outbound_doc = Message(
            tenant_id=tenant_id,
            session_id=session_id,
            sender=MessageSender.BOT,
            message_type=MessageType.TEXT,
            text=HANDOVER_MESSAGE,
            status=MessageStatus.SENT if success else MessageStatus.FAILED,
            metadata={
                "meta_message_id": meta_id,
                "sentiment_score": state["reply_decision"].sentiment_score,
                "handover_triggered": True,
            },
        )
        await deps.message_repo.insert(outbound_doc)
        await deps.typing_heartbeat.stop(session_id)

        node_log.warning("Session escalated to NEEDS_HUMAN due to sentiment threshold")
        return {"dispatch_result": {"success": success, "meta_message_id": meta_id, "error_message": error_message}}

    return handover


