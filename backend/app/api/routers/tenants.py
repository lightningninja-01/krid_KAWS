"""
Tenant endpoints — powers the dashboard's Tenant Switcher and lets you
seed/manage tenants without touching Mongo directly.
"""
from fastapi import APIRouter, Depends

from app.api.deps import get_tenant_service
from app.schemas.tenant_schema import TenantCreateRequest, TenantResponse
from app.services.tenant_service import TenantService

router = APIRouter()


@router.get("", response_model=list[TenantResponse])
async def list_tenants(service: TenantService = Depends(get_tenant_service)) -> list[TenantResponse]:
    return await service.list_tenants()


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(tenant_id: str, service: TenantService = Depends(get_tenant_service)) -> TenantResponse:
    return await service.get_tenant(tenant_id)


@router.post("", response_model=TenantResponse, status_code=201)
async def create_tenant(
    payload: TenantCreateRequest, service: TenantService = Depends(get_tenant_service)
) -> TenantResponse:
    return await service.create_tenant(payload)
