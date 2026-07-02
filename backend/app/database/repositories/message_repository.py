"""
Message repository — audit log writes and the "last 5 messages" read used
by the Context Retriever node.
"""
from app.database.repositories.base_repository import BaseRepository
from app.models.message import Message


class MessageRepository(BaseRepository[Message]):
    collection_name = "messages"
    model_cls = Message

    async def get_recent_history(self, tenant_id: str, session_id: str, limit: int = 5) -> list[Message]:
        """
        Returns the last `limit` messages, oldest-first, ready to be dropped
        directly into the LLM's conversation context.
        """
        messages = await self.find_many_scoped(
            tenant_id,
            {"session_id": session_id},
            sort=[("created_at", -1), ("_id", -1)],
            limit=limit,
        )
        return list(reversed(messages))  # chronological order for prompt construction

    async def list_for_session(self, tenant_id: str, session_id: str) -> list[Message]:
        """Full history for the dashboard's conversation window."""
        return await self.find_many_scoped(
            tenant_id,
            {"session_id": session_id},
            sort=[("created_at", 1), ("_id", 1)],
        )
