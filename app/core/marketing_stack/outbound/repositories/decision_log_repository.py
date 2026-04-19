from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.core.marketing_stack.models.decision_log import DecisionLog


class DecisionLogRepository(ABC):
    @abstractmethod
    async def create(self, decision: DecisionLog) -> DecisionLog:
        pass

    @abstractmethod
    async def get_latest_by_user(self, user_id: UUID) -> Optional[DecisionLog]:
        pass

    @abstractmethod
    async def list_by_client(self, client_id: UUID, limit: int = 100) -> List[DecisionLog]:
        pass
