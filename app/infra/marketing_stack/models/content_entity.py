import uuid
from sqlalchemy import Column, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.sql import func

from app.infra.marketing_stack.models import MarketingBase


class ContentEntity(MarketingBase):
    __tablename__ = "contents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    strategy_id = Column(UUID(as_uuid=True), ForeignKey("strategies.id"), index=True)
    channel = Column(Text, nullable=False, index=True)  # instagram / whatsapp / etc
    content_type = Column(Text, nullable=False)  # post / reel_script / campaign_message
    variant_group = Column(Text, index=True)  # groups A/B/C variants
    variant_label = Column(Text, default="A")  # A / B / C
    caption = Column(Text, default="")
    media_url = Column(Text)
    hashtags = Column(ARRAY(Text), default=list)
    cta_text = Column(Text)
    cta_url = Column(Text)
    coupon_code = Column(Text)
    utm_params = Column(Text)
    language = Column(Text, default="english")
    ai_model_used = Column(Text)
    risk_level = Column(Text, default="low")  # low / medium / high / blocked
    status = Column(Text, default="draft", index=True)  # draft / approved / published / failed
    scheduled_for = Column(DateTime(timezone=True))
    published_at = Column(DateTime(timezone=True))
    platform_post_id = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
