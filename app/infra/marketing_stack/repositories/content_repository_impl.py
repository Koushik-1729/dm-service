from datetime import datetime
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.core.marketing_stack.models.content import Content
from app.core.marketing_stack.outbound.repositories.content_repository import ContentRepository
from app.infra.marketing_stack.models.content_entity import ContentEntity


class ContentRepositoryImpl(ContentRepository):
    """SQLAlchemy implementation of ContentRepository."""

    def __init__(self, session: Session):
        self._session = session

    def _entity_to_domain(self, entity: ContentEntity) -> Content:
        return Content(
            id=entity.id,
            client_id=entity.client_id,
            strategy_id=entity.strategy_id,
            channel=entity.channel,
            content_type=entity.content_type,
            variant_group=entity.variant_group,
            variant_label=entity.variant_label,
            caption=entity.caption,
            media_url=entity.media_url,
            hashtags=list(entity.hashtags) if entity.hashtags else [],
            cta_text=entity.cta_text,
            cta_url=entity.cta_url,
            coupon_code=entity.coupon_code,
            utm_params=entity.utm_params,
            language=entity.language,
            ai_model_used=entity.ai_model_used,
            risk_level=entity.risk_level,
            status=entity.status,
            scheduled_for=entity.scheduled_for,
            published_at=entity.published_at,
            platform_post_id=entity.platform_post_id,
            created_at=entity.created_at,
        )

    async def create(self, content: Content) -> Content:
        entity = ContentEntity(
            id=content.id,
            client_id=content.client_id,
            strategy_id=content.strategy_id,
            channel=content.channel,
            content_type=content.content_type,
            variant_group=content.variant_group,
            variant_label=content.variant_label,
            caption=content.caption,
            media_url=content.media_url,
            hashtags=[str(h) for h in content.hashtags] if content.hashtags else [],
            cta_text=content.cta_text,
            cta_url=content.cta_url,
            coupon_code=content.coupon_code,
            utm_params=content.utm_params,
            language=content.language,
            ai_model_used=content.ai_model_used,
            risk_level=content.risk_level,
            status=content.status,
            scheduled_for=content.scheduled_for,
        )
        self._session.add(entity)
        self._session.commit()
        self._session.refresh(entity)
        return self._entity_to_domain(entity)

    async def create_batch(self, contents: List[Content]) -> List[Content]:
        entities = []
        for content in contents:
            entity = ContentEntity(
                id=content.id,
                client_id=content.client_id,
                strategy_id=content.strategy_id,
                channel=content.channel,
                content_type=content.content_type,
                variant_group=content.variant_group,
                variant_label=content.variant_label,
                caption=content.caption,
                media_url=content.media_url,
                hashtags=[str(h) for h in content.hashtags] if content.hashtags else [],
                cta_text=content.cta_text,
                cta_url=content.cta_url,
                coupon_code=content.coupon_code,
                utm_params=content.utm_params,
                language=content.language,
                ai_model_used=content.ai_model_used,
                risk_level=content.risk_level,
                status=content.status,
                scheduled_for=content.scheduled_for,
            )
            entities.append(entity)
        self._session.add_all(entities)
        self._session.commit()
        for e in entities:
            self._session.refresh(e)
        return [self._entity_to_domain(e) for e in entities]

    async def get_by_id(self, content_id: UUID) -> Optional[Content]:
        entity = self._session.query(ContentEntity).filter(ContentEntity.id == content_id).first()
        return self._entity_to_domain(entity) if entity else None

    async def list_by_client(
        self,
        client_id: UUID,
        status: Optional[str] = None,
        channel: Optional[str] = None,
    ) -> List[Content]:
        query = self._session.query(ContentEntity).filter(ContentEntity.client_id == client_id)
        if status:
            query = query.filter(ContentEntity.status == status)
        if channel:
            query = query.filter(ContentEntity.channel == channel)
        entities = query.order_by(ContentEntity.created_at.desc()).all()
        return [self._entity_to_domain(e) for e in entities]

    async def get_scheduled(self, before: datetime) -> List[Content]:
        entities = (
            self._session.query(ContentEntity)
            .filter(ContentEntity.status == "scheduled")
            .filter(ContentEntity.scheduled_for <= before)
            .order_by(ContentEntity.scheduled_for.asc())
            .all()
        )
        return [self._entity_to_domain(e) for e in entities]

    async def list_by_variant_group(self, variant_group: str) -> List[Content]:
        entities = (
            self._session.query(ContentEntity)
            .filter(ContentEntity.variant_group == variant_group)
            .order_by(ContentEntity.variant_label.asc())
            .all()
        )
        return [self._entity_to_domain(e) for e in entities]

    async def update(self, content: Content) -> Content:
        entity = self._session.query(ContentEntity).filter(ContentEntity.id == content.id).first()
        if not entity:
            raise ValueError(f"Content {content.id} not found")
        entity.status = content.status
        entity.published_at = content.published_at
        entity.platform_post_id = content.platform_post_id
        entity.media_url = content.media_url
        entity.coupon_code = content.coupon_code
        entity.utm_params = content.utm_params
        self._session.commit()
        self._session.refresh(entity)
        return self._entity_to_domain(entity)
