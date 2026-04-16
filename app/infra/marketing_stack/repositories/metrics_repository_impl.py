from datetime import date, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func as sa_func

from app.core.marketing_stack.models.daily_metrics import DailyMetrics
from app.core.marketing_stack.outbound.repositories.metrics_repository import MetricsRepository
from app.infra.marketing_stack.models.daily_metrics_entity import DailyMetricsEntity


class MetricsRepositoryImpl(MetricsRepository):
    """SQLAlchemy implementation of MetricsRepository."""

    def __init__(self, session: Session):
        self._session = session

    def _entity_to_domain(self, entity: DailyMetricsEntity) -> DailyMetrics:
        return DailyMetrics(
            id=entity.id,
            client_id=entity.client_id,
            date=entity.date,
            channel=entity.channel,
            impressions=entity.impressions or 0,
            reach=entity.reach or 0,
            engagement=entity.engagement or 0,
            clicks=entity.clicks or 0,
            leads_count=entity.leads_count or 0,
            revenue=entity.revenue or Decimal("0"),
            spend=entity.spend or Decimal("0"),
            followers_gained=entity.followers_gained or 0,
            messages_sent=entity.messages_sent or 0,
            messages_delivered=entity.messages_delivered or 0,
            messages_read=entity.messages_read or 0,
            created_at=entity.created_at,
        )

    async def upsert_daily(self, metrics: DailyMetrics) -> DailyMetrics:
        entity = (
            self._session.query(DailyMetricsEntity)
            .filter(DailyMetricsEntity.client_id == metrics.client_id)
            .filter(DailyMetricsEntity.date == metrics.date)
            .filter(DailyMetricsEntity.channel == metrics.channel)
            .first()
        )

        if entity:
            entity.impressions = metrics.impressions
            entity.reach = metrics.reach
            entity.engagement = metrics.engagement
            entity.clicks = metrics.clicks
            entity.leads_count = metrics.leads_count
            entity.revenue = metrics.revenue
            entity.spend = metrics.spend
            entity.followers_gained = metrics.followers_gained
            entity.messages_sent = metrics.messages_sent
            entity.messages_delivered = metrics.messages_delivered
            entity.messages_read = metrics.messages_read
        else:
            entity = DailyMetricsEntity(
                id=metrics.id,
                client_id=metrics.client_id,
                date=metrics.date,
                channel=metrics.channel,
                impressions=metrics.impressions,
                reach=metrics.reach,
                engagement=metrics.engagement,
                clicks=metrics.clicks,
                leads_count=metrics.leads_count,
                revenue=metrics.revenue,
                spend=metrics.spend,
                followers_gained=metrics.followers_gained,
                messages_sent=metrics.messages_sent,
                messages_delivered=metrics.messages_delivered,
                messages_read=metrics.messages_read,
            )
            self._session.add(entity)

        self._session.commit()
        self._session.refresh(entity)
        return self._entity_to_domain(entity)

    async def get_range(
        self,
        client_id: UUID,
        start_date: date,
        end_date: date,
        channel: Optional[str] = None,
    ) -> List[DailyMetrics]:
        query = (
            self._session.query(DailyMetricsEntity)
            .filter(DailyMetricsEntity.client_id == client_id)
            .filter(DailyMetricsEntity.date >= start_date)
            .filter(DailyMetricsEntity.date <= end_date)
        )
        if channel:
            query = query.filter(DailyMetricsEntity.channel == channel)
        entities = query.order_by(DailyMetricsEntity.date.asc()).all()
        return [self._entity_to_domain(e) for e in entities]

    async def get_latest(self, client_id: UUID) -> Optional[DailyMetrics]:
        entity = (
            self._session.query(DailyMetricsEntity)
            .filter(DailyMetricsEntity.client_id == client_id)
            .order_by(DailyMetricsEntity.date.desc())
            .first()
        )
        return self._entity_to_domain(entity) if entity else None

    async def get_summary(self, client_id: UUID, days: int = 7) -> Dict[str, Any]:
        since = date.today() - timedelta(days=days)
        results = (
            self._session.query(
                DailyMetricsEntity.channel,
                sa_func.sum(DailyMetricsEntity.impressions).label("total_impressions"),
                sa_func.sum(DailyMetricsEntity.clicks).label("total_clicks"),
                sa_func.sum(DailyMetricsEntity.engagement).label("total_engagement"),
                sa_func.sum(DailyMetricsEntity.leads_count).label("total_leads"),
                sa_func.sum(DailyMetricsEntity.revenue).label("total_revenue"),
                sa_func.sum(DailyMetricsEntity.spend).label("total_spend"),
                sa_func.sum(DailyMetricsEntity.followers_gained).label("total_followers"),
                sa_func.sum(DailyMetricsEntity.messages_sent).label("total_messages_sent"),
                sa_func.sum(DailyMetricsEntity.messages_read).label("total_messages_read"),
            )
            .filter(DailyMetricsEntity.client_id == client_id)
            .filter(DailyMetricsEntity.date >= since)
            .group_by(DailyMetricsEntity.channel)
            .all()
        )

        summary = {}
        for row in results:
            total_spend = float(row.total_spend or 0)
            total_revenue = float(row.total_revenue or 0)
            summary[row.channel] = {
                "impressions": int(row.total_impressions or 0),
                "clicks": int(row.total_clicks or 0),
                "engagement": int(row.total_engagement or 0),
                "leads": int(row.total_leads or 0),
                "revenue": total_revenue,
                "spend": total_spend,
                "roi": round(total_revenue / total_spend, 2) if total_spend > 0 else 0,
                "followers_gained": int(row.total_followers or 0),
                "messages_sent": int(row.total_messages_sent or 0),
                "messages_read": int(row.total_messages_read or 0),
            }
        return summary
