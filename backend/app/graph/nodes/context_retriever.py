"""
Context Retriever Node — pulls everything the LLM needs to reason:
tenant instructions, media library rules, and the last 5 messages.
"""
from typing import Any

from app.graph.dependencies import GraphDependencies
from app.graph.state import ConversationState
from app.utils.logger import get_logger

log = get_logger(__name__)


def build_context_retriever_node(deps: GraphDependencies):
    async def context_retriever(state: ConversationState) -> dict[str, Any]:
        tenant_id = state["tenant_id"]
        session_id = state["session_id"]
        node_log = get_logger(__name__, tenant_id=tenant_id, session_id=session_id)

        tenant = await deps.tenant_repo.get_by_id(tenant_id)
        recent_messages = await deps.message_repo.get_recent_history(tenant_id, session_id, limit=5)

        history_payload = [
            {
                "sender": msg.sender.value,
                "text": msg.text,
                "message_type": msg.message_type.value,
                "created_at": msg.created_at.isoformat(),
            }
            for msg in recent_messages
        ]

        node_log.info(f"Loaded context: {len(history_payload)} prior messages, "
                       f"{len(tenant.media_library)} media assets")

        return {
            "tenant_system_prompt": tenant.system_prompt,
            "media_library": tenant.media_library,
            "history": history_payload,
        }

    return context_retriever
