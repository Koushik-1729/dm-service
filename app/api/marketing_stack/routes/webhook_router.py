from fastapi import APIRouter, Depends, Query, Request, Response, HTTPException
from loguru import logger

from app.config.app_config import app_config
from app.core.marketing_stack.services.orchestrator_service import OrchestratorService
from app.api.marketing_stack.marketing_dependencies import get_orchestrator_service

router = APIRouter(prefix="/webhook", tags=["WhatsApp Webhook"])


@router.get("/whatsapp")
async def verify_webhook(
    request: Request,
) -> Response:
    """WhatsApp webhook verification endpoint (called by Meta during setup)."""
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == app_config.whatsapp_verify_token:
        logger.info("WhatsApp webhook verified successfully")
        return Response(content=challenge, media_type="text/plain")

    logger.warning(f"Webhook verification failed: mode={mode}, token={token}")
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/whatsapp")
async def receive_webhook(
    request: Request,
    service: OrchestratorService = Depends(get_orchestrator_service),
) -> dict:
    """Receive incoming WhatsApp messages and status updates."""
    try:
        payload = await request.json()
    except Exception:
        logger.error("Failed to parse webhook payload")
        return {"status": "error", "message": "Invalid JSON"}

    # Extract messages from Meta's nested webhook structure
    entries = payload.get("entry", [])
    for entry in entries:
        changes = entry.get("changes", [])
        for change in changes:
            value = change.get("value", {})

            # Handle incoming messages
            messages = value.get("messages", [])
            for message in messages:
                from_number = message.get("from", "")
                message_id = message.get("id", "")
                message_type = message.get("type", "text")

                # Extract text content based on message type
                text_body = ""
                metadata = {}

                if message_type == "text":
                    text_body = message.get("text", {}).get("body", "")

                elif message_type == "interactive":
                    interactive = message.get("interactive", {})
                    reply_type = interactive.get("type", "")
                    if reply_type == "button_reply":
                        reply = interactive.get("button_reply", {})
                        text_body = reply.get("title", "")
                        metadata["button_id"] = reply.get("id", "")
                    elif reply_type == "list_reply":
                        reply = interactive.get("list_reply", {})
                        text_body = reply.get("title", "")
                        metadata["list_id"] = reply.get("id", "")

                elif message_type == "image":
                    image = message.get("image", {})
                    text_body = image.get("caption", "")
                    metadata["image_id"] = image.get("id", "")
                    metadata["mime_type"] = image.get("mime_type", "")

                elif message_type == "button":
                    text_body = message.get("button", {}).get("text", "")
                    metadata["button_payload"] = message.get("button", {}).get("payload", "")

                if from_number and message_id:
                    try:
                        await service.handle_incoming_message(
                            phone_number=from_number,
                            message_text=text_body,
                            wa_message_id=message_id,
                            message_type=message_type,
                            metadata=metadata if metadata else None,
                        )
                    except Exception as e:
                        logger.error(
                            f"Error processing message from {from_number}: "
                            f"{type(e).__name__}: {e}"
                        )

            # Handle status updates (delivered, read, etc.)
            statuses = value.get("statuses", [])
            for status in statuses:
                logger.debug(
                    f"WhatsApp status update: id={status.get('id')} "
                    f"status={status.get('status')} "
                    f"recipient={status.get('recipient_id')}"
                )

    return {"status": "ok"}
