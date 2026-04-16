from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func as sa_func

from app.core.marketing_stack.models.lead import Lead
from app.core.marketing_stack.outbound.repositories.lead_repository import LeadRepository
from app.infra.marketing_stack.models.lead_entity import LeadEntity


class LeadRepositoryImpl(LeadRepository):
    """SQLAlchemy implementation of LeadRepository."""

    def __init__(self, session: Session):
        self._session = session

    def _entity_to_domain(self, entity: LeadEntity) -> Lead:
        return Lead(
            id=entity.id,
            client_id=entity.client_id,
            campaign_id=entity.campaign_id,
            name=entity.name,
            phone_number=entity.phone_number,
            source_channel=entity.source_channel,
            source_campaign_tag=entity.source_campaign_tag,
            status=entity.status,
            notes=entity.notes,
            revenue_amount=entity.revenue_amount,
            payment_verified=entity.payment_verified,
            followup_count=entity.followup_count,
            last_followup_at=entity.last_followup_at,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def create(self, lead: Lead) -> Lead:
        entity = LeadEntity(
            id=lead.id,
            client_id=lead.client_id,
            campaign_id=lead.campaign_id,
            name=lead.name,
            phone_number=lead.phone_number,
            source_channel=lead.source_channel,
            source_campaign_tag=lead.source_campaign_tag,
            status=lead.status,
        )
        self._session.add(entity)
        self._session.commit()
        self._session.refresh(entity)
        return self._entity_to_domain(entity)

    async def get_by_id(self, lead_id: UUID) -> Optional[Lead]:
        entity = self._session.query(LeadEntity).filter(LeadEntity.id == lead_id).first()
        return self._entity_to_domain(entity) if entity else None

    async def get_by_phone_and_client(self, phone_number: str, client_id: UUID) -> Optional[Lead]:
        entity = (
            self._session.query(LeadEntity)
            .filter(LeadEntity.phone_number == phone_number)
            .filter(LeadEntity.client_id == client_id)
            .order_by(LeadEntity.created_at.desc())
            .first()
        )
        return self._entity_to_domain(entity) if entity else None

    async def list_by_client(self, client_id: UUID, status: Optional[str] = None) -> List[Lead]:
        query = self._session.query(LeadEntity).filter(LeadEntity.client_id == client_id)
        if status:
            query = query.filter(LeadEntity.status == status)
        entities = query.order_by(LeadEntity.created_at.desc()).all()
        return [self._entity_to_domain(e) for e in entities]

    async def list_needs_followup(self, client_id: UUID, max_followups: int = 3) -> List[Lead]:
        entities = (
            self._session.query(LeadEntity)
            .filter(LeadEntity.client_id == client_id)
            .filter(LeadEntity.status.in_(["new", "notified"]))
            .filter(LeadEntity.followup_count < max_followups)
            .order_by(LeadEntity.created_at.asc())
            .all()
        )
        return [self._entity_to_domain(e) for e in entities]

    async def update(self, lead: Lead) -> Lead:
        entity = self._session.query(LeadEntity).filter(LeadEntity.id == lead.id).first()
        if not entity:
            raise ValueError(f"Lead {lead.id} not found")
        entity.status = lead.status
        entity.notes = lead.notes
        entity.revenue_amount = lead.revenue_amount
        entity.payment_verified = lead.payment_verified
        entity.followup_count = lead.followup_count
        entity.last_followup_at = lead.last_followup_at
        entity.name = lead.name
        self._session.commit()
        self._session.refresh(entity)
        return self._entity_to_domain(entity)

    async def count_by_source(self, client_id: UUID, days: int = 7) -> dict:
        since = datetime.utcnow() - timedelta(days=days)
        results = (
            self._session.query(
                LeadEntity.source_channel,
                sa_func.count(LeadEntity.id).label("count"),
            )
            .filter(LeadEntity.client_id == client_id)
            .filter(LeadEntity.created_at >= since)
            .group_by(LeadEntity.source_channel)
            .all()
        )
        return {row.source_channel: row.count for row in results}
