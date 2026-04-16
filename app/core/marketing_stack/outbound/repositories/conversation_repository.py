from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.core.marketing_stack.models.conversation import Conversation


class ConversationRepository(ABC):
    """Abstract repository interface for Conversation (WhatsApp message log) operations."""

    @abstractmethod
    async def create(self, conversation: Conversation) -> Conversation:
        pass

    @abstractmethod
    async def get_by_wa_message_id(self, wa_message_id: str) -> Optional[Conversation]:
        pass

    @abstractmethod
    async def get_recent_by_client(self, client_id: UUID, limit: int = 20) -> List[Conversation]:
        pass

    @abstractmethod
    async def get_recent_by_phone(self, phone_number: str, limit: int = 20) -> List[Conversation]:
        pass
