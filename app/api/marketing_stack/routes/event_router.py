from fastapi import APIRouter, Depends

from app.api.marketing_stack.marketing_dependencies import get_event_ingestion_service
from app.api.marketing_stack.models.event_models import EventIngestRequest, EventIngestResponse
from app.core.marketing_stack.services.event_ingestion_service import EventIngestionService

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("", response_model=EventIngestResponse)
async def ingest_event(
    payload: EventIngestRequest,
    service: EventIngestionService = Depends(get_event_ingestion_service),
) -> EventIngestResponse:
    result = await service.ingest_event(
        client_id=payload.client_id,
        event_type=payload.event_type,
        occurred_at=payload.occurred_at,
        external_ref=payload.external_ref,
        email=payload.email,
        phone_number=payload.phone_number,
        first_name=payload.first_name,
        last_name=payload.last_name,
        channel=payload.channel,
        campaign_id=payload.campaign_id,
        adset_id=payload.adset_id,
        creative_id=payload.creative_id,
        message_id=payload.message_id,
        session_id=payload.session_id,
        source_id=payload.source_id,
        revenue_amount=payload.revenue_amount,
        currency=payload.currency,
        metadata=payload.metadata,
        conversion_type=payload.conversion_type,
        payment_reference=payload.payment_reference,
    )

    return EventIngestResponse(
        user_id=result["user"].id,
        marketing_event_id=result["marketing_event"].id,
        conversion_event_id=result["conversion_event"].id if result["conversion_event"] else None,
        revenue_event_id=result["revenue_event"].id if result["revenue_event"] else None,
        event_type=result["marketing_event"].event_type,
        occurred_at=result["marketing_event"].occurred_at,
    )
