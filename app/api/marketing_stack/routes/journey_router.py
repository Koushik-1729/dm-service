from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID

from app.api.marketing_stack.marketing_dependencies import get_journey_service
from app.api.marketing_stack.models.journey_models import (
    JourneyActionResponse,
    JourneyConversionRequest,
    JourneyFollowupRequest,
    JourneyRegistrationRequest,
    JourneySurveyRequest,
)
from app.core.marketing_stack.services.journey_service import JourneyService

router = APIRouter(prefix="/journeys", tags=["Journeys"])


@router.post("/register", response_model=JourneyActionResponse)
async def register_journey_user(
    payload: JourneyRegistrationRequest,
    service: JourneyService = Depends(get_journey_service),
) -> JourneyActionResponse:
    result = await service.register_user(**payload.model_dump())
    return JourneyActionResponse(
        user_id=result["user"].id,
        event_id=result["registration_event"].id,
        message_id=result["thank_you_message_id"],
    )


@router.post("/{user_id}/follow-up", response_model=JourneyActionResponse)
async def trigger_followup(
    user_id: UUID,
    payload: JourneyFollowupRequest,
    service: JourneyService = Depends(get_journey_service),
) -> JourneyActionResponse:
    try:
        result = await service.trigger_no_conversion_followup(
            client_id=payload.client_id,
            user_id=user_id,
            channel=payload.channel,
            metadata=payload.metadata,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    survey_event = result.get("survey_event")
    return JourneyActionResponse(
        user_id=result["user"].id,
        event_id=survey_event.id if survey_event else None,
        followup_sent=result["followup_sent"],
        message_id=result.get("followup_message_id"),
        reason=result.get("reason"),
    )


@router.post("/{user_id}/survey", response_model=JourneyActionResponse)
async def record_survey(
    user_id: UUID,
    payload: JourneySurveyRequest,
    service: JourneyService = Depends(get_journey_service),
) -> JourneyActionResponse:
    try:
        result = await service.record_survey_response(
            client_id=payload.client_id,
            user_id=user_id,
            response_text=payload.response_text,
            response_code=payload.response_code,
            channel=payload.channel,
            metadata=payload.metadata,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return JourneyActionResponse(
        user_id=result["user"].id,
        event_id=result["survey_event"].id,
    )


@router.post("/{user_id}/convert", response_model=JourneyActionResponse)
async def record_conversion(
    user_id: UUID,
    payload: JourneyConversionRequest,
    service: JourneyService = Depends(get_journey_service),
) -> JourneyActionResponse:
    try:
        result = await service.record_conversion(
            client_id=payload.client_id,
            user_id=user_id,
            conversion_type=payload.conversion_type,
            revenue_amount=payload.revenue_amount,
            currency=payload.currency,
            payment_reference=payload.payment_reference,
            channel=payload.channel,
            metadata=payload.metadata,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return JourneyActionResponse(
        user_id=result["user"].id,
        event_id=result["marketing_event"].id,
        conversion_event_id=result["conversion_event"].id if result["conversion_event"] else None,
        revenue_event_id=result["revenue_event"].id if result["revenue_event"] else None,
    )
