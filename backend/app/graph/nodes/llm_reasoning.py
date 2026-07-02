"""
LLM Reasoning Node — the agentic core. Decides reply type (text/image/
document), which media asset to use (if any), and scores sentiment for
the handover bonus feature.
"""
from typing import Any

from app.graph.dependencies import GraphDependencies
from app.graph.state import ConversationState
from app.utils.logger import get_logger

log = get_logger(__name__)


def build_llm_reasoning_node(deps: GraphDependencies):
    async def llm_reasoning(state: ConversationState) -> dict[str, Any]:
        tenant_id = state["tenant_id"]
        session_id = state["session_id"]
        node_log = get_logger(__name__, tenant_id=tenant_id, session_id=session_id)

        decision = await deps.llm_service.decide_reply(
            system_prompt=state["tenant_system_prompt"],
            media_library=state["media_library"],
            history=state["history"],
            incoming_message=state["incoming_message"],
            media_description=state.get("media_description"),
        )

        node_log.info(
            f"LLM decided reply_type={decision.reply_type} "
            f"sentiment={decision.sentiment_score:.2f} needs_human={decision.needs_human}"
        )

        return {"reply_decision": decision}

    return llm_reasoning


def should_handover(state: ConversationState) -> str:
    """Conditional-edge router: sentiment-triggered handover, per bonus spec."""
    decision = state["reply_decision"]
    return "handover" if decision.needs_human else "dispatch"
