from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional
from uuid import UUID


class MarketingEvent:
    """Immutable event in the customer journey."""

    def __init__(
        self,
        id: Optional[UUID] = None,
        client_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        event_type: str = "",
        occurred_at: Optional[datetime] = None,
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
        created_at: Optional[datetime] = None,
    ):
        self.id = id
        self.client_id = client_id
        self.user_id = user_id
        self.event_type = event_type
        self.occurred_at = occurred_at
        self.channel = channel
        self.campaign_id = campaign_id
        self.adset_id = adset_id
        self.creative_id = creative_id
        self.message_id = message_id
        self.session_id = session_id
        self.source_id = source_id
        self.revenue_amount = revenue_amount
        self.currency = currency
        self.metadata = metadata or {}
        self.created_at = created_at
