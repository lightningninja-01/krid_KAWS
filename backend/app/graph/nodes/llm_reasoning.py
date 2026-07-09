"""
LLM Reasoning Node - the agentic core. Decides reply type (text/image/
document), which media asset to use (if any), and scores sentiment for
the handover bonus feature.
"""
from typing import Any

from app.graph.dependencies import GraphDependencies
from app.graph.state import ConversationState, ReplyDecision
from app.utils.logger import get_logger

log = get_logger(__name__)

FALLBACK_REPLY = (
    "Sorry, I'm having trouble generating a full response right now. "
    "I've received your message and our team will follow up shortly."
)


def build_llm_reasoning_node(deps: GraphDependencies):
    async def llm_reasoning(state: ConversationState) -> dict[str, Any]:
        tenant_id = state["tenant_id"]
        session_id = state["session_id"]
        node_log = get_logger(__name__, tenant_id=tenant_id, session_id=session_id)

        try:
            decision = await deps.llm_service.decide_reply(
                system_prompt=state["tenant_system_prompt"],
                media_library=state["media_library"],
                history=state["history"],
                incoming_message=state["incoming_message"],
                media_description=state.get("media_description"),
            )
        except Exception as exc:  # noqa: BLE001 - keep the customer flow alive if the provider fails
            node_log.error(f"LLM reasoning failed; sending fallback reply: {exc!r}")
            decision = ReplyDecision(
                reply_type="text",
                text_content=FALLBACK_REPLY,
                sentiment_score=0.0,
                needs_human=False,
                reasoning=f"Fallback reply because LLM reasoning failed: {exc!r}",
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
