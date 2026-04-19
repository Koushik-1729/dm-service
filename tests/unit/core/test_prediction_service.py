from decimal import Decimal
from uuid import uuid4

import pytest

from app.core.marketing_stack.models.daily_metrics import DailyMetrics
from app.core.marketing_stack.services.event_ingestion_service import EventIngestionService
from app.core.marketing_stack.services.feature_service import FeatureService
from app.core.marketing_stack.services.identity_service import IdentityService
from app.core.marketing_stack.services.prediction_service import PredictionService


@pytest.fixture
def prediction_service(
    mock_user_repo,
    mock_user_identity_repo,
    mock_marketing_event_repo,
    mock_conversion_event_repo,
    mock_revenue_event_repo,
    mock_prediction_score_repo,
    mock_metrics_repo,
):
    identity = IdentityService(mock_user_repo, mock_user_identity_repo)
    event_ingestion = EventIngestionService(
        identity_service=identity,
        marketing_event_repository=mock_marketing_event_repo,
        conversion_event_repository=mock_conversion_event_repo,
        revenue_event_repository=mock_revenue_event_repo,
    )

    feature_service = FeatureService(
        user_repository=mock_user_repo,
        marketing_event_repository=mock_marketing_event_repo,
        metrics_repository=mock_metrics_repo,
    )
    service = PredictionService(
        user_repository=mock_user_repo,
        feature_service=feature_service,
        prediction_score_repository=mock_prediction_score_repo,
    )
    return service, event_ingestion, mock_metrics_repo


@pytest.mark.asyncio
async def test_score_user_creates_prediction_snapshot(prediction_service):
    service, event_ingestion, metrics_repo = prediction_service
    client_id = uuid4()

    await metrics_repo.upsert_daily(
        DailyMetrics(
            id=uuid4(),
            client_id=client_id,
            channel="facebook_ads",
            impressions=1000,
            clicks=50,
            leads_count=10,
            revenue=Decimal("20000"),
            spend=Decimal("5000"),
        )
    )

    registration = await event_ingestion.ingest_event(
        client_id=client_id,
        event_type="registration_completed",
        external_ref="pred-001",
        phone_number="+919876543219",
        channel="facebook_ads",
    )
    await event_ingestion.ingest_event(
        client_id=client_id,
        event_type="thank_you_sent",
        external_ref="pred-001",
        phone_number="+919876543219",
        channel="facebook_ads",
    )
    await event_ingestion.ingest_event(
        client_id=client_id,
        event_type="followup_sent",
        external_ref="pred-001",
        phone_number="+919876543219",
        channel="facebook_ads",
    )

    prediction = await service.score_user(client_id, registration["user"].id)

    assert prediction.client_id == client_id
    assert prediction.user_id == registration["user"].id
    assert prediction.model_name == "baseline_v1"
    assert prediction.conversion_probability > 0
    assert prediction.dropout_risk > 0
    assert prediction.expected_revenue > Decimal("0")


@pytest.mark.asyncio
async def test_score_converted_user_has_low_dropout_and_high_conversion(prediction_service):
    service, event_ingestion, _ = prediction_service
    client_id = uuid4()

    registration = await event_ingestion.ingest_event(
        client_id=client_id,
        event_type="registration_completed",
        external_ref="pred-002",
        phone_number="+919876543220",
        channel="whatsapp",
    )
    await event_ingestion.ingest_event(
        client_id=client_id,
        event_type="purchase_completed",
        external_ref="pred-002",
        phone_number="+919876543220",
        revenue_amount=Decimal("1499.00"),
        channel="whatsapp",
    )

    prediction = await service.score_user(client_id, registration["user"].id)

    assert prediction.conversion_probability == 0.99
    assert prediction.dropout_risk == 0.01
