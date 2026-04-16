from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal


class CampaignResponse(BaseModel):
    id: UUID
    client_id: UUID
    channel: str
    campaign_type: str
    status: str
    platform_id: Optional[str] = None
    budget: Optional[Decimal] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class CampaignListResponse(BaseModel):
    data: List[CampaignResponse]
    total: int
