from datetime import datetime, date
from typing import Optional
from uuid import UUID
from decimal import Decimal


class DailyMetrics:
    """Domain model representing daily performance metrics per channel."""

    def __init__(
        self,
        id: Optional[UUID] = None,
        client_id: Optional[UUID] = None,
        date: Optional[date] = None,
        channel: str = "",
        impressions: int = 0,
        reach: int = 0,
        engagement: int = 0,
        clicks: int = 0,
        leads_count: int = 0,
        revenue: Decimal = Decimal("0"),
        spend: Decimal = Decimal("0"),
        followers_gained: int = 0,
        messages_sent: int = 0,
        messages_delivered: int = 0,
        messages_read: int = 0,
        created_at: Optional[datetime] = None,
    ):
        self.id = id
        self.client_id = client_id
        self.date = date
        self.channel = channel
        self.impressions = impressions
        self.reach = reach
        self.engagement = engagement
        self.clicks = clicks
        self.leads_count = leads_count
        self.revenue = revenue
        self.spend = spend
        self.followers_gained = followers_gained
        self.messages_sent = messages_sent
        self.messages_delivered = messages_delivered
        self.messages_read = messages_read
        self.created_at = created_at

    def ctr(self) -> float:
        if self.impressions == 0:
            return 0.0
        return round((self.clicks / self.impressions) * 100, 2)

    def roi(self) -> float:
        if self.spend == 0:
            return 0.0
        return round(float(self.revenue / self.spend), 2)

    def engagement_rate(self) -> float:
        if self.reach == 0:
            return 0.0
        return round((self.engagement / self.reach) * 100, 2)
