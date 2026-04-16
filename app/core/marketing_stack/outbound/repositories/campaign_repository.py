from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.core.marketing_stack.models.campaign import Campaign


class CampaignRepository(ABC):
    """Abstract repository interface for Campaign operations."""

    @abstractmethod
    async def create(self, campaign: Campaign) -> Campaign:
        pass

    @abstractmethod
    async def get_by_id(self, campaign_id: UUID) -> Optional[Campaign]:
        pass

    @abstractmethod
    async def list_active_by_client(self, client_id: UUID) -> List[Campaign]:
        pass

    @abstractmethod
    async def update(self, campaign: Campaign) -> Campaign:
        pass

    @abstractmethod
    async def list_by_channel(self, client_id: UUID, channel: str) -> List[Campaign]:
        pass
