from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.core.marketing_stack.models.strategy import Strategy


class StrategyRepository(ABC):
    """Abstract repository interface for Strategy operations."""

    @abstractmethod
    async def create(self, strategy: Strategy) -> Strategy:
        pass

    @abstractmethod
    async def get_by_id(self, strategy_id: UUID) -> Optional[Strategy]:
        pass

    @abstractmethod
    async def get_active_by_client(self, client_id: UUID) -> Optional[Strategy]:
        pass

    @abstractmethod
    async def update(self, strategy: Strategy) -> Strategy:
        pass

    @abstractmethod
    async def list_by_client(self, client_id: UUID) -> List[Strategy]:
        pass
