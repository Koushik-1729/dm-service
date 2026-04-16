from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID


class Conversation:
    """Domain model representing a WhatsApp message (inbound or outbound)."""

    def __init__(
        self,
        id: Optional[UUID] = None,
        client_id: Optional[UUID] = None,
        phone_number: str = "",
        direction: str = "inbound",
        message_type: str = "text",
        wa_message_id: Optional[str] = None,
        content: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        context_type: str = "onboarding",
        created_at: Optional[datetime] = None,
    ):
        self.id = id
        self.client_id = client_id
        self.phone_number = phone_number
        self.direction = direction
        self.message_type = message_type
        self.wa_message_id = wa_message_id
        self.content = content
        self.metadata = metadata or {}
        self.context_type = context_type
        self.created_at = created_at

    def is_inbound(self) -> bool:
        return self.direction == "inbound"

    def is_outbound(self) -> bool:
        return self.direction == "outbound"
