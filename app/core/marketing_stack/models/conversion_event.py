from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID


class ConversionEvent:
    """Represents a conversion linked to a user journey."""

    def __init__(
        self,
        id: Optional[UUID] = None,
        client_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        marketing_event_id: Optional[UUID] = None,
        conversion_type: str = "",
        conversion_value: Optional[Decimal] = None,
        currency: str = "INR",
        occurred_at: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
    ):
        self.id = id
        self.client_id = client_id
        self.user_id = user_id
        self.marketing_event_id = marketing_event_id
        self.conversion_type = conversion_type
        self.conversion_value = conversion_value
        self.currency = currency
        self.occurred_at = occurred_at
        self.created_at = created_at
