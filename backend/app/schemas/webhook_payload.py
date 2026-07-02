"""
Schema for Meta's WhatsApp Cloud API webhook payload.

This mirrors Meta's actual wire format, which is deeply nested and mostly
optional (a single webhook call can carry messages, status updates, or
both, and any given message may be text/image/document/etc.). Rather than
strict-validate every possible field, we parse permissively and expose a
convenience accessor that extracts what the Acknowledge node actually
needs — keeps the rest of the codebase from having to know Meta's payload
shape at all.
"""
from pydantic import BaseModel


class WebhookTextContent(BaseModel):
    body: str


class WebhookMediaContent(BaseModel):
    id: str
    mime_type: str | None = None
    sha256: str | None = None
    caption: str | None = None


class WebhookInboundMessage(BaseModel):
    id: str
    from_: str  # 'from' is a reserved word in Python
    timestamp: str
    type: str  # "text" | "image" | "document" | ...
    text: WebhookTextContent | None = None
    image: WebhookMediaContent | None = None
    document: WebhookMediaContent | None = None

    model_config = {"populate_by_name": True}

    def __init__(self, **data):
        if "from" in data:
            data["from_"] = data.pop("from")
        super().__init__(**data)


class WebhookMetadata(BaseModel):
    display_phone_number: str | None = None
    phone_number_id: str


class WebhookContact(BaseModel):
    wa_id: str
    profile: dict | None = None


class WebhookValue(BaseModel):
    messaging_product: str
    metadata: WebhookMetadata
    contacts: list[WebhookContact] | None = None
    messages: list[WebhookInboundMessage] | None = None
    statuses: list[dict] | None = None  # delivery/read status callbacks — not processed by the graph


class WebhookChange(BaseModel):
    value: WebhookValue
    field: str


class WebhookEntry(BaseModel):
    id: str
    changes: list[WebhookChange]


class WebhookPayload(BaseModel):
    object: str
    entry: list[WebhookEntry]

    def extract_first_message(self) -> tuple[WebhookInboundMessage, str] | None:
        """
        Returns (message, phone_number_id) for the first actual inbound
        message in this payload, or None if this webhook call only carried
        status callbacks (delivery/read receipts) with no new message.
        """
        for entry in self.entry:
            for change in entry.changes:
                if change.value.messages:
                    return change.value.messages[0], change.value.metadata.phone_number_id
        return None
