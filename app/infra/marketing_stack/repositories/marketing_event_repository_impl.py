from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.marketing_stack.models.marketing_event import MarketingEvent
from app.core.marketing_stack.outbound.repositories.marketing_event_repository import MarketingEventRepository
from app.infra.marketing_stack.models.marketing_event_entity import MarketingEventEntity


class MarketingEventRepositoryImpl(MarketingEventRepository):
    def __init__(self, session: Session):
        self._session = session

    def _entity_to_domain(self, entity: MarketingEventEntity) -> MarketingEvent:
        return MarketingEvent(
            id=entity.id,
            client_id=entity.client_id,
            user_id=entity.user_id,
            event_type=entity.event_type,
            occurred_at=entity.occurred_at,
            channel=entity.channel,
            campaign_id=entity.campaign_id,
            adset_id=entity.adset_id,
            creative_id=entity.creative_id,
            message_id=entity.message_id,
            session_id=entity.session_id,
            source_id=entity.source_id,
            revenue_amount=entity.revenue_amount,
            currency=entity.currency,
            metadata=entity.event_metadata or {},
            created_at=entity.created_at,
        )

    async def create(self, event: MarketingEvent) -> MarketingEvent:
        entity = MarketingEventEntity(
            id=event.id,
            client_id=event.client_id,
            user_id=event.user_id,
            event_type=event.event_type,
            occurred_at=event.occurred_at,
            channel=event.channel,
            campaign_id=event.campaign_id,
            adset_id=event.adset_id,
            creative_id=event.creative_id,
            message_id=event.message_id,
            session_id=event.session_id,
            source_id=event.source_id,
            revenue_amount=event.revenue_amount,
            currency=event.currency,
            event_metadata=event.metadata,
        )
        self._session.add(entity)
        self._session.commit()
        self._session.refresh(entity)
        return self._entity_to_domain(entity)

    async def get_by_id(self, event_id: UUID) -> Optional[MarketingEvent]:
        entity = self._session.query(MarketingEventEntity).filter(MarketingEventEntity.id == event_id).first()
        return self._entity_to_domain(entity) if entity else None

    async def list_by_user(self, user_id: UUID, limit: int = 100) -> List[MarketingEvent]:
        entities = (
            self._session.query(MarketingEventEntity)
            .filter(MarketingEventEntity.user_id == user_id)
            .order_by(MarketingEventEntity.occurred_at.desc())
            .limit(limit)
            .all()
        )
        return [self._entity_to_domain(entity) for entity in entities]
