import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func

from app.infra.marketing_stack.models import MarketingBase


class MarketingEventEntity(MarketingBase):
    __tablename__ = "marketing_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    event_type = Column(Text, nullable=False, index=True)
    occurred_at = Column(DateTime(timezone=True), nullable=False, index=True)
    channel = Column(Text, index=True)
    campaign_id = Column(Text, index=True)
    adset_id = Column(Text)
    creative_id = Column(Text)
    message_id = Column(Text, index=True)
    session_id = Column(Text, index=True)
    source_id = Column(Text, index=True)
    revenue_amount = Column(Numeric(precision=12, scale=2))
    currency = Column(Text, default="INR")
    event_metadata = Column("metadata", JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
