"""
API contract schemas for session endpoints — used by the dashboard's
Live Chat List.
"""
from datetime import datetime

from pydantic import BaseModel

from app.models.session import SessionStatus


class SessionResponse(BaseModel):
    id: str
    tenant_id: str
    customer_phone: str
    status: SessionStatus
    context_variables: dict
    last_message_at: datetime | None
    created_at: datetime
