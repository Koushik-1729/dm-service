from abc import ABC, abstractmethod
from datetime import date
from typing import Dict, Any, List
from uuid import UUID

from app.core.marketing_stack.models.usage import Usage


class UsageRepository(ABC):
    """Abstract repository interface for Usage (billing events) operations."""

    @abstractmethod
    async def create(self, usage: Usage) -> Usage:
        pass

    @abstractmethod
    async def get_total_by_client(
        self,
        client_id: UUID,
        start_date: date,
        end_date: date,
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def list_by_client(self, client_id: UUID, limit: int = 100) -> List[Usage]:
        pass
