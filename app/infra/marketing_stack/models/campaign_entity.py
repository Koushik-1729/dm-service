import uuid
from sqlalchemy import Column, Text, Numeric, Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from app.infra.marketing_stack.models import MarketingBase


class CampaignEntity(MarketingBase):
    __tablename__ = "campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    content_id = Column(UUID(as_uuid=True), ForeignKey("contents.id"), index=True)
    channel = Column(Text, nullable=False, index=True)
    campaign_type = Column(Text, nullable=False)  # organic_post / whatsapp_broadcast / paid_ad
    status = Column(Text, default="scheduled", index=True)  # scheduled / running / paused / completed / failed
    platform_id = Column(Text)  # IG post ID / Meta campaign ID
    target_audience = Column(JSONB, default=dict)
    budget = Column(Numeric(precision=12, scale=2))
    start_date = Column(Date)
    end_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
