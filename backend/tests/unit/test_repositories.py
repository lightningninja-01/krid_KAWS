"""
Repository tests, backed by mongomock-motor (an in-memory Motor-compatible
mock) — verifies actual query behavior, not just mocked calls. Focused on
the thing that matters most: tenant isolation cannot be bypassed.
"""
import pytest
from mongomock_motor import AsyncMongoMockClient

from app.database.repositories.message_repository import MessageRepository
from app.database.repositories.session_repository import SessionRepository
from app.models.message import Message, MessageSender, MessageType
from app.models.session import Session


@pytest.fixture
def db():
    return AsyncMongoMockClient()["test_db"]


class TestSessionRepositoryTenantIsolation:
    async def test_find_many_scoped_never_returns_other_tenants_data(self, db):
        repo = SessionRepository(db)
        await repo.insert(Session(tenant_id="tenant_a", customer_phone="111"))
        await repo.insert(Session(tenant_id="tenant_b", customer_phone="222"))

        results = await repo.find_many_scoped("tenant_a")

        assert len(results) == 1
        assert results[0].tenant_id == "tenant_a"

    async def test_get_or_create_is_idempotent_per_tenant_and_phone(self, db):
        repo = SessionRepository(db)
        first = await repo.get_or_create("tenant_a", "111")
        second = await repo.get_or_create("tenant_a", "111")

        assert first.id == second.id

    async def test_same_phone_number_different_tenants_are_distinct_sessions(self, db):
        repo = SessionRepository(db)
        session_a = await repo.get_or_create("tenant_a", "111")
        session_b = await repo.get_or_create("tenant_b", "111")

        assert session_a.id != session_b.id


class TestMessageRepositoryHistoryOrdering:
    async def test_recent_history_is_chronological_and_limited(self, db):
        repo = MessageRepository(db)
        for i in range(7):
            await repo.insert(
                Message(
                    tenant_id="t1",
                    session_id="s1",
                    sender=MessageSender.CUSTOMER,
                    message_type=MessageType.TEXT,
                    text=f"message {i}",
                )
            )

        history = await repo.get_recent_history("t1", "s1", limit=5)

        assert len(history) == 5
        # Oldest-first, and it should be the *last* 5, not the first 5.
        assert [m.text for m in history] == ["message 2", "message 3", "message 4", "message 5", "message 6"]
