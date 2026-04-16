import uuid
from sqlalchemy import Column, Text, Integer, Boolean, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.infra.marketing_stack.models import MarketingBase


class LeadEntity(MarketingBase):
    __tablename__ = "leads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=True, index=True)
    name = Column(Text)
    phone_number = Column(Text, nullable=False, index=True)
    source_channel = Column(Text, nullable=False, index=True)  # whatsapp / instagram / google_ads
    source_campaign_tag = Column(Text)  # UTM tag or coupon code
    status = Column(Text, default="new", index=True)  # new / notified / contacted / converted / lost
    notes = Column(Text)
    revenue_amount = Column(Numeric(precision=12, scale=2))
    payment_verified = Column(Boolean, default=False)
    followup_count = Column(Integer, default=0)
    last_followup_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
