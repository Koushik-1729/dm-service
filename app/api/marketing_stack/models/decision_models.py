from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DecisionResponse(BaseModel):
    id: UUID
    client_id: UUID
    user_id: UUID
    prediction_score_id: UUID | None = None
    action_type: str
    action_payload: Dict[str, Any]
    confidence: float
    expected_revenue_impact: Decimal
    reason: str
    status: str
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class DecisionListResponse(BaseModel):
    data: List[DecisionResponse]
    total: int
