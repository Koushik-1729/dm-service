from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.marketing_stack.models.user_identity import UserIdentity
from app.core.marketing_stack.outbound.repositories.user_identity_repository import UserIdentityRepository
from app.infra.marketing_stack.models.user_identity_entity import UserIdentityEntity


class UserIdentityRepositoryImpl(UserIdentityRepository):
    def __init__(self, session: Session):
        self._session = session

    def _entity_to_domain(self, entity: UserIdentityEntity) -> UserIdentity:
        return UserIdentity(
            id=entity.id,
            client_id=entity.client_id,
            user_id=entity.user_id,
            identity_type=entity.identity_type,
            identity_value=entity.identity_value,
            is_primary=entity.is_primary,
            created_at=entity.created_at,
        )

    async def create(self, identity: UserIdentity) -> UserIdentity:
        entity = UserIdentityEntity(
            id=identity.id,
            client_id=identity.client_id,
            user_id=identity.user_id,
            identity_type=identity.identity_type,
            identity_value=identity.identity_value,
            is_primary=identity.is_primary,
        )
        self._session.add(entity)
        self._session.commit()
        self._session.refresh(entity)
        return self._entity_to_domain(entity)

    async def get_by_type_and_value(
        self,
        client_id: UUID,
        identity_type: str,
        identity_value: str,
    ) -> Optional[UserIdentity]:
        entity = (
            self._session.query(UserIdentityEntity)
            .filter(UserIdentityEntity.client_id == client_id)
            .filter(UserIdentityEntity.identity_type == identity_type)
            .filter(UserIdentityEntity.identity_value == identity_value)
            .first()
        )
        return self._entity_to_domain(entity) if entity else None

    async def list_by_user(self, user_id: UUID) -> List[UserIdentity]:
        entities = (
            self._session.query(UserIdentityEntity)
            .filter(UserIdentityEntity.user_id == user_id)
            .order_by(UserIdentityEntity.created_at.asc())
            .all()
        )
        return [self._entity_to_domain(entity) for entity in entities]
