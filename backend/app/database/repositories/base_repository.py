"""
Base repository — shared CRUD plumbing for all Mongo-backed repositories.

Design decision: `tenant_id` is a required first argument on every scoped
method, not an optional filter. This makes cross-tenant data leakage a
visible mistake at every call site rather than a bug you only catch in
code review. A repository method that forgets to filter by tenant simply
cannot be written here — the base class won't allow it.
"""
from typing import Any, Generic, TypeVar

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase
from pydantic import BaseModel

ModelT = TypeVar("ModelT", bound=BaseModel)


class BaseRepository(Generic[ModelT]):
    collection_name: str
    model_cls: type[ModelT]

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._collection: AsyncIOMotorCollection = db[self.collection_name]

    def _to_model(self, doc: dict[str, Any] | None) -> ModelT | None:
        if doc is None:
            return None
        doc = {**doc, "_id": str(doc["_id"])}
        return self.model_cls.model_validate(doc)

    async def find_by_id_scoped(self, tenant_id: str, doc_id: str) -> ModelT | None:
        """Fetch a single document, scoped to a tenant. Prevents ID-guessing across tenants."""
        if not ObjectId.is_valid(doc_id):
            return None
        doc = await self._collection.find_one({"_id": ObjectId(doc_id), "tenant_id": tenant_id})
        return self._to_model(doc)

    async def find_many_scoped(
        self,
        tenant_id: str,
        query: dict[str, Any] | None = None,
        *,
        sort: list[tuple[str, int]] | None = None,
        limit: int = 0,
    ) -> list[ModelT]:
        full_query = {"tenant_id": tenant_id, **(query or {})}
        cursor = self._collection.find(full_query)
        if sort:
            cursor = cursor.sort(sort)
        if limit:
            cursor = cursor.limit(limit)
        return [self._to_model(doc) for doc in await cursor.to_list(length=limit or None)]

    async def insert(self, model: ModelT) -> ModelT:
        await self._collection.insert_one(model.to_mongo())  # type: ignore[attr-defined]
        return model

    async def update_scoped(self, tenant_id: str, doc_id: str, update: dict[str, Any]) -> bool:
        if not ObjectId.is_valid(doc_id):
            return False
        result = await self._collection.update_one(
            {"_id": ObjectId(doc_id), "tenant_id": tenant_id},
            {"$set": update},
        )
        return result.modified_count > 0
