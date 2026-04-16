import pytest
from uuid import uuid4
from decimal import Decimal

from app.core.marketing_stack.services.lead_service import LeadService
from app.core.marketing_stack.constants.status_constants import LeadStatus


@pytest.mark.asyncio
async def test_capture_lead_creates_new_lead(mock_lead_repo, mock_messaging):
    service = LeadService(mock_lead_repo, mock_messaging)
    client_id = uuid4()

    lead = await service.capture_lead(
        client_id=client_id,
        phone_number="+919876543210",
        source_channel="whatsapp",
        source_campaign_tag="BREW-WA",
        name="Test Customer",
    )

    assert lead.client_id == client_id
    assert lead.source_channel == "whatsapp"
    assert lead.status == LeadStatus.NEW


@pytest.mark.asyncio
async def test_capture_lead_deduplicates(mock_lead_repo, mock_messaging):
    service = LeadService(mock_lead_repo, mock_messaging)
    client_id = uuid4()

    lead1 = await service.capture_lead(client_id, "+919876543210", "whatsapp")
    lead2 = await service.capture_lead(client_id, "+919876543210", "instagram")

    assert lead1.id == lead2.id  # Same lead returned


@pytest.mark.asyncio
async def test_notify_owner_sends_message(mock_lead_repo, mock_messaging):
    service = LeadService(mock_lead_repo, mock_messaging)
    client_id = uuid4()

    lead = await service.capture_lead(client_id, "+919876543210", "instagram", name="Rahul")
    await service.notify_owner(lead, "+919999999999")

    assert len(mock_messaging.sent_messages) == 1
    assert "New lead" in mock_messaging.sent_messages[0]["body"]
    assert "Rahul" in mock_messaging.sent_messages[0]["body"]


@pytest.mark.asyncio
async def test_auto_followup_sends_and_increments(mock_lead_repo, mock_messaging):
    service = LeadService(mock_lead_repo, mock_messaging)
    client_id = uuid4()

    lead = await service.capture_lead(client_id, "+919876543210", "whatsapp")

    await service.auto_followup(lead, "Brew Culture")

    assert len(mock_messaging.sent_messages) == 1
    assert "Brew Culture" in mock_messaging.sent_messages[0]["body"]
    assert lead.followup_count == 1


@pytest.mark.asyncio
async def test_mark_converted_updates_revenue(mock_lead_repo, mock_messaging):
    service = LeadService(mock_lead_repo, mock_messaging)
    client_id = uuid4()

    lead = await service.capture_lead(client_id, "+919876543210", "whatsapp")
    updated = await service.mark_converted(lead.id, Decimal("1500"))

    assert updated.status == "converted"
    assert updated.revenue_amount == Decimal("1500")
