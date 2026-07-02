"""
API contract schemas for the Broadcast Campaign Drawer.
"""
from pydantic import BaseModel, Field


class BroadcastRequest(BaseModel):
    tenant_id: str
    target_tags: list[str] = Field(..., description="Customer tags defining the cohort, e.g. ['vip', 'furniture_interest']")
    template_name: str = Field(..., description="Meta-approved WhatsApp message template name")
    template_params: list[str] = Field(default_factory=list, description="Positional params for the template body")


class BroadcastResult(BaseModel):
    tenant_id: str
    total_targeted: int
    total_sent: int
    total_failed: int
    failed_numbers: list[str] = []
