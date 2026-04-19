from decimal import Decimal
from uuid import uuid4

import pytest

from app.core.marketing_stack.services.conversation_service import ConversationService
from app.core.marketing_stack.services.event_ingestion_service import EventIngestionService
from app.core.marketing_stack.services.identity_service import IdentityService
from app.core.marketing_stack.services.journey_service import JourneyService


@pytest.fixture
def journey_service(
    mock_user_repo,
    mock_user_identity_repo,
    mock_marketing_event_repo,
    mock_conversion_event_repo,
    mock_revenue_event_repo,
    mock_messaging,
    mock_conversation_repo,
):
    identity = IdentityService(mock_user_repo, mock_user_identity_repo)
    event_ingestion = EventIngestionService(
        identity_service=identity,
        marketing_event_repository=mock_marketing_event_repo,
        conversion_event_repository=mock_conversion_event_repo,
        revenue_event_repository=mock_revenue_event_repo,
    )
    conversation = ConversationService(mock_conversation_repo)
    return JourneyService(
        user_repository=mock_user_repo,
        marketing_event_repository=mock_marketing_event_repo,
        event_ingestion_service=event_ingestion,
        messaging_port=mock_messaging,
        conversation_service=conversation,
    )


@pytest.mark.asyncio
async def test_register_user_sends_thank_you_and_logs_event(journey_service, mock_messaging):
    client_id = uuid4()

    result = await journey_service.register_user(
        client_id=client_id,
        external_ref="reg-001",
        phone_number="+919876543210",
        first_name="Asha",
        channel="facebook_ads",
        campaign_id="cmp_1",
    )

    assert result["user"].external_ref == "reg-001"
    assert result["thank_you_message_id"] is not None
    assert len(mock_messaging.sent_messages) == 1
    assert "Thanks Asha" in mock_messaging.sent_messages[0]["body"]


@pytest.mark.asyncio
async def test_no_conversion_followup_sends_followup_and_survey(journey_service, mock_messaging):
    client_id = uuid4()
    registration = await journey_service.register_user(
        client_id=client_id,
        external_ref="reg-002",
        phone_number="+919876543211",
    )

    result = await journey_service.trigger_no_conversion_followup(
        client_id=client_id,
        user_id=registration["user"].id,
    )

    assert result["followup_sent"] is True
    assert result["survey_event"] is not None
    assert len(mock_messaging.sent_messages) == 3
    assert mock_messaging.sent_messages[1]["type"] == "text"
    assert mock_messaging.sent_messages[2]["type"] == "interactive"


@pytest.mark.asyncio
async def test_no_conversion_followup_skips_converted_user(journey_service):
    client_id = uuid4()
    registration = await journey_service.register_user(
        client_id=client_id,
        external_ref="reg-003",
        phone_number="+919876543212",
    )
    await journey_service.record_conversion(
        client_id=client_id,
        user_id=registration["user"].id,
        conversion_type="purchase",
        revenue_amount=Decimal("999.00"),
    )

    result = await journey_service.trigger_no_conversion_followup(
        client_id=client_id,
        user_id=registration["user"].id,
    )

    assert result["followup_sent"] is False
    assert result["reason"] == "user_already_converted"


@pytest.mark.asyncio
async def test_record_survey_response_creates_event(journey_service):
    client_id = uuid4()
    registration = await journey_service.register_user(
        client_id=client_id,
        external_ref="reg-004",
        phone_number="+919876543213",
    )

    result = await journey_service.record_survey_response(
        client_id=client_id,
        user_id=registration["user"].id,
        response_text="Too expensive",
        response_code="survey_price",
    )

    assert result["survey_event"].event_type == "survey_completed"


@pytest.mark.asyncio
async def test_record_conversion_links_revenue(journey_service):
    client_id = uuid4()
    registration = await journey_service.register_user(
        client_id=client_id,
        external_ref="reg-005",
        phone_number="+919876543214",
    )

    result = await journey_service.record_conversion(
        client_id=client_id,
        user_id=registration["user"].id,
        conversion_type="service_signup",
        revenue_amount=Decimal("2499.00"),
        payment_reference="pay_005",
        channel="whatsapp",
    )

    assert result["conversion_event"] is not None
    assert result["revenue_event"] is not None
    assert result["revenue_event"].amount == Decimal("2499.00")
