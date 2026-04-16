from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4
from decimal import Decimal
from loguru import logger

from app.core.marketing_stack.models.lead import Lead
from app.core.marketing_stack.outbound.repositories.lead_repository import LeadRepository
from app.core.marketing_stack.outbound.external.messaging_port import MessagingPort
from app.core.marketing_stack.constants.status_constants import LeadStatus


class LeadService:
    """Captures leads from campaigns, routes to business owner, and handles auto-followup."""

    def __init__(
        self,
        lead_repository: LeadRepository,
        messaging_port: MessagingPort,
    ):
        self._lead_repo = lead_repository
        self._messaging = messaging_port

    async def capture_lead(
        self,
        client_id: UUID,
        phone_number: str,
        source_channel: str,
        source_campaign_tag: Optional[str] = None,
        name: Optional[str] = None,
    ) -> Lead:
        # Check for duplicate
        existing = await self._lead_repo.get_by_phone_and_client(phone_number, client_id)
        if existing:
            logger.info(f"Duplicate lead from {phone_number} for client {client_id}")
            return existing

        lead = Lead(
            id=uuid4(),
            client_id=client_id,
            name=name,
            phone_number=phone_number,
            source_channel=source_channel,
            source_campaign_tag=source_campaign_tag,
            status=LeadStatus.NEW,
        )

        lead = await self._lead_repo.create(lead)
        logger.info(f"Lead captured: {phone_number} from {source_channel} for client {client_id}")
        return lead

    async def notify_owner(self, lead: Lead, owner_phone: str) -> None:
        source = lead.source_channel.replace("_", " ").title()
        message = (
            f"New lead from {source}!\n\n"
            f"Name: {lead.name or 'Unknown'}\n"
            f"Phone: {lead.phone_number}\n"
        )
        if lead.source_campaign_tag:
            message += f"Campaign: {lead.source_campaign_tag}\n"
        message += f"\nRespond quickly — fast replies convert 3x better!"

        await self._messaging.send_text(to=owner_phone, body=message)

        lead.status = LeadStatus.NOTIFIED
        await self._lead_repo.update(lead)

    async def auto_followup(self, lead: Lead, business_name: str) -> None:
        if not lead.needs_followup():
            return

        message = (
            f"Hi{' ' + lead.name if lead.name else ''}! "
            f"Thanks for your interest in {business_name}. "
            f"Someone from our team will get back to you shortly!"
        )

        try:
            await self._messaging.send_text(to=lead.phone_number, body=message)
            lead.increment_followup()
            await self._lead_repo.update(lead)
            logger.info(f"Auto-followup sent to lead {lead.phone_number}")
        except Exception as e:
            logger.error(f"Auto-followup failed for {lead.phone_number}: {e}")

    async def mark_converted(self, lead_id: UUID, revenue: Decimal) -> Optional[Lead]:
        lead = await self._lead_repo.get_by_id(lead_id)
        if not lead:
            return None
        lead.mark_converted(revenue)
        return await self._lead_repo.update(lead)

    async def get_leads_needing_followup(self, client_id: UUID) -> List[Lead]:
        return await self._lead_repo.list_needs_followup(client_id)
