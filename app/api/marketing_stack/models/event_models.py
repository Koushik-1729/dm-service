from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EventIngestRequest(BaseModel):
    client_id: UUID
    event_type: str
    occurred_at: Optional[datetime] = None
    external_ref: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    channel: Optional[str] = None
    campaign_id: Optional[str] = None
    adset_id: Optional[str] = None
    creative_id: Optional[str] = None
    message_id: Optional[str] = None
    session_id: Optional[str] = None
    source_id: Optional[str] = None
    revenue_amount: Optional[Decimal] = None
    currency: str = "INR"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    conversion_type: Optional[str] = None
    payment_reference: Optional[str] = None


class EventIngestResponse(BaseModel):
    user_id: UUID
    marketing_event_id: UUID
    conversion_event_id: Optional[UUID] = None
    revenue_event_id: Optional[UUID] = None
    event_type: str
    occurred_at: datetime

    model_config = ConfigDict(from_attributes=True)
