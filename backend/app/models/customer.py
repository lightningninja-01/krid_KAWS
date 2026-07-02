"""
Customer document model — lightweight profile per (tenant, phone number),
mainly useful for broadcast targeting (cohort selection) and dashboard display.
"""
from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from pydantic import BaseModel, Field, field_validator


class Customer(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    tenant_id: str
    phone_number: str
    display_name: str | None = None
    tags: list[str] = Field(default_factory=list)  # used for broadcast cohort selection
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"populate_by_name": True, "arbitrary_types_allowed": True}

    @field_validator("id", mode="before")
    @classmethod
    def _stringify_object_id(cls, value: Any) -> str:
        return str(value) if isinstance(value, ObjectId) else value

    def to_mongo(self) -> dict[str, Any]:
        data = self.model_dump(by_alias=True, exclude={"id"})
        data["_id"] = ObjectId(self.id) if ObjectId.is_valid(self.id) else self.id
        return data
