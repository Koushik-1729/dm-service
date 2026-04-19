from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.marketing_stack.models.revenue_event import RevenueEvent
from app.core.marketing_stack.outbound.repositories.revenue_event_repository import RevenueEventRepository
from app.infra.marketing_stack.models.revenue_event_entity import RevenueEventEntity


class RevenueEventRepositoryImpl(RevenueEventRepository):
    def __init__(self, session: Session):
        self._session = session

    def _entity_to_domain(self, entity: RevenueEventEntity) -> RevenueEvent:
        return RevenueEvent(
            id=entity.id,
            client_id=entity.client_id,
            user_id=entity.user_id,
            conversion_event_id=entity.conversion_event_id,
            amount=entity.amount,
            currency=entity.currency,
            payment_reference=entity.payment_reference,
            occurred_at=entity.occurred_at,
            created_at=entity.created_at,
        )

    async def create(self, event: RevenueEvent) -> RevenueEvent:
        entity = RevenueEventEntity(
            id=event.id,
            client_id=event.client_id,
            user_id=event.user_id,
            conversion_event_id=event.conversion_event_id,
            amount=event.amount,
            currency=event.currency,
            payment_reference=event.payment_reference,
            occurred_at=event.occurred_at,
        )
        self._session.add(entity)
        self._session.commit()
        self._session.refresh(entity)
        return self._entity_to_domain(entity)

    async def get_by_id(self, revenue_event_id: UUID) -> Optional[RevenueEvent]:
        entity = self._session.query(RevenueEventEntity).filter(RevenueEventEntity.id == revenue_event_id).first()
        return self._entity_to_domain(entity) if entity else None

    async def list_by_user(self, user_id: UUID, limit: int = 100) -> List[RevenueEvent]:
        entities = (
            self._session.query(RevenueEventEntity)
            .filter(RevenueEventEntity.user_id == user_id)
            .order_by(RevenueEventEntity.occurred_at.desc())
            .limit(limit)
            .all()
        )
        return [self._entity_to_domain(entity) for entity in entities]
