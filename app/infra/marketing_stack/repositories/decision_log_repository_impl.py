from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.marketing_stack.models.decision_log import DecisionLog
from app.core.marketing_stack.outbound.repositories.decision_log_repository import DecisionLogRepository
from app.infra.marketing_stack.models.decision_log_entity import DecisionLogEntity


class DecisionLogRepositoryImpl(DecisionLogRepository):
    def __init__(self, session: Session):
        self._session = session

    def _entity_to_domain(self, entity: DecisionLogEntity) -> DecisionLog:
        return DecisionLog(
            id=entity.id,
            client_id=entity.client_id,
            user_id=entity.user_id,
            prediction_score_id=entity.prediction_score_id,
            action_type=entity.action_type,
            action_payload=entity.action_payload or {},
            confidence=entity.confidence,
            expected_revenue_impact=entity.expected_revenue_impact,
            reason=entity.reason,
            status=entity.status,
            created_at=entity.created_at,
        )

    async def create(self, decision: DecisionLog) -> DecisionLog:
        entity = DecisionLogEntity(
            id=decision.id,
            client_id=decision.client_id,
            user_id=decision.user_id,
            prediction_score_id=decision.prediction_score_id,
            action_type=decision.action_type,
            action_payload=decision.action_payload,
            confidence=decision.confidence,
            expected_revenue_impact=decision.expected_revenue_impact,
            reason=decision.reason,
            status=decision.status,
        )
        self._session.add(entity)
        self._session.commit()
        self._session.refresh(entity)
        return self._entity_to_domain(entity)

    async def get_latest_by_user(self, user_id: UUID) -> Optional[DecisionLog]:
        entity = (
            self._session.query(DecisionLogEntity)
            .filter(DecisionLogEntity.user_id == user_id)
            .order_by(DecisionLogEntity.created_at.desc())
            .first()
        )
        return self._entity_to_domain(entity) if entity else None

    async def list_by_client(self, client_id: UUID, limit: int = 100) -> List[DecisionLog]:
        entities = (
            self._session.query(DecisionLogEntity)
            .filter(DecisionLogEntity.client_id == client_id)
            .order_by(DecisionLogEntity.created_at.desc())
            .limit(limit)
            .all()
        )
        return [self._entity_to_domain(entity) for entity in entities]
