from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.marketing_stack.models.user import User
from app.core.marketing_stack.outbound.repositories.user_repository import UserRepository
from app.infra.marketing_stack.models.user_entity import UserEntity


class UserRepositoryImpl(UserRepository):
    def __init__(self, session: Session):
        self._session = session

    def _entity_to_domain(self, entity: UserEntity) -> User:
        return User(
            id=entity.id,
            client_id=entity.client_id,
            external_ref=entity.external_ref,
            email=entity.email,
            phone_number=entity.phone_number,
            first_name=entity.first_name,
            last_name=entity.last_name,
            status=entity.status,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def create(self, user: User) -> User:
        entity = UserEntity(
            id=user.id,
            client_id=user.client_id,
            external_ref=user.external_ref,
            email=user.email,
            phone_number=user.phone_number,
            first_name=user.first_name,
            last_name=user.last_name,
            status=user.status,
        )
        self._session.add(entity)
        self._session.commit()
        self._session.refresh(entity)
        return self._entity_to_domain(entity)

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        entity = self._session.query(UserEntity).filter(UserEntity.id == user_id).first()
        return self._entity_to_domain(entity) if entity else None

    async def get_by_external_ref(self, client_id: UUID, external_ref: str) -> Optional[User]:
        entity = (
            self._session.query(UserEntity)
            .filter(UserEntity.client_id == client_id)
            .filter(UserEntity.external_ref == external_ref)
            .first()
        )
        return self._entity_to_domain(entity) if entity else None

    async def update(self, user: User) -> User:
        entity = self._session.query(UserEntity).filter(UserEntity.id == user.id).first()
        if not entity:
            raise ValueError(f"User {user.id} not found")
        entity.external_ref = user.external_ref
        entity.email = user.email
        entity.phone_number = user.phone_number
        entity.first_name = user.first_name
        entity.last_name = user.last_name
        entity.status = user.status
        self._session.commit()
        self._session.refresh(entity)
        return self._entity_to_domain(entity)

    async def list_by_client(self, client_id: UUID, limit: int = 100) -> List[User]:
        entities = (
            self._session.query(UserEntity)
            .filter(UserEntity.client_id == client_id)
            .order_by(UserEntity.created_at.desc())
            .limit(limit)
            .all()
        )
        return [self._entity_to_domain(entity) for entity in entities]
