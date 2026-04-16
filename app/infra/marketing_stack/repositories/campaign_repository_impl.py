from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.core.marketing_stack.models.campaign import Campaign
from app.core.marketing_stack.outbound.repositories.campaign_repository import CampaignRepository
from app.infra.marketing_stack.models.campaign_entity import CampaignEntity


class CampaignRepositoryImpl(CampaignRepository):
    """SQLAlchemy implementation of CampaignRepository."""

    def __init__(self, session: Session):
        self._session = session

    def _entity_to_domain(self, entity: CampaignEntity) -> Campaign:
        return Campaign(
            id=entity.id,
            client_id=entity.client_id,
            content_id=entity.content_id,
            channel=entity.channel,
            campaign_type=entity.campaign_type,
            status=entity.status,
            platform_id=entity.platform_id,
            target_audience=entity.target_audience or {},
            budget=entity.budget,
            start_date=entity.start_date,
            end_date=entity.end_date,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def create(self, campaign: Campaign) -> Campaign:
        entity = CampaignEntity(
            id=campaign.id,
            client_id=campaign.client_id,
            content_id=campaign.content_id,
            channel=campaign.channel,
            campaign_type=campaign.campaign_type,
            status=campaign.status,
            platform_id=campaign.platform_id,
            target_audience=campaign.target_audience,
            budget=campaign.budget,
            start_date=campaign.start_date,
            end_date=campaign.end_date,
        )
        self._session.add(entity)
        self._session.commit()
        self._session.refresh(entity)
        return self._entity_to_domain(entity)

    async def get_by_id(self, campaign_id: UUID) -> Optional[Campaign]:
        entity = self._session.query(CampaignEntity).filter(CampaignEntity.id == campaign_id).first()
        return self._entity_to_domain(entity) if entity else None

    async def list_active_by_client(self, client_id: UUID) -> List[Campaign]:
        entities = (
            self._session.query(CampaignEntity)
            .filter(CampaignEntity.client_id == client_id)
            .filter(CampaignEntity.status.in_(["scheduled", "running"]))
            .order_by(CampaignEntity.created_at.desc())
            .all()
        )
        return [self._entity_to_domain(e) for e in entities]

    async def update(self, campaign: Campaign) -> Campaign:
        entity = self._session.query(CampaignEntity).filter(CampaignEntity.id == campaign.id).first()
        if not entity:
            raise ValueError(f"Campaign {campaign.id} not found")
        entity.status = campaign.status
        entity.platform_id = campaign.platform_id
        entity.budget = campaign.budget
        entity.end_date = campaign.end_date
        self._session.commit()
        self._session.refresh(entity)
        return self._entity_to_domain(entity)

    async def list_by_channel(self, client_id: UUID, channel: str) -> List[Campaign]:
        entities = (
            self._session.query(CampaignEntity)
            .filter(CampaignEntity.client_id == client_id)
            .filter(CampaignEntity.channel == channel)
            .order_by(CampaignEntity.created_at.desc())
            .all()
        )
        return [self._entity_to_domain(e) for e in entities]
