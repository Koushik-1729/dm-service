from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.core.marketing_stack.models.client import Client


class ClientRepository(ABC):
    """Abstract repository interface for Client operations."""

    @abstractmethod
    async def create(self, client: Client) -> Client:
        pass

    @abstractmethod
    async def get_by_id(self, client_id: UUID) -> Optional[Client]:
        pass

    @abstractmethod
    async def get_by_phone(self, phone_number: str) -> Optional[Client]:
        pass

    @abstractmethod
    async def update(self, client: Client) -> Client:
        pass

    @abstractmethod
    async def list_active(self) -> List[Client]:
        pass

    @abstractmethod
    async def list_by_sector(self, sector: str) -> List[Client]:
        pass
