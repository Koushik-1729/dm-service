from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal


class DailyMetricsResponse(BaseModel):
    id: UUID
    client_id: UUID
    date: date
    channel: str
    impressions: int = 0
    reach: int = 0
    engagement: int = 0
    clicks: int = 0
    leads_count: int = 0
    revenue: Decimal = Decimal("0")
    spend: Decimal = Decimal("0")
    followers_gained: int = 0

    model_config = ConfigDict(from_attributes=True)


class MetricsSummaryResponse(BaseModel):
    client_id: UUID
    period_days: int
    channels: Dict[str, Any]
    total_spend: float
    total_revenue: float
    overall_roi: float
