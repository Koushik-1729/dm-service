import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.infra.marketing_stack.models import MarketingBase


class ConversionEventEntity(MarketingBase):
    __tablename__ = "conversion_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    marketing_event_id = Column(UUID(as_uuid=True), ForeignKey("marketing_events.id"), index=True)
    conversion_type = Column(Text, nullable=False, index=True)
    conversion_value = Column(Numeric(precision=12, scale=2))
    currency = Column(Text, default="INR")
    occurred_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
