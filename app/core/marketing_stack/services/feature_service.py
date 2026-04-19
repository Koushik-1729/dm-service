from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict
from uuid import UUID

from app.core.marketing_stack.outbound.repositories.marketing_event_repository import MarketingEventRepository
from app.core.marketing_stack.outbound.repositories.metrics_repository import MetricsRepository
from app.core.marketing_stack.outbound.repositories.user_repository import UserRepository


class FeatureService:
    """Builds baseline prediction features from app data."""

    def __init__(
        self,
        user_repository: UserRepository,
        marketing_event_repository: MarketingEventRepository,
        metrics_repository: MetricsRepository,
    ):
        self._users = user_repository
        self._events = marketing_event_repository
        self._metrics = metrics_repository

    async def build_user_features(self, client_id: UUID, user_id: UUID) -> Dict[str, Any]:
        user = await self._users.get_by_id(user_id)
        if not user or user.client_id != client_id:
            raise ValueError(f"User {user_id} not found")

        events = await self._events.list_by_user(user_id, limit=200)
        event_types = [event.event_type for event in events]
        last_event_at = events[0].occurred_at if events else None
        first_event = events[-1] if events else None
        primary_channel = first_event.channel if first_event else None
        metrics_summary = await self._metrics.get_summary(client_id, days=30)
        channel_metrics = metrics_summary.get(primary_channel or "", {})

        now = datetime.now(timezone.utc)
        days_since_last_event = 999
        if last_event_at:
            days_since_last_event = max(0, (now - last_event_at).days)

        leads = int(channel_metrics.get("leads", 0) or 0)
        revenue = Decimal(str(channel_metrics.get("revenue", 0) or 0))
        revenue_per_lead = Decimal("0")
        if leads > 0:
            revenue_per_lead = revenue / Decimal(leads)

        return {
            "user_id": str(user.id),
            "primary_channel": primary_channel or "unknown",
            "total_events": len(events),
            "has_registration": "registration_completed" in event_types,
            "has_thank_you": "thank_you_sent" in event_types,
            "has_followup": "followup_sent" in event_types,
            "has_survey": "survey_completed" in event_types,
            "has_conversion": any(
                event_type in {"purchase_completed", "service_signed_up", "conversion_recorded"}
                for event_type in event_types
            ),
            "days_since_last_event": days_since_last_event,
            "channel_leads_30d": leads,
            "channel_roi_30d": float(channel_metrics.get("roi", 0) or 0),
            "channel_messages_read_30d": int(channel_metrics.get("messages_read", 0) or 0),
            "channel_revenue_per_lead_30d": float(revenue_per_lead),
        }
