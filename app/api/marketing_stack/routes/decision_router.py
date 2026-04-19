from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID

from app.api.marketing_stack.marketing_dependencies import get_decision_service
from app.api.marketing_stack.models.decision_models import DecisionListResponse, DecisionResponse
from app.core.marketing_stack.services.decision_service import DecisionService

router = APIRouter(prefix="/decisions", tags=["Decisions"])


@router.post("/clients/{client_id}/users/{user_id}", response_model=DecisionResponse)
async def decide_for_user(
    client_id: UUID,
    user_id: UUID,
    service: DecisionService = Depends(get_decision_service),
) -> DecisionResponse:
    try:
        decision = await service.decide_for_user(client_id, user_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return DecisionResponse.model_validate(decision)


@router.post("/clients/{client_id}/batch", response_model=DecisionListResponse)
async def decide_for_client(
    client_id: UUID,
    limit: int = Query(default=100, ge=1, le=500),
    service: DecisionService = Depends(get_decision_service),
) -> DecisionListResponse:
    decisions = await service.decide_for_client(client_id, limit=limit)
    return DecisionListResponse(
        data=[DecisionResponse.model_validate(decision) for decision in decisions],
        total=len(decisions),
    )
