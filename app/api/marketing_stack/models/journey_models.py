from decimal import Decimal
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class JourneyRegistrationRequest(BaseModel):
    client_id: UUID
    external_ref: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    channel: Optional[str] = None
    campaign_id: Optional[str] = None
    adset_id: Optional[str] = None
    creative_id: Optional[str] = None
    session_id: Optional[str] = None
    source_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class JourneyFollowupRequest(BaseModel):
    client_id: UUID
    channel: str = "whatsapp"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class JourneySurveyRequest(BaseModel):
    client_id: UUID
    response_text: str
    response_code: Optional[str] = None
    channel: str = "whatsapp"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class JourneyConversionRequest(BaseModel):
    client_id: UUID
    conversion_type: str
    revenue_amount: Decimal
    currency: str = "INR"
    payment_reference: Optional[str] = None
    channel: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class JourneyActionResponse(BaseModel):
    user_id: UUID
    event_id: Optional[UUID] = None
    followup_sent: Optional[bool] = None
    message_id: Optional[str] = None
    conversion_event_id: Optional[UUID] = None
    revenue_event_id: Optional[UUID] = None
    reason: Optional[str] = None
