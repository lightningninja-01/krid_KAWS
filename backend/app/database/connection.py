"""
MongoDB connection lifecycle, using Motor (async driver).

A single AsyncIOMotorClient is created on app startup and reused for the
process lifetime (Motor manages its own connection pool internally — do
NOT create a new client per request, that defeats pooling entirely).
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config.settings import get_settings
from app.utils.logger import get_logger

log = get_logger(__name__)


class MongoConnection:
    """
    Thin wrapper around the Motor client so we have one place to manage
    connect/disconnect and one place tests can mock/override.
    """

    def __init__(self) -> None:
        self._client: AsyncIOMotorClient | None = None
        self._db: AsyncIOMotorDatabase | None = None

    async def connect(self) -> None:
        settings = get_settings()
        self._client = AsyncIOMotorClient(settings.mongodb_uri)
        self._db = self._client[settings.mongodb_db_name]
        # Fail fast on startup if Atlas is unreachable, rather than on first request.
        await self._client.admin.command("ping")
        await self._ensure_indexes()
        log.info(f"Connected to MongoDB database '{settings.mongodb_db_name}'")

    async def disconnect(self) -> None:
        if self._client is not None:
            self._client.close()
            log.info("MongoDB connection closed")

    @property
    def db(self) -> AsyncIOMotorDatabase:
        if self._db is None:
            raise RuntimeError("MongoDB connection not initialized — call connect() during app startup")
        return self._db

    async def _ensure_indexes(self) -> None:
        """
        Indexes that matter for this access pattern:
        - tenants: unique lookup by external tenant slug (used by webhook routing)
        - sessions: compound lookup by (tenant_id, customer_phone) — the hot path
          for every inbound message
        - messages: lookup by session_id ordered by timestamp — used by
          Context Retriever's "last 5 messages" query
        """
        await self._db.tenants.create_index("phone_number_id", unique=True)
        await self._db.sessions.create_index([("tenant_id", 1), ("customer_phone", 1)], unique=True)
        await self._db.messages.create_index([("session_id", 1), ("created_at", -1)])
        await self._db.customers.create_index([("tenant_id", 1), ("phone_number", 1)], unique=True)


mongo_connection = MongoConnection()


def get_database() -> AsyncIOMotorDatabase:
    """FastAPI dependency: returns the active database handle."""
    return mongo_connection.db
