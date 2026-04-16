from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class WebhookVerifyParams(BaseModel):
    """Query parameters for WhatsApp webhook verification (GET)."""
    hub_mode: str
    hub_challenge: str
    hub_verify_token: str


class WhatsAppMessage(BaseModel):
    """Extracted message from WhatsApp webhook payload."""
    from_number: str
    message_id: str
    timestamp: str
    message_type: str = "text"
    text_body: Optional[str] = None
    image_url: Optional[str] = None
    button_payload: Optional[str] = None
    interactive_reply_id: Optional[str] = None
    interactive_reply_title: Optional[str] = None


class WebhookStatusUpdate(BaseModel):
    """Status update from WhatsApp (delivered, read, failed)."""
    message_id: str
    status: str  
    timestamp: str
    recipient_id: str
