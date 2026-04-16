from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class GMBPort(ABC):
    """Abstract interface for Google Business Profile. Phase 2."""

    @abstractmethod
    async def create_post(
        self,
        location_id: str,
        summary: str,
        media_url: Optional[str] = None,
        call_to_action: Optional[Dict[str, str]] = None,
    ) -> str:
        """Create a Google Business Profile post. Returns post ID."""
        pass

    @abstractmethod
    async def get_reviews(self, location_id: str, page_size: int = 20) -> List[Dict[str, Any]]:
        """Get recent reviews for a location."""
        pass

    @abstractmethod
    async def respond_to_review(self, review_id: str, response_text: str) -> bool:
        """Respond to a Google review."""
        pass

    @abstractmethod
    async def get_insights(self, location_id: str) -> Dict[str, Any]:
        """Get location insights (direction clicks, calls, views)."""
        pass
