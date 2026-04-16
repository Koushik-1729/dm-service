"""Phase 2: Dashboard API — Client management endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from uuid import UUID

from app.api.marketing_stack.models.client_models import ClientResponse, ClientListResponse
from app.api.marketing_stack.marketing_dependencies import get_client_repository
from app.core.marketing_stack.outbound.repositories.client_repository import ClientRepository

router = APIRouter(prefix="/clients", tags=["Clients"])


@router.get("", response_model=ClientListResponse)
async def list_clients(
    repo: ClientRepository = Depends(get_client_repository),
) -> ClientListResponse:
    clients = await repo.list_active()
    return ClientListResponse(
        data=[ClientResponse(
            id=c.id, phone_number=c.phone_number, business_name=c.business_name,
            owner_name=c.owner_name, sector=c.sector, city=c.city, locality=c.locality,
            language=c.language, onboarding_status=c.onboarding_status,
            subscription_tier=c.subscription_tier, autonomy_level=c.autonomy_level,
            is_active=c.is_active, created_at=c.created_at,
        ) for c in clients],
        total=len(clients),
    )


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: UUID,
    repo: ClientRepository = Depends(get_client_repository),
) -> ClientResponse:
    client = await repo.get_by_id(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return ClientResponse(
        id=client.id, phone_number=client.phone_number, business_name=client.business_name,
        owner_name=client.owner_name, sector=client.sector, city=client.city,
        locality=client.locality, language=client.language,
        onboarding_status=client.onboarding_status, subscription_tier=client.subscription_tier,
        autonomy_level=client.autonomy_level, is_active=client.is_active,
        created_at=client.created_at,
    )
