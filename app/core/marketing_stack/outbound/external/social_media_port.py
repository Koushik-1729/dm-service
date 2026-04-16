from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class SocialMediaPort(ABC):
    """Abstract interface for social media publishing (Instagram, Facebook, etc.)."""

    @abstractmethod
    async def publish_post(
        self,
        image_url: str,
        caption: str,
    ) -> str:
        """Publish a single image post. Returns platform post ID."""
        pass

    @abstractmethod
    async def publish_carousel(
        self,
        image_urls: List[str],
        caption: str,
    ) -> str:
        """Publish a carousel post. Returns platform post ID."""
        pass

    @abstractmethod
    async def get_post_insights(self, post_id: str) -> Dict[str, Any]:
        """Get engagement metrics for a specific post."""
        pass

    @abstractmethod
    async def get_account_insights(
        self,
        period: str = "day",
        metrics: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Get account-level insights (followers, reach, etc.)."""
        pass
