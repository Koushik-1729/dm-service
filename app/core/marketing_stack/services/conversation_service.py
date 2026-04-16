from typing import List, Optional
from uuid import UUID, uuid4

from app.core.marketing_stack.models.conversation import Conversation
from app.core.marketing_stack.outbound.repositories.conversation_repository import ConversationRepository
from app.core.marketing_stack.constants.status_constants import ConversationDirection


class ConversationService:
    """Service for logging and retrieving WhatsApp conversations."""

    def __init__(self, conversation_repository: ConversationRepository):
        self._conversation_repo = conversation_repository

    async def log_inbound(
        self,
        client_id: Optional[UUID],
        phone_number: str,
        content: str,
        wa_message_id: str,
        message_type: str = "text",
        context_type: str = "onboarding",
        metadata: Optional[dict] = None,
    ) -> Conversation:
        conversation = Conversation(
            id=uuid4(),
            client_id=client_id,
            phone_number=phone_number,
            direction=ConversationDirection.INBOUND,
            message_type=message_type,
            wa_message_id=wa_message_id,
            content=content,
            metadata=metadata or {},
            context_type=context_type,
        )
        return await self._conversation_repo.create(conversation)

    async def log_outbound(
        self,
        client_id: Optional[UUID],
        phone_number: str,
        content: str,
        wa_message_id: str,
        message_type: str = "text",
        context_type: str = "onboarding",
        metadata: Optional[dict] = None,
    ) -> Conversation:
        conversation = Conversation(
            id=uuid4(),
            client_id=client_id,
            phone_number=phone_number,
            direction=ConversationDirection.OUTBOUND,
            message_type=message_type,
            wa_message_id=wa_message_id,
            content=content,
            metadata=metadata or {},
            context_type=context_type,
        )
        return await self._conversation_repo.create(conversation)

    async def get_context(self, phone_number: str, limit: int = 20) -> List[Conversation]:
        return await self._conversation_repo.get_recent_by_phone(phone_number, limit=limit)

    async def is_duplicate(self, wa_message_id: str) -> bool:
        existing = await self._conversation_repo.get_by_wa_message_id(wa_message_id)
        return existing is not None
