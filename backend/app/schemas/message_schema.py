"""
API contract schemas for message endpoints — used by the dashboard's
Conversation Window (message bubbles, media previews, typing metadata).
"""
from datetime import datetime

from pydantic import BaseModel

from app.models.message import MediaAttachment, MessageSender, MessageStatus, MessageType


class MessageResponse(BaseModel):
    id: str
    session_id: str
    sender: MessageSender
    message_type: MessageType
    text: str | None
    media: MediaAttachment | None
    status: MessageStatus
    metadata: dict
    created_at: datetime
