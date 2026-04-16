from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.core.marketing_stack.models.conversation import Conversation
from app.core.marketing_stack.outbound.repositories.conversation_repository import ConversationRepository
from app.infra.marketing_stack.models.conversation_entity import ConversationEntity


class ConversationRepositoryImpl(ConversationRepository):
    """SQLAlchemy implementation of ConversationRepository."""

    def __init__(self, session: Session):
        self._session = session

    def _entity_to_domain(self, entity: ConversationEntity) -> Conversation:
        return Conversation(
            id=entity.id,
            client_id=entity.client_id,
            phone_number=entity.phone_number,
            direction=entity.direction,
            message_type=entity.message_type,
            wa_message_id=entity.wa_message_id,
            content=entity.content,
            metadata=entity.extra_data or {},
            context_type=entity.context_type,
            created_at=entity.created_at,
        )

    async def create(self, conversation: Conversation) -> Conversation:
        entity = ConversationEntity(
            id=conversation.id,
            client_id=conversation.client_id,
            phone_number=conversation.phone_number,
            direction=conversation.direction,
            message_type=conversation.message_type,
            wa_message_id=conversation.wa_message_id,
            content=conversation.content,
            extra_data=conversation.metadata,
            context_type=conversation.context_type,
        )
        self._session.add(entity)
        self._session.commit()
        self._session.refresh(entity)
        return self._entity_to_domain(entity)

    async def get_by_wa_message_id(self, wa_message_id: str) -> Optional[Conversation]:
        entity = (
            self._session.query(ConversationEntity)
            .filter(ConversationEntity.wa_message_id == wa_message_id)
            .first()
        )
        return self._entity_to_domain(entity) if entity else None

    async def get_recent_by_client(self, client_id: UUID, limit: int = 20) -> List[Conversation]:
        entities = (
            self._session.query(ConversationEntity)
            .filter(ConversationEntity.client_id == client_id)
            .order_by(ConversationEntity.created_at.desc())
            .limit(limit)
            .all()
        )
        return [self._entity_to_domain(e) for e in entities]

    async def get_recent_by_phone(self, phone_number: str, limit: int = 20) -> List[Conversation]:
        entities = (
            self._session.query(ConversationEntity)
            .filter(ConversationEntity.phone_number == phone_number)
            .order_by(ConversationEntity.created_at.desc())
            .limit(limit)
            .all()
        )
        return [self._entity_to_domain(e) for e in entities]
