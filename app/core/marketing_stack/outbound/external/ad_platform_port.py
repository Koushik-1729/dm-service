from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from decimal import Decimal


class AdPlatformPort(ABC):
    """Abstract interface for ad platforms (Meta Ads, Google Ads). Phase 2."""

    @abstractmethod
    async def create_campaign(
        self,
        name: str,
        objective: str,
        daily_budget: Decimal,
        targeting: Dict[str, Any],
        creative: Dict[str, Any],
    ) -> str:
        """Create an ad campaign. Returns platform campaign ID."""
        pass

    @abstractmethod
    async def get_campaign_metrics(self, campaign_id: str) -> Dict[str, Any]:
        """Get performance metrics for a campaign."""
        pass

    @abstractmethod
    async def pause_campaign(self, campaign_id: str) -> bool:
        """Pause a running campaign."""
        pass

    @abstractmethod
    async def resume_campaign(self, campaign_id: str) -> bool:
        """Resume a paused campaign."""
        pass

    @abstractmethod
    async def update_budget(self, campaign_id: str, daily_budget: Decimal) -> bool:
        """Update a campaign's daily budget."""
        pass
