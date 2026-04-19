from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.core.marketing_stack.models.marketing_event import MarketingEvent


class MarketingEventRepository(ABC):
    @abstractmethod
    async def create(self, event: MarketingEvent) -> MarketingEvent:
        pass

    @abstractmethod
    async def get_by_id(self, event_id: UUID) -> Optional[MarketingEvent]:
        pass

    @abstractmethod
    async def list_by_user(self, user_id: UUID, limit: int = 100) -> List[MarketingEvent]:
        pass
