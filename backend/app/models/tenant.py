"""
Tenant document model — represents a company using the SaaS
(e.g. "Luxury Furniture Store", "Automotive Care").
"""
from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from pydantic import BaseModel, Field, field_validator


class Branding(BaseModel):
    display_name: str
    primary_color: str = "#4F46E5"
    logo_url: str | None = None


class Tenant(BaseModel):
    """
    Mongo document shape for the `tenants` collection.

    media_library maps a query term to a publicly accessible asset URL, per
    the assignment spec, e.g. {"catalog": "https://.../catalog.pdf"}.
    The LLM reasons over this map's keys (not literal keyword matching) to
    pick the right asset for a given customer intent.
    """

    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    company_name: str
    phone_number_id: str  # Meta's Phone Number ID — used to route inbound webhooks to this tenant
    system_prompt: str  # tenant-specific instructions injected into the LLM Reasoning node
    media_library: dict[str, str] = Field(default_factory=dict)
    branding: Branding
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"populate_by_name": True, "arbitrary_types_allowed": True}

    @field_validator("id", mode="before")
    @classmethod
    def _stringify_object_id(cls, value: Any) -> str:
        return str(value) if isinstance(value, ObjectId) else value

    def to_mongo(self) -> dict[str, Any]:
        """Serialize for insertion, converting the string id back to ObjectId."""
        data = self.model_dump(by_alias=True, exclude={"id"})
        data["_id"] = ObjectId(self.id) if ObjectId.is_valid(self.id) else self.id
        return data
