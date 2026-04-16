from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal


class LeadResponse(BaseModel):
    id: UUID
    client_id: UUID
    name: Optional[str] = None
    phone_number: str
    source_channel: str
    source_campaign_tag: Optional[str] = None
    status: str
    revenue_amount: Optional[Decimal] = None
    followup_count: int = 0
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class LeadListResponse(BaseModel):
    data: List[LeadResponse]
    total: int


class LeadConvertRequest(BaseModel):
    lead_id: UUID
    revenue_amount: Decimal
