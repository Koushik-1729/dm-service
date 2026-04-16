from pydantic import BaseModel
from typing import Dict, Any, Optional
from uuid import UUID


class WeeklyReportResponse(BaseModel):
    client_id: UUID
    report_text: str
    metrics_summary: Dict[str, Any]
    leads_by_source: Dict[str, int]
    period_days: int = 7


class RevenueCheckResponse(BaseModel):
    client_id: UUID
    total_leads: int
    confirmed_customers: Optional[int] = None
    estimated_revenue: Optional[float] = None
