import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.infra.marketing_stack.models import MarketingBase


class UserIdentityEntity(MarketingBase):
    __tablename__ = "user_identities"
    __table_args__ = (
        UniqueConstraint("client_id", "identity_type", "identity_value", name="uq_user_identity_key"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    identity_type = Column(Text, nullable=False, index=True)
    identity_value = Column(Text, nullable=False, index=True)
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
