from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class MessagingPort(ABC):
    """Abstract interface for messaging (WhatsApp, SMS, etc.)."""

    @abstractmethod
    async def send_text(self, to: str, body: str) -> str:
        """Send a plain text message. Returns message ID."""
        pass

    @abstractmethod
    async def send_template(
        self,
        to: str,
        template_name: str,
        language_code: str,
        parameters: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """Send a pre-approved template message. Returns message ID."""
        pass

    @abstractmethod
    async def send_interactive(
        self,
        to: str,
        body: str,
        buttons: List[Dict[str, str]],
    ) -> str:
        """Send interactive message with buttons. Returns message ID."""
        pass

    @abstractmethod
    async def send_image(
        self,
        to: str,
        image_url: str,
        caption: Optional[str] = None,
    ) -> str:
        """Send an image with optional caption. Returns message ID."""
        pass

    @abstractmethod
    async def mark_as_read(self, message_id: str) -> bool:
        """Mark a received message as read."""
        pass
