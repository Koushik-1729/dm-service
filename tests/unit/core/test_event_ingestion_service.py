from decimal import Decimal
from uuid import uuid4

import pytest

from app.core.marketing_stack.services.event_ingestion_service import EventIngestionService
from app.core.marketing_stack.services.identity_service import IdentityService


@pytest.mark.asyncio
async def test_ingest_registration_creates_user_and_event(
    mock_user_repo,
    mock_user_identity_repo,
    mock_marketing_event_repo,
    mock_conversion_event_repo,
    mock_revenue_event_repo,
):
    identity = IdentityService(mock_user_repo, mock_user_identity_repo)
    service = EventIngestionService(
        identity_service=identity,
        marketing_event_repository=mock_marketing_event_repo,
        conversion_event_repository=mock_conversion_event_repo,
        revenue_event_repository=mock_revenue_event_repo,
    )

    client_id = uuid4()
    result = await service.ingest_event(
        client_id=client_id,
        event_type="registration_completed",
        external_ref="lead-123",
        email="Person@Example.com",
        phone_number="+91 98765 43210",
        metadata={"landing_page": "summer-offer"},
    )

    assert result["user"].client_id == client_id
    assert result["user"].email == "person@example.com"
    assert result["user"].phone_number == "+919876543210"
    assert result["marketing_event"].event_type == "registration_completed"
    assert result["conversion_event"] is None
    assert result["revenue_event"] is None


@pytest.mark.asyncio
async def test_ingest_purchase_reuses_identity_and_creates_conversion_and_revenue(
    mock_user_repo,
    mock_user_identity_repo,
    mock_marketing_event_repo,
    mock_conversion_event_repo,
    mock_revenue_event_repo,
):
    identity = IdentityService(mock_user_repo, mock_user_identity_repo)
    service = EventIngestionService(
        identity_service=identity,
        marketing_event_repository=mock_marketing_event_repo,
        conversion_event_repository=mock_conversion_event_repo,
        revenue_event_repository=mock_revenue_event_repo,
    )

    client_id = uuid4()
    first = await service.ingest_event(
        client_id=client_id,
        event_type="registration_completed",
        external_ref="lead-123",
        email="person@example.com",
    )
    second = await service.ingest_event(
        client_id=client_id,
        event_type="purchase_completed",
        external_ref="lead-123",
        revenue_amount=Decimal("1499.00"),
        currency="INR",
        payment_reference="pay_001",
    )

    assert first["user"].id == second["user"].id
    assert second["conversion_event"] is not None
    assert second["conversion_event"].conversion_type == "purchase_completed"
    assert second["revenue_event"] is not None
    assert second["revenue_event"].amount == Decimal("1499.00")
