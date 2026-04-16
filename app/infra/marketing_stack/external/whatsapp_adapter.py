from typing import List, Dict, Any, Optional
from loguru import logger
import httpx

from app.core.marketing_stack.outbound.external.messaging_port import MessagingPort
from app.common.constants import WHATSAPP_API_BASE
from app.monitoring.metrics import WHATSAPP_MESSAGES_SENT


class WhatsAppAdapter(MessagingPort):
    """Meta WhatsApp Cloud API adapter implementing MessagingPort."""

    def __init__(self, phone_number_id: str, access_token: str):
        self._phone_number_id = phone_number_id
        self._access_token = access_token
        self._base_url = f"{WHATSAPP_API_BASE}/{phone_number_id}/messages"
        self._headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    async def send_text(self, to: str, body: str) -> str:
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {"preview_url": False, "body": body},
        }
        message_id = await self._send(payload)
        WHATSAPP_MESSAGES_SENT.labels(message_type="text").inc()
        return message_id

    async def send_template(
        self,
        to: str,
        template_name: str,
        language_code: str,
        parameters: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        components = []
        if parameters:
            components.append({
                "type": "body",
                "parameters": parameters,
            })

        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language_code},
                "components": components,
            },
        }
        message_id = await self._send(payload)
        WHATSAPP_MESSAGES_SENT.labels(message_type="template").inc()
        return message_id

    async def send_interactive(
        self,
        to: str,
        body: str,
        buttons: List[Dict[str, str]],
    ) -> str:
        button_objects = []
        for btn in buttons[:3]:  # WhatsApp allows max 3 buttons
            button_objects.append({
                "type": "reply",
                "reply": {
                    "id": btn.get("id", btn.get("title", "")[:20]),
                    "title": btn.get("title", "")[:20],  # Max 20 chars
                },
            })

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": body},
                "action": {"buttons": button_objects},
            },
        }
        message_id = await self._send(payload)
        WHATSAPP_MESSAGES_SENT.labels(message_type="interactive").inc()
        return message_id

    async def send_image(
        self,
        to: str,
        image_url: str,
        caption: Optional[str] = None,
    ) -> str:
        image_obj = {"link": image_url}
        if caption:
            image_obj["caption"] = caption

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "image",
            "image": image_obj,
        }
        message_id = await self._send(payload)
        WHATSAPP_MESSAGES_SENT.labels(message_type="image").inc()
        return message_id

    async def mark_as_read(self, message_id: str) -> bool:
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id,
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    self._base_url,
                    json=payload,
                    headers=self._headers,
                )
                return response.status_code == 200
        except Exception as e:
            logger.debug(f"Failed to mark message as read: {e}")
            return False

    async def _send(self, payload: dict) -> str:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self._base_url,
                    json=payload,
                    headers=self._headers,
                )

                if response.status_code not in (200, 201):
                    error_body = response.text
                    logger.error(
                        f"WhatsApp API error: status={response.status_code} "
                        f"body={error_body[:500]}"
                    )
                    response.raise_for_status()

                data = response.json()
                message_id = data.get("messages", [{}])[0].get("id", "")
                logger.debug(f"WhatsApp message sent: id={message_id} to={payload.get('to')}")
                return message_id

        except httpx.TimeoutException:
            logger.error(f"WhatsApp API timeout sending to {payload.get('to')}")
            raise
        except httpx.HTTPStatusError as e:
            logger.error(f"WhatsApp HTTP error: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"WhatsApp send failed: {type(e).__name__}: {e}")
            raise
