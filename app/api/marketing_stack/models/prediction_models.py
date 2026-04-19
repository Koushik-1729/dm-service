from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PredictionResponse(BaseModel):
    id: UUID
    client_id: UUID
    user_id: UUID
    model_name: str
    conversion_probability: float
    dropout_risk: float
    expected_revenue: Decimal
    feature_snapshot: Dict[str, Any]
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class PredictionListResponse(BaseModel):
    data: List[PredictionResponse]
    total: int
