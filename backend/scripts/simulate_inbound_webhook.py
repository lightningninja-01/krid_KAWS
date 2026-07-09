import asyncio
import hashlib
import hmac
import json
import time

import httpx

from app.config.settings import get_settings


async def main() -> None:
    settings = get_settings()
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "local-test-entry",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "+1 555-657-1495",
                                "phone_number_id": settings.meta_phone_number_id,
                            },
                            "contacts": [
                                {
                                    "wa_id": "919399423431",
                                    "profile": {"name": "Local Test Customer"},
                                }
                            ],
                            "messages": [
                                {
                                    "id": f"wamid.localtest.{int(time.time())}",
                                    "from": "919399423431",
                                    "timestamp": str(int(time.time())),
                                    "type": "text",
                                    "text": {"body": "Hi, do you offer oil change?"},
                                }
                            ],
                        },
                    }
                ],
            }
        ],
    }
    raw_body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    signature = hmac.new(
        settings.meta_app_secret.encode("utf-8"),
        raw_body,
        hashlib.sha256,
    ).hexdigest()

    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.post(
            "http://127.0.0.1:8000/api/webhooks/whatsapp",
            content=raw_body,
            headers={
                "Content-Type": "application/json",
                "X-Hub-Signature-256": f"sha256={signature}",
            },
        )
    print(f"status={response.status_code}")
    print(response.text[:300])


if __name__ == "__main__":
    asyncio.run(main())
