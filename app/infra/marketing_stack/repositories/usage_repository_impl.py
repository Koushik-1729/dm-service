from datetime import date, timedelta, datetime
from typing import Dict, Any, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func as sa_func

from app.core.marketing_stack.models.usage import Usage
from app.core.marketing_stack.outbound.repositories.usage_repository import UsageRepository
from app.infra.marketing_stack.models.usage_entity import UsageEntity


class UsageRepositoryImpl(UsageRepository):
    """SQLAlchemy implementation of UsageRepository."""

    def __init__(self, session: Session):
        self._session = session

    def _entity_to_domain(self, entity: UsageEntity) -> Usage:
        return Usage(
            id=entity.id,
            client_id=entity.client_id,
            event_type=entity.event_type,
            model_used=entity.model_used,
            tokens_input=entity.tokens_input or 0,
            tokens_output=entity.tokens_output or 0,
            cost_usd=entity.cost_usd or 0,
            metadata=entity.extra_data or {},
            created_at=entity.created_at,
        )

    async def create(self, usage: Usage) -> Usage:
        entity = UsageEntity(
            id=usage.id,
            client_id=usage.client_id,
            event_type=usage.event_type,
            model_used=usage.model_used,
            tokens_input=usage.tokens_input,
            tokens_output=usage.tokens_output,
            cost_usd=usage.cost_usd,
            extra_data=usage.metadata,
        )
        self._session.add(entity)
        self._session.commit()
        self._session.refresh(entity)
        return self._entity_to_domain(entity)

    async def get_total_by_client(
        self,
        client_id: UUID,
        start_date: date,
        end_date: date,
    ) -> Dict[str, Any]:
        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.max.time())

        results = (
            self._session.query(
                UsageEntity.event_type,
                sa_func.count(UsageEntity.id).label("count"),
                sa_func.sum(UsageEntity.tokens_input).label("total_input_tokens"),
                sa_func.sum(UsageEntity.tokens_output).label("total_output_tokens"),
                sa_func.sum(UsageEntity.cost_usd).label("total_cost"),
            )
            .filter(UsageEntity.client_id == client_id)
            .filter(UsageEntity.created_at >= start_dt)
            .filter(UsageEntity.created_at <= end_dt)
            .group_by(UsageEntity.event_type)
            .all()
        )

        breakdown = {}
        total_cost = 0
        for row in results:
            cost = float(row.total_cost or 0)
            breakdown[row.event_type] = {
                "count": int(row.count or 0),
                "tokens_input": int(row.total_input_tokens or 0),
                "tokens_output": int(row.total_output_tokens or 0),
                "cost_usd": cost,
            }
            total_cost += cost

        return {"breakdown": breakdown, "total_cost_usd": round(total_cost, 6)}

    async def list_by_client(self, client_id: UUID, limit: int = 100) -> List[Usage]:
        entities = (
            self._session.query(UsageEntity)
            .filter(UsageEntity.client_id == client_id)
            .order_by(UsageEntity.created_at.desc())
            .limit(limit)
            .all()
        )
        return [self._entity_to_domain(e) for e in entities]
