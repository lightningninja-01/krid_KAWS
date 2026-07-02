"""
Broadcast endpoint — triggered by the dashboard's Broadcast Campaign Drawer.
"""
from fastapi import APIRouter, Depends

from app.api.deps import get_broadcast_service
from app.schemas.broadcast_schema import BroadcastRequest, BroadcastResult
from app.services.broadcast_service import BroadcastService

router = APIRouter()


@router.post("", response_model=BroadcastResult)
async def send_broadcast(
    payload: BroadcastRequest, service: BroadcastService = Depends(get_broadcast_service)
) -> BroadcastResult:
    return await service.send_broadcast(payload)
