import uuid
from sqlalchemy import Column, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from app.infra.marketing_stack.models import MarketingBase


class ConversationEntity(MarketingBase):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), index=True)
    phone_number = Column(Text, nullable=False, index=True)
    direction = Column(Text, nullable=False)  # inbound / outbound
    message_type = Column(Text, default="text")  # text / image / interactive / template
    wa_message_id = Column(Text, unique=True, index=True)
    content = Column(Text, default="")
    extra_data = Column("metadata", JSONB, default=dict)
    context_type = Column(Text, default="onboarding")  # onboarding / approval / report / lead_followup
    created_at = Column(DateTime(timezone=True), server_default=func.now())
