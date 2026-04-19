from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID


class RevenueEvent:
    """Represents realized revenue tied to a user and conversion."""

    def __init__(
        self,
        id: Optional[UUID] = None,
        client_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        conversion_event_id: Optional[UUID] = None,
        amount: Decimal = Decimal("0"),
        currency: str = "INR",
        payment_reference: Optional[str] = None,
        occurred_at: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
    ):
        self.id = id
        self.client_id = client_id
        self.user_id = user_id
        self.conversion_event_id = conversion_event_id
        self.amount = amount
        self.currency = currency
        self.payment_reference = payment_reference
        self.occurred_at = occurred_at
        self.created_at = created_at
