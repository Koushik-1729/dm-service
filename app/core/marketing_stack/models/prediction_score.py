from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional
from uuid import UUID


class PredictionScore:
    """Represents a persisted prediction snapshot for a user."""

    def __init__(
        self,
        id: Optional[UUID] = None,
        client_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        model_name: str = "baseline_v1",
        conversion_probability: float = 0.0,
        dropout_risk: float = 0.0,
        expected_revenue: Decimal = Decimal("0"),
        feature_snapshot: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None,
    ):
        self.id = id
        self.client_id = client_id
        self.user_id = user_id
        self.model_name = model_name
        self.conversion_probability = conversion_probability
        self.dropout_risk = dropout_risk
        self.expected_revenue = expected_revenue
        self.feature_snapshot = feature_snapshot or {}
        self.created_at = created_at
