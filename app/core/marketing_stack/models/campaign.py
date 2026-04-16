from datetime import datetime, date
from typing import Optional, Dict, Any
from uuid import UUID
from decimal import Decimal


class Campaign:
    """Domain model representing a published/active campaign."""

    def __init__(
        self,
        id: Optional[UUID] = None,
        client_id: Optional[UUID] = None,
        content_id: Optional[UUID] = None,
        channel: str = "",
        campaign_type: str = "",
        status: str = "scheduled",
        platform_id: Optional[str] = None,
        target_audience: Optional[Dict[str, Any]] = None,
        budget: Optional[Decimal] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.client_id = client_id
        self.content_id = content_id
        self.channel = channel
        self.campaign_type = campaign_type
        self.status = status
        self.platform_id = platform_id
        self.target_audience = target_audience or {}
        self.budget = budget
        self.start_date = start_date
        self.end_date = end_date
        self.created_at = created_at
        self.updated_at = updated_at

    def pause(self) -> None:
        self.status = "paused"
        self.updated_at = datetime.utcnow()

    def resume(self) -> None:
        self.status = "running"
        self.updated_at = datetime.utcnow()

    def complete(self) -> None:
        self.status = "completed"
        self.updated_at = datetime.utcnow()

    def is_active(self) -> bool:
        return self.status in ("scheduled", "running")
