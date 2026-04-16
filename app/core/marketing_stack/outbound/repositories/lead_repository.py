from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.core.marketing_stack.models.lead import Lead


class LeadRepository(ABC):
    """Abstract repository interface for Lead operations."""

    @abstractmethod
    async def create(self, lead: Lead) -> Lead:
        pass

    @abstractmethod
    async def get_by_id(self, lead_id: UUID) -> Optional[Lead]:
        pass

    @abstractmethod
    async def get_by_phone_and_client(self, phone_number: str, client_id: UUID) -> Optional[Lead]:
        pass

    @abstractmethod
    async def list_by_client(self, client_id: UUID, status: Optional[str] = None) -> List[Lead]:
        pass

    @abstractmethod
    async def list_needs_followup(self, client_id: UUID, max_followups: int = 3) -> List[Lead]:
        pass

    @abstractmethod
    async def update(self, lead: Lead) -> Lead:
        pass

    @abstractmethod
    async def count_by_source(self, client_id: UUID, days: int = 7) -> dict:
        pass
