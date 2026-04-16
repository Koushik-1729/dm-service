from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from loguru import logger

from app.core.marketing_stack.models.client import Client
from app.core.marketing_stack.outbound.repositories.client_repository import ClientRepository
from app.infra.marketing_stack.models.client_entity import ClientEntity


class ClientRepositoryImpl(ClientRepository):
    """SQLAlchemy implementation of ClientRepository."""

    def __init__(self, session: Session):
        self._session = session

    def _entity_to_domain(self, entity: ClientEntity) -> Client:
        return Client(
            id=entity.id,
            phone_number=entity.phone_number,
            business_name=entity.business_name,
            owner_name=entity.owner_name,
            sector=entity.sector,
            sub_sector=entity.sub_sector,
            website_url=entity.website_url,
            google_maps_url=entity.google_maps_url,
            instagram_handle=entity.instagram_handle,
            city=entity.city,
            locality=entity.locality,
            language=entity.language or "english",
            business_profile=entity.business_profile or {},
            scraped_data=entity.scraped_data or {},
            onboarding_status=entity.onboarding_status,
            onboarding_answers=entity.onboarding_answers or {},
            current_question_index=entity.current_question_index or 0,
            subscription_tier=entity.subscription_tier,
            autonomy_level=entity.autonomy_level,
            content_review_state=entity.content_review_state or {},
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def _domain_to_entity(self, client: Client) -> ClientEntity:
        return ClientEntity(
            id=client.id,
            phone_number=client.phone_number,
            business_name=client.business_name,
            owner_name=client.owner_name,
            sector=client.sector,
            sub_sector=client.sub_sector,
            website_url=client.website_url,
            google_maps_url=client.google_maps_url,
            instagram_handle=client.instagram_handle,
            city=client.city,
            locality=client.locality,
            language=client.language,
            business_profile=client.business_profile,
            scraped_data=client.scraped_data,
            onboarding_status=client.onboarding_status,
            onboarding_answers=client.onboarding_answers,
            current_question_index=client.current_question_index,
            subscription_tier=client.subscription_tier,
            autonomy_level=client.autonomy_level,
            content_review_state=client.content_review_state,
            is_active=client.is_active,
        )

    async def create(self, client: Client) -> Client:
        entity = self._domain_to_entity(client)
        try:
            self._session.add(entity)
            self._session.commit()
            self._session.refresh(entity)
            return self._entity_to_domain(entity)
        except IntegrityError as e:
            self._session.rollback()
            if "phone_number" in str(e):
                raise ValueError(f"Client with phone {client.phone_number} already exists")
            raise

    async def get_by_id(self, client_id: UUID) -> Optional[Client]:
        entity = (
            self._session.query(ClientEntity)
            .filter(ClientEntity.id == client_id)
            .first()
        )
        return self._entity_to_domain(entity) if entity else None

    async def get_by_phone(self, phone_number: str) -> Optional[Client]:
        entity = (
            self._session.query(ClientEntity)
            .filter(ClientEntity.phone_number == phone_number)
            .first()
        )
        return self._entity_to_domain(entity) if entity else None

    async def update(self, client: Client) -> Client:
        entity = (
            self._session.query(ClientEntity)
            .filter(ClientEntity.id == client.id)
            .first()
        )
        if not entity:
            raise ValueError(f"Client with id {client.id} not found")

        entity.phone_number = client.phone_number
        entity.business_name = client.business_name
        entity.owner_name = client.owner_name
        entity.sector = client.sector
        entity.sub_sector = client.sub_sector
        entity.website_url = client.website_url
        entity.google_maps_url = client.google_maps_url
        entity.instagram_handle = client.instagram_handle
        entity.city = client.city
        entity.locality = client.locality
        entity.language = client.language
        entity.business_profile = client.business_profile
        entity.scraped_data = client.scraped_data
        entity.onboarding_status = client.onboarding_status
        entity.onboarding_answers = client.onboarding_answers
        entity.current_question_index = client.current_question_index
        entity.subscription_tier = client.subscription_tier
        entity.autonomy_level = client.autonomy_level
        entity.content_review_state = client.content_review_state
        entity.is_active = client.is_active

        try:
            self._session.commit()
            self._session.refresh(entity)
            return self._entity_to_domain(entity)
        except IntegrityError:
            self._session.rollback()
            raise

    async def list_active(self) -> List[Client]:
        entities = (
            self._session.query(ClientEntity)
            .filter(ClientEntity.is_active == True)
            .filter(ClientEntity.onboarding_status == "complete")
            .order_by(ClientEntity.created_at.desc())
            .all()
        )
        return [self._entity_to_domain(e) for e in entities]

    async def list_by_sector(self, sector: str) -> List[Client]:
        entities = (
            self._session.query(ClientEntity)
            .filter(ClientEntity.sector == sector)
            .filter(ClientEntity.is_active == True)
            .all()
        )
        return [self._entity_to_domain(e) for e in entities]
