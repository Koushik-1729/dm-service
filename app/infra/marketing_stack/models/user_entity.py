import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.infra.marketing_stack.models import MarketingBase


class UserEntity(MarketingBase):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    external_ref = Column(Text, index=True)
    email = Column(Text, index=True)
    phone_number = Column(Text, index=True)
    first_name = Column(Text)
    last_name = Column(Text)
    status = Column(Text, default="active", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
