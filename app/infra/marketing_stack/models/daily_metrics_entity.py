import uuid
from sqlalchemy import Column, Text, Integer, Numeric, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.infra.marketing_stack.models import MarketingBase


class DailyMetricsEntity(MarketingBase):
    __tablename__ = "daily_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    channel = Column(Text, nullable=False, index=True)
    impressions = Column(Integer, default=0)
    reach = Column(Integer, default=0)
    engagement = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    leads_count = Column(Integer, default=0)
    revenue = Column(Numeric(precision=12, scale=2), default=0)
    spend = Column(Numeric(precision=12, scale=2), default=0)
    followers_gained = Column(Integer, default=0)
    messages_sent = Column(Integer, default=0)
    messages_delivered = Column(Integer, default=0)
    messages_read = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("client_id", "date", "channel", name="uq_client_date_channel"),
    )
