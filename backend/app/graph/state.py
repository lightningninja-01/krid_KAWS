"""
LangGraph state definition.

Every node reads/writes a well-typed slice of this state — no ad-hoc dict
mutation. `error` is a first-class field so any node can short-circuit
gracefully (the Dispatcher sends a fallback message) instead of the graph
crashing and leaving the customer with no response and typing stuck ON.
"""
from typing import Any, Literal, TypedDict

from pydantic import BaseModel, Field


class IncomingMessage(BaseModel):
    """Normalized inbound message — decoupled from Meta's raw webhook shape."""

    meta_message_id: str
    from_phone: str
    message_type: Literal["text", "image", "document"]
    text_body: str | None = None
    media_id: str | None = None  # Meta's media object ID, used to fetch the actual asset
    media_mime_type: str | None = None


class ReplyDecision(BaseModel):
    """Structured output from the LLM Reasoning node."""

    reply_type: Literal["text", "image", "document"]
    text_content: str = Field(description="The message text. Always populated, even for media replies (used as caption/context).")
    media_asset_key: str | None = Field(
        default=None,
        description="Key into the tenant's media_library dict, if reply_type is image/document.",
    )
    sentiment_score: float = Field(
        ge=0.0, le=1.0,
        description="0.0 = calm/satisfied, 1.0 = highly frustrated. Used for handover routing.",
    )
    needs_human: bool = Field(default=False)
    reasoning: str = Field(default="", description="Brief internal rationale, logged but never sent to the customer.")


class DispatchResult(BaseModel):
    success: bool
    meta_message_id: str | None = None
    error_message: str | None = None


class ConversationState(TypedDict, total=False):
    # --- Identity (set once, at graph invocation) ---
    tenant_id: str
    session_id: str
    customer_phone: str
    phone_number_id: str

    # --- Acknowledge node output ---
    incoming_message: IncomingMessage
    inbound_message_doc_id: str

    # --- Context Retriever node output ---
    tenant_system_prompt: str
    media_library: dict[str, str]
    history: list[dict[str, Any]]  # serialized recent Message docs, chronological

    # --- Media Interpreter node output (conditional) ---
    media_description: str | None

    # --- LLM Reasoning node output ---
    reply_decision: ReplyDecision

    # --- Dispatcher / Handover node output ---
    dispatch_result: DispatchResult

    # --- Error short-circuit ---
    error: str | None


