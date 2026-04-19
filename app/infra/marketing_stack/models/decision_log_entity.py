import uuid

from sqlalchemy import Column, DateTime, Float, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func

from app.infra.marketing_stack.models import MarketingBase


class DecisionLogEntity(MarketingBase):
    __tablename__ = "decision_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    prediction_score_id = Column(UUID(as_uuid=True), ForeignKey("prediction_scores.id"), index=True)
    action_type = Column(Text, nullable=False, index=True)
    action_payload = Column(JSONB, default=dict)
    confidence = Column(Float, nullable=False, default=0.0)
    expected_revenue_impact = Column(Numeric(precision=12, scale=2), nullable=False, default=0)
    reason = Column(Text, nullable=False)
    status = Column(Text, nullable=False, default="recommended", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
