from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from app.core.marketing_stack.models.content import Content


class ContentRepository(ABC):
    """Abstract repository interface for Content operations."""

    @abstractmethod
    async def create(self, content: Content) -> Content:
        pass

    @abstractmethod
    async def create_batch(self, contents: List[Content]) -> List[Content]:
        pass

    @abstractmethod
    async def get_by_id(self, content_id: UUID) -> Optional[Content]:
        pass

    @abstractmethod
    async def list_by_client(
        self,
        client_id: UUID,
        status: Optional[str] = None,
        channel: Optional[str] = None,
    ) -> List[Content]:
        pass

    @abstractmethod
    async def get_scheduled(self, before: datetime) -> List[Content]:
        pass

    @abstractmethod
    async def list_by_variant_group(self, variant_group: str) -> List[Content]:
        pass

    @abstractmethod
    async def update(self, content: Content) -> Content:
        pass
