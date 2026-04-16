from datetime import datetime
from typing import Optional
from uuid import UUID
from decimal import Decimal


class Lead:
    """Domain model representing a captured lead from marketing campaigns."""

    def __init__(
        self,
        id: Optional[UUID] = None,
        client_id: Optional[UUID] = None,
        campaign_id: Optional[UUID] = None,
        name: Optional[str] = None,
        phone_number: str = "",
        source_channel: str = "",
        source_campaign_tag: Optional[str] = None,
        status: str = "new",
        notes: Optional[str] = None,
        revenue_amount: Optional[Decimal] = None,
        payment_verified: bool = False,
        followup_count: int = 0,
        last_followup_at: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.client_id = client_id
        self.campaign_id = campaign_id
        self.name = name
        self.phone_number = phone_number
        self.source_channel = source_channel
        self.source_campaign_tag = source_campaign_tag
        self.status = status
        self.notes = notes
        self.revenue_amount = revenue_amount
        self.payment_verified = payment_verified
        self.followup_count = followup_count
        self.last_followup_at = last_followup_at
        self.created_at = created_at
        self.updated_at = updated_at

    def mark_contacted(self) -> None:
        self.status = "contacted"
        self.updated_at = datetime.utcnow()

    def mark_converted(self, revenue: Decimal) -> None:
        self.status = "converted"
        self.revenue_amount = revenue
        self.updated_at = datetime.utcnow()

    def mark_lost(self) -> None:
        self.status = "lost"
        self.updated_at = datetime.utcnow()

    def increment_followup(self) -> None:
        self.followup_count += 1
        self.last_followup_at = datetime.utcnow()

    def needs_followup(self, max_followups: int = 3) -> bool:
        return (
            self.status in ("new", "notified")
            and self.followup_count < max_followups
        )
