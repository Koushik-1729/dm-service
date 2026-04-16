from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from decimal import Decimal


class Usage:
    """Domain model representing a billable AI usage event."""

    def __init__(
        self,
        id: Optional[UUID] = None,
        client_id: Optional[UUID] = None,
        event_type: str = "",
        model_used: Optional[str] = None,
        tokens_input: int = 0,
        tokens_output: int = 0,
        cost_usd: Decimal = Decimal("0"),
        metadata: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None,
    ):
        self.id = id
        self.client_id = client_id
        self.event_type = event_type
        self.model_used = model_used
        self.tokens_input = tokens_input
        self.tokens_output = tokens_output
        self.cost_usd = cost_usd
        self.metadata = metadata or {}
        self.created_at = created_at

    def total_tokens(self) -> int:
        return self.tokens_input + self.tokens_output
