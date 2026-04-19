from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, Optional
from uuid import uuid4

from app.core.marketing_stack.models.conversion_event import ConversionEvent
from app.core.marketing_stack.models.marketing_event import MarketingEvent
from app.core.marketing_stack.models.revenue_event import RevenueEvent
from app.core.marketing_stack.services.identity_service import IdentityService
from app.core.marketing_stack.outbound.repositories.conversion_event_repository import ConversionEventRepository
from app.core.marketing_stack.outbound.repositories.marketing_event_repository import MarketingEventRepository
from app.core.marketing_stack.outbound.repositories.revenue_event_repository import RevenueEventRepository


class EventIngestionService:
    """Ingests journey events and persists related conversion/revenue state."""

    CONVERSION_EVENT_TYPES = {"purchase_completed", "service_signed_up", "conversion_recorded"}
    REVENUE_EVENT_TYPES = {"purchase_completed", "payment_captured", "revenue_recorded"}

    def __init__(
        self,
        identity_service: IdentityService,
        marketing_event_repository: MarketingEventRepository,
        conversion_event_repository: ConversionEventRepository,
        revenue_event_repository: RevenueEventRepository,
    ):
        self._identity = identity_service
        self._events = marketing_event_repository
        self._conversions = conversion_event_repository
        self._revenues = revenue_event_repository

    async def ingest_event(
        self,
        *,
        client_id,
        event_type: str,
        occurred_at: Optional[datetime] = None,
        external_ref: Optional[str] = None,
        email: Optional[str] = None,
        phone_number: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        channel: Optional[str] = None,
        campaign_id: Optional[str] = None,
        adset_id: Optional[str] = None,
        creative_id: Optional[str] = None,
        message_id: Optional[str] = None,
        session_id: Optional[str] = None,
        source_id: Optional[str] = None,
        revenue_amount: Optional[Decimal] = None,
        currency: str = "INR",
        metadata: Optional[Dict[str, Any]] = None,
        conversion_type: Optional[str] = None,
        payment_reference: Optional[str] = None,
    ) -> Dict[str, Any]:
        user = await self._identity.resolve_user(
            client_id=client_id,
            external_ref=external_ref,
            email=email,
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
        )

        event = await self._events.create(
            MarketingEvent(
                id=uuid4(),
                client_id=client_id,
                user_id=user.id,
                event_type=event_type,
                occurred_at=self._normalize_datetime(occurred_at),
                channel=channel,
                campaign_id=campaign_id,
                adset_id=adset_id,
                creative_id=creative_id,
                message_id=message_id,
                session_id=session_id,
                source_id=source_id,
                revenue_amount=revenue_amount,
                currency=currency,
                metadata=metadata or {},
            )
        )

        conversion = None
        if event_type in self.CONVERSION_EVENT_TYPES:
            conversion = await self._conversions.create(
                ConversionEvent(
                    id=uuid4(),
                    client_id=client_id,
                    user_id=user.id,
                    marketing_event_id=event.id,
                    conversion_type=conversion_type or event_type,
                    conversion_value=revenue_amount,
                    currency=currency,
                    occurred_at=event.occurred_at,
                )
            )

        revenue = None
        if revenue_amount is not None and event_type in self.REVENUE_EVENT_TYPES:
            revenue = await self._revenues.create(
                RevenueEvent(
                    id=uuid4(),
                    client_id=client_id,
                    user_id=user.id,
                    conversion_event_id=conversion.id if conversion else None,
                    amount=revenue_amount,
                    currency=currency,
                    payment_reference=payment_reference,
                    occurred_at=event.occurred_at,
                )
            )

        return {
            "user": user,
            "marketing_event": event,
            "conversion_event": conversion,
            "revenue_event": revenue,
        }

    def _normalize_datetime(self, value: Optional[datetime]) -> datetime:
        if value is None:
            return datetime.now(timezone.utc)
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value
