"""
Session document model — one per (tenant, customer_phone) pair.
Represents the ongoing chat relationship, per assignment spec.
"""
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from bson import ObjectId
from pydantic import BaseModel, Field, field_validator


class SessionStatus(StrEnum):
    """Exact enum values specified by the assignment."""

    WAITING_FOR_BOT = "WAITING_FOR_BOT"
    AGENT_RESPONDING = "AGENT_RESPONDING"
    RESOLVED = "RESOLVED"
    NEEDS_HUMAN = "NEEDS_HUMAN"  # bonus: sentiment-triggered handover


class Session(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    tenant_id: str
    customer_phone: str
    status: SessionStatus = SessionStatus.WAITING_FOR_BOT
    context_variables: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_message_at: datetime | None = None

    model_config = {"populate_by_name": True, "arbitrary_types_allowed": True}

    @field_validator("id", mode="before")
    @classmethod
    def _stringify_object_id(cls, value: Any) -> str:
        return str(value) if isinstance(value, ObjectId) else value

    def to_mongo(self) -> dict[str, Any]:
        data = self.model_dump(by_alias=True, exclude={"id"})
        data["_id"] = ObjectId(self.id) if ObjectId.is_valid(self.id) else self.id
        return data
