import uuid
from sqlalchemy import Column, Text, Integer, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from app.infra.marketing_stack.models import MarketingBase


class UsageEntity(MarketingBase):
    __tablename__ = "usage_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    event_type = Column(Text, nullable=False, index=True)  # ai_generation / whatsapp_message / instagram_publish
    model_used = Column(Text)  # claude-sonnet / gemini-flash
    tokens_input = Column(Integer, default=0)
    tokens_output = Column(Integer, default=0)
    cost_usd = Column(Numeric(precision=10, scale=6), default=0)
    extra_data = Column("metadata", JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
