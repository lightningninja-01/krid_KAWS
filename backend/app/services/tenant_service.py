"""
Tenant service — thin business-logic layer over TenantRepository.
Kept separate from the repository so validation/business rules (e.g. future
plan limits, media library size caps) have a natural home that isn't the
router or the raw DB layer.
"""
from app.database.repositories.tenant_repository import TenantRepository
from app.models.tenant import Tenant
from app.schemas.tenant_schema import TenantCreateRequest, TenantResponse


class TenantService:
    def __init__(self, tenant_repo: TenantRepository) -> None:
        self._tenant_repo = tenant_repo

    async def create_tenant(self, payload: TenantCreateRequest) -> TenantResponse:
        tenant = Tenant(
            company_name=payload.company_name,
            phone_number_id=payload.phone_number_id,
            system_prompt=payload.system_prompt,
            media_library=payload.media_library,
            branding=payload.branding.model_dump(),
        )
        await self._tenant_repo.insert(tenant)
        return self._to_response(tenant)

    async def get_tenant(self, tenant_id: str) -> TenantResponse:
        tenant = await self._tenant_repo.get_by_id(tenant_id)
        return self._to_response(tenant)

    async def list_tenants(self) -> list[TenantResponse]:
        tenants = await self._tenant_repo.list_all()
        return [self._to_response(t) for t in tenants]

    @staticmethod
    def _to_response(tenant: Tenant) -> TenantResponse:
        return TenantResponse(
            id=tenant.id,
            company_name=tenant.company_name,
            phone_number_id=tenant.phone_number_id,
            system_prompt=tenant.system_prompt,
            media_library=tenant.media_library,
            branding=tenant.branding.model_dump(),
        )
