from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.core.marketing_stack.models.conversion_event import ConversionEvent


class ConversionEventRepository(ABC):
    @abstractmethod
    async def create(self, event: ConversionEvent) -> ConversionEvent:
        pass

    @abstractmethod
    async def get_by_id(self, conversion_event_id: UUID) -> Optional[ConversionEvent]:
        pass

    @abstractmethod
    async def list_by_user(self, user_id: UUID, limit: int = 100) -> List[ConversionEvent]:
        pass
