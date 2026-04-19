from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional
from uuid import UUID


class DecisionLog:
    """Represents a next-best-action decision for a user."""

    def __init__(
        self,
        id: Optional[UUID] = None,
        client_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        prediction_score_id: Optional[UUID] = None,
        action_type: str = "",
        action_payload: Optional[Dict[str, Any]] = None,
        confidence: float = 0.0,
        expected_revenue_impact: Decimal = Decimal("0"),
        reason: str = "",
        status: str = "recommended",
        created_at: Optional[datetime] = None,
    ):
        self.id = id
        self.client_id = client_id
        self.user_id = user_id
        self.prediction_score_id = prediction_score_id
        self.action_type = action_type
        self.action_payload = action_payload or {}
        self.confidence = confidence
        self.expected_revenue_impact = expected_revenue_impact
        self.reason = reason
        self.status = status
        self.created_at = created_at
