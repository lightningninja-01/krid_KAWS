"""
Media Interpreter Node (bonus feature) — conditionally runs only when the
inbound message itself is an image, using a multimodal LLM to produce a
text description that gets folded into the LLM Reasoning node's context.

This is deliberately its own node rather than logic inside Context
Retriever or LLM Reasoning: single responsibility (only this node knows
how to call a vision model), and it can be disabled or swapped out
per-tenant later without touching the reasoning logic.
"""
from typing import Any

from app.graph.dependencies import GraphDependencies
from app.graph.state import ConversationState
from app.utils.logger import get_logger

log = get_logger(__name__)


def should_interpret_media(state: ConversationState) -> str:
    """Conditional-edge router: only visit this node for inbound images."""
    incoming = state["incoming_message"]
    return "interpret" if incoming.message_type == "image" else "skip"


def build_media_interpreter_node(deps: GraphDependencies):
    async def media_interpreter(state: ConversationState) -> dict[str, Any]:
        tenant_id = state["tenant_id"]
        session_id = state["session_id"]
        incoming = state["incoming_message"]
        node_log = get_logger(__name__, tenant_id=tenant_id, session_id=session_id)

        if not incoming.media_id:
            node_log.warning("Image message had no media_id — skipping interpretation")
            return {"media_description": None}

        try:
            description = await deps.vision_service.describe_media(incoming.media_id)
            node_log.info("Interpreted inbound image")
            return {"media_description": description}
        except Exception as exc:  # noqa: BLE001 — vision failure shouldn't block the reply
            node_log.warning(f"Media interpretation failed (non-fatal): {exc!r}")
            return {"media_description": None}

    return media_interpreter
