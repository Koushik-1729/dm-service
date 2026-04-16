import uuid
from sqlalchemy import Column, Text, Boolean, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from app.infra.marketing_stack.models import MarketingBase


class ClientEntity(MarketingBase):
    __tablename__ = "clients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone_number = Column(Text, unique=True, nullable=False, index=True)
    business_name = Column(Text)
    owner_name = Column(Text)
    sector = Column(Text, index=True)
    sub_sector = Column(Text)
    website_url = Column(Text)
    google_maps_url = Column(Text)
    instagram_handle = Column(Text)
    city = Column(Text, index=True)
    locality = Column(Text)
    language = Column(Text, default="english")
    business_profile = Column(JSONB, default=dict)
    scraped_data = Column(JSONB, default=dict)
    onboarding_status = Column(Text, default="pending_questions", index=True)
    onboarding_answers = Column(JSONB, default=dict)
    current_question_index = Column(Integer, default=0)
    subscription_tier = Column(Text, default="trial")
    autonomy_level = Column(Text, default="supervised")
    content_review_state = Column(JSONB, default=dict)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
