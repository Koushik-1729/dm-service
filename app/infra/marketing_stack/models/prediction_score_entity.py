import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Float, Numeric, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func

from app.infra.marketing_stack.models import MarketingBase


class PredictionScoreEntity(MarketingBase):
    __tablename__ = "prediction_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    model_name = Column(Text, nullable=False, index=True)
    conversion_probability = Column(Float, nullable=False, default=0.0)
    dropout_risk = Column(Float, nullable=False, default=0.0)
    expected_revenue = Column(Numeric(precision=12, scale=2), nullable=False, default=0)
    feature_snapshot = Column(JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
