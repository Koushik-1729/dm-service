from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.core.marketing_stack.models.strategy import Strategy
from app.core.marketing_stack.outbound.repositories.strategy_repository import StrategyRepository
from app.infra.marketing_stack.models.strategy_entity import StrategyEntity


class StrategyRepositoryImpl(StrategyRepository):
    """SQLAlchemy implementation of StrategyRepository."""

    def __init__(self, session: Session):
        self._session = session

    def _entity_to_domain(self, entity: StrategyEntity) -> Strategy:
        return Strategy(
            id=entity.id,
            client_id=entity.client_id,
            version=entity.version,
            channels=entity.channels or [],
            content_calendar=entity.content_calendar or [],
            kpis=entity.kpis or {},
            budget_allocation=entity.budget_allocation or {},
            festival_campaigns=entity.festival_campaigns or [],
            playbook_id=entity.playbook_id,
            ai_reasoning=entity.ai_reasoning,
            status=entity.status,
            created_at=entity.created_at,
        )

    async def create(self, strategy: Strategy) -> Strategy:
        entity = StrategyEntity(
            id=strategy.id,
            client_id=strategy.client_id,
            version=strategy.version,
            channels=strategy.channels,
            content_calendar=strategy.content_calendar,
            kpis=strategy.kpis,
            budget_allocation=strategy.budget_allocation,
            festival_campaigns=strategy.festival_campaigns,
            playbook_id=strategy.playbook_id,
            ai_reasoning=strategy.ai_reasoning,
            status=strategy.status,
        )
        self._session.add(entity)
        self._session.commit()
        self._session.refresh(entity)
        return self._entity_to_domain(entity)

    async def get_by_id(self, strategy_id: UUID) -> Optional[Strategy]:
        entity = self._session.query(StrategyEntity).filter(StrategyEntity.id == strategy_id).first()
        return self._entity_to_domain(entity) if entity else None

    async def get_active_by_client(self, client_id: UUID) -> Optional[Strategy]:
        entity = (
            self._session.query(StrategyEntity)
            .filter(StrategyEntity.client_id == client_id)
            .filter(StrategyEntity.status == "active")
            .order_by(StrategyEntity.version.desc())
            .first()
        )
        return self._entity_to_domain(entity) if entity else None

    async def update(self, strategy: Strategy) -> Strategy:
        entity = self._session.query(StrategyEntity).filter(StrategyEntity.id == strategy.id).first()
        if not entity:
            raise ValueError(f"Strategy {strategy.id} not found")
        entity.channels = strategy.channels
        entity.content_calendar = strategy.content_calendar
        entity.kpis = strategy.kpis
        entity.budget_allocation = strategy.budget_allocation
        entity.festival_campaigns = strategy.festival_campaigns
        entity.ai_reasoning = strategy.ai_reasoning
        entity.status = strategy.status
        self._session.commit()
        self._session.refresh(entity)
        return self._entity_to_domain(entity)

    async def list_by_client(self, client_id: UUID) -> List[Strategy]:
        entities = (
            self._session.query(StrategyEntity)
            .filter(StrategyEntity.client_id == client_id)
            .order_by(StrategyEntity.version.desc())
            .all()
        )
        return [self._entity_to_domain(e) for e in entities]
