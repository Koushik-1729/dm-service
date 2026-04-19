from collections import OrderedDict
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.marketing_stack.models.prediction_score import PredictionScore
from app.core.marketing_stack.outbound.repositories.prediction_score_repository import PredictionScoreRepository
from app.infra.marketing_stack.models.prediction_score_entity import PredictionScoreEntity


class PredictionScoreRepositoryImpl(PredictionScoreRepository):
    def __init__(self, session: Session):
        self._session = session

    def _entity_to_domain(self, entity: PredictionScoreEntity) -> PredictionScore:
        return PredictionScore(
            id=entity.id,
            client_id=entity.client_id,
            user_id=entity.user_id,
            model_name=entity.model_name,
            conversion_probability=entity.conversion_probability,
            dropout_risk=entity.dropout_risk,
            expected_revenue=entity.expected_revenue,
            feature_snapshot=entity.feature_snapshot or {},
            created_at=entity.created_at,
        )

    async def create(self, prediction: PredictionScore) -> PredictionScore:
        entity = PredictionScoreEntity(
            id=prediction.id,
            client_id=prediction.client_id,
            user_id=prediction.user_id,
            model_name=prediction.model_name,
            conversion_probability=prediction.conversion_probability,
            dropout_risk=prediction.dropout_risk,
            expected_revenue=prediction.expected_revenue,
            feature_snapshot=prediction.feature_snapshot,
        )
        self._session.add(entity)
        self._session.commit()
        self._session.refresh(entity)
        return self._entity_to_domain(entity)

    async def get_latest_by_user(self, user_id: UUID) -> Optional[PredictionScore]:
        entity = (
            self._session.query(PredictionScoreEntity)
            .filter(PredictionScoreEntity.user_id == user_id)
            .order_by(PredictionScoreEntity.created_at.desc())
            .first()
        )
        return self._entity_to_domain(entity) if entity else None

    async def list_latest_by_client(self, client_id: UUID, limit: int = 100) -> List[PredictionScore]:
        entities = (
            self._session.query(PredictionScoreEntity)
            .filter(PredictionScoreEntity.client_id == client_id)
            .order_by(PredictionScoreEntity.created_at.desc())
            .limit(limit * 5)
            .all()
        )
        latest_by_user = OrderedDict()
        for entity in entities:
            if entity.user_id not in latest_by_user:
                latest_by_user[entity.user_id] = entity
            if len(latest_by_user) >= limit:
                break
        return [self._entity_to_domain(entity) for entity in latest_by_user.values()]
