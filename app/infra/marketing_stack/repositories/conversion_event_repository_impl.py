from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.marketing_stack.models.conversion_event import ConversionEvent
from app.core.marketing_stack.outbound.repositories.conversion_event_repository import ConversionEventRepository
from app.infra.marketing_stack.models.conversion_event_entity import ConversionEventEntity


class ConversionEventRepositoryImpl(ConversionEventRepository):
    def __init__(self, session: Session):
        self._session = session

    def _entity_to_domain(self, entity: ConversionEventEntity) -> ConversionEvent:
        return ConversionEvent(
            id=entity.id,
            client_id=entity.client_id,
            user_id=entity.user_id,
            marketing_event_id=entity.marketing_event_id,
            conversion_type=entity.conversion_type,
            conversion_value=entity.conversion_value,
            currency=entity.currency,
            occurred_at=entity.occurred_at,
            created_at=entity.created_at,
        )

    async def create(self, event: ConversionEvent) -> ConversionEvent:
        entity = ConversionEventEntity(
            id=event.id,
            client_id=event.client_id,
            user_id=event.user_id,
            marketing_event_id=event.marketing_event_id,
            conversion_type=event.conversion_type,
            conversion_value=event.conversion_value,
            currency=event.currency,
            occurred_at=event.occurred_at,
        )
        self._session.add(entity)
        self._session.commit()
        self._session.refresh(entity)
        return self._entity_to_domain(entity)

    async def get_by_id(self, conversion_event_id: UUID) -> Optional[ConversionEvent]:
        entity = (
            self._session.query(ConversionEventEntity)
            .filter(ConversionEventEntity.id == conversion_event_id)
            .first()
        )
        return self._entity_to_domain(entity) if entity else None

    async def list_by_user(self, user_id: UUID, limit: int = 100) -> List[ConversionEvent]:
        entities = (
            self._session.query(ConversionEventEntity)
            .filter(ConversionEventEntity.user_id == user_id)
            .order_by(ConversionEventEntity.occurred_at.desc())
            .limit(limit)
            .all()
        )
        return [self._entity_to_domain(entity) for entity in entities]
