from abc import ABC, abstractmethod
from typing import Dict, Any


class WebScraperPort(ABC):
    """Abstract interface for web scraping operations."""

    @abstractmethod
    async def scrape_url(self, url: str) -> Dict[str, Any]:
        """Scrape a website and extract business-relevant information."""
        pass

    @abstractmethod
    async def scrape_google_maps(self, url: str) -> Dict[str, Any]:
        """Scrape Google Maps listing for business data."""
        pass
