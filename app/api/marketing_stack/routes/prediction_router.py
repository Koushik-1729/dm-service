from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID

from app.api.marketing_stack.marketing_dependencies import get_prediction_service
from app.api.marketing_stack.models.prediction_models import PredictionListResponse, PredictionResponse
from app.core.marketing_stack.services.prediction_service import PredictionService

router = APIRouter(prefix="/predictions", tags=["Predictions"])


@router.post("/clients/{client_id}/users/{user_id}", response_model=PredictionResponse)
async def score_user(
    client_id: UUID,
    user_id: UUID,
    service: PredictionService = Depends(get_prediction_service),
) -> PredictionResponse:
    try:
        prediction = await service.score_user(client_id, user_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return PredictionResponse.model_validate(prediction)


@router.post("/clients/{client_id}/batch", response_model=PredictionListResponse)
async def score_client_users(
    client_id: UUID,
    limit: int = Query(default=100, ge=1, le=500),
    service: PredictionService = Depends(get_prediction_service),
) -> PredictionListResponse:
    predictions = await service.score_client_users(client_id, limit=limit)
    return PredictionListResponse(
        data=[PredictionResponse.model_validate(prediction) for prediction in predictions],
        total=len(predictions),
    )
