import uuid
from sqlalchemy import Column, Text, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from app.infra.marketing_stack.models import MarketingBase


class StrategyEntity(MarketingBase):
    __tablename__ = "strategies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    version = Column(Integer, default=1)
    channels = Column(JSONB, default=list)
    content_calendar = Column(JSONB, default=list)
    kpis = Column(JSONB, default=dict)
    budget_allocation = Column(JSONB, default=dict)
    festival_campaigns = Column(JSONB, default=list)
    playbook_id = Column(Text)
    ai_reasoning = Column(Text)
    status = Column(Text, default="draft", index=True)  # draft / active / archived
    created_at = Column(DateTime(timezone=True), server_default=func.now())
