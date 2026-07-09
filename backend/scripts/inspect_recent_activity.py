import asyncio
from pprint import pprint

from motor.motor_asyncio import AsyncIOMotorClient

from app.config.settings import get_settings


async def main() -> None:
    settings = get_settings()
    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client[settings.mongodb_db_name]

    print("tenants", await db.tenants.count_documents({}))
    print("sessions", await db.sessions.count_documents({}))
    print("messages", await db.messages.count_documents({}))

    print("\nrecent sessions")
    sessions = await db.sessions.find(
        {},
        {"tenant_id": 1, "customer_phone": 1, "status": 1, "last_message_at": 1, "updated_at": 1},
    ).sort("updated_at", -1).limit(5).to_list(5)
    for session in sessions:
        session["_id"] = str(session["_id"])
        pprint(session)

    print("\nrecent messages")
    messages = await db.messages.find(
        {},
        {
            "tenant_id": 1,
            "session_id": 1,
            "sender": 1,
            "message_type": 1,
            "text": 1,
            "status": 1,
            "metadata": 1,
            "created_at": 1,
        },
    ).sort("created_at", -1).limit(8).to_list(8)
    for message in messages:
        message["_id"] = str(message["_id"])
        pprint(message)

    client.close()


if __name__ == "__main__":
    asyncio.run(main())
