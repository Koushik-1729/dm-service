from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.core.marketing_stack.models.revenue_event import RevenueEvent


class RevenueEventRepository(ABC):
    @abstractmethod
    async def create(self, event: RevenueEvent) -> RevenueEvent:
        pass

    @abstractmethod
    async def get_by_id(self, revenue_event_id: UUID) -> Optional[RevenueEvent]:
        pass

    @abstractmethod
    async def list_by_user(self, user_id: UUID, limit: int = 100) -> List[RevenueEvent]:
        pass
