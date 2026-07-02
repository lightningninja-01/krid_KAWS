"""
Customer repository — profile lookups and broadcast cohort queries.
"""
from app.database.repositories.base_repository import BaseRepository
from app.models.customer import Customer


class CustomerRepository(BaseRepository[Customer]):
    collection_name = "customers"
    model_cls = Customer

    async def get_or_create(self, tenant_id: str, phone_number: str) -> Customer:
        doc = await self._collection.find_one({"tenant_id": tenant_id, "phone_number": phone_number})
        if doc is not None:
            return self._to_model(doc)
        customer = Customer(tenant_id=tenant_id, phone_number=phone_number)
        return await self.insert(customer)

    async def find_by_tags(self, tenant_id: str, tags: list[str]) -> list[Customer]:
        """Used by the Broadcast Drawer to resolve a selected cohort to phone numbers."""
        return await self.find_many_scoped(tenant_id, {"tags": {"$in": tags}})
