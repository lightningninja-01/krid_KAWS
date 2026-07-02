"""
Seeds the two demo tenants from the assignment's business scenario:
Tenant A (Luxury Furniture Store) and Tenant B (Automotive Care).

Run with: python -m scripts.seed_db
Requires the same .env as the main app (reads MONGODB_URI via Settings).
"""
import asyncio

from motor.motor_asyncio import AsyncIOMotorClient

from app.config.settings import get_settings
from app.models.tenant import Branding, Tenant

# NOTE: replace these placeholder media URLs with real, publicly accessible
# asset URLs before running against a live WhatsApp number — Meta's API
# fetches these URLs server-side to attach media, so they must be reachable
# from the public internet (not localhost).
TENANT_A = Tenant(
    company_name="Luxury Furniture Co.",
    phone_number_id="REPLACE_WITH_TENANT_A_PHONE_NUMBER_ID",
    system_prompt=(
        "You are a warm, knowledgeable sales assistant for Luxury Furniture Co., a high-end "
        "furniture retailer. Customers often ask about product catalogs, showroom pieces, and "
        "materials. Be helpful and concise, and offer to share the catalog or product images "
        "when a customer expresses interest in seeing items."
    ),
    media_library={
        "catalog": "https://example.com/assets/luxury-furniture/catalog.pdf",
        "sofa": "https://example.com/assets/luxury-furniture/sofa.jpg",
        "chair": "https://example.com/assets/luxury-furniture/chair.jpg",
        "showroom": "https://example.com/assets/luxury-furniture/showroom.jpg",
    },
    branding=Branding(display_name="Luxury Furniture Co.", primary_color="#B5651D"),
)

TENANT_B = Tenant(
    company_name="Automotive Care Center",
    phone_number_id="1198036343395892",
    system_prompt=(
        "You are a professional, efficient service assistant for Automotive Care Center, an "
        "auto repair and maintenance shop. Customers often ask about scheduling service, repair "
        "costs, and invoices. Be clear and precise, and offer to share the invoice sheet or "
        "repair diagrams when relevant."
    ),
    media_library={
        "invoice": "https://example.com/assets/automotive-care/invoice.pdf",
        "repair_diagram": "https://example.com/assets/automotive-care/repair.jpg",
    },
    branding=Branding(display_name="Automotive Care Center", primary_color="#2563EB"),
)


async def seed() -> None:
    settings = get_settings()
    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client[settings.mongodb_db_name]

    for tenant in (TENANT_A, TENANT_B):
        existing = await db.tenants.find_one({"company_name": tenant.company_name})
        if existing:
            await db.tenants.update_one(
                {"company_name": tenant.company_name},
                {"$set": {"phone_number_id": tenant.phone_number_id, "system_prompt": tenant.system_prompt, "media_library": tenant.media_library}}
            )
            print(f"Updated tenant '{tenant.company_name}' with new phone ID.")
            continue
        await db.tenants.insert_one(tenant.to_mongo())
        print(f"Seeded tenant: {tenant.company_name}")

    client.close()


if __name__ == "__main__":
    asyncio.run(seed())
