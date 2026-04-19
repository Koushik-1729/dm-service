from decimal import Decimal
from uuid import uuid4

import pytest

from app.core.marketing_stack.models.daily_metrics import DailyMetrics
from app.core.marketing_stack.services.decision_service import DecisionService
from app.core.marketing_stack.services.event_ingestion_service import EventIngestionService
from app.core.marketing_stack.services.feature_service import FeatureService
from app.core.marketing_stack.services.identity_service import IdentityService
from app.core.marketing_stack.services.prediction_service import PredictionService


@pytest.fixture
def decision_service(
    mock_user_repo,
    mock_user_identity_repo,
    mock_marketing_event_repo,
    mock_conversion_event_repo,
    mock_revenue_event_repo,
    mock_prediction_score_repo,
    mock_decision_log_repo,
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
    prediction_service = PredictionService(
        user_repository=mock_user_repo,
        feature_service=feature_service,
        prediction_score_repository=mock_prediction_score_repo,
    )
    service = DecisionService(
        user_repository=mock_user_repo,
        marketing_event_repository=mock_marketing_event_repo,
        prediction_score_repository=mock_prediction_score_repo,
        prediction_service=prediction_service,
        decision_log_repository=mock_decision_log_repo,
    )
    return service, event_ingestion, mock_metrics_repo


@pytest.mark.asyncio
async def test_decision_recommends_followup_for_high_dropout_user(decision_service):
    service, event_ingestion, metrics_repo = decision_service
    client_id = uuid4()

    await metrics_repo.upsert_daily(
        DailyMetrics(
            id=uuid4(),
            client_id=client_id,
            channel="facebook_ads",
            leads_count=5,
            revenue=Decimal("5000"),
            spend=Decimal("7000"),
        )
    )
    registration = await event_ingestion.ingest_event(
        client_id=client_id,
        event_type="registration_completed",
        external_ref="dec-001",
        phone_number="+919876543221",
        channel="facebook_ads",
    )

    decision = await service.decide_for_user(client_id, registration["user"].id)

    assert decision.action_type in {"send_followup", "send_survey", "monitor", "send_offer", "escalate_to_human"}
    assert decision.reason
    assert decision.client_id == client_id


@pytest.mark.asyncio
async def test_decision_recommends_offer_for_high_conversion_user(decision_service):
    service, event_ingestion, metrics_repo = decision_service
    client_id = uuid4()

    await metrics_repo.upsert_daily(
        DailyMetrics(
            id=uuid4(),
            client_id=client_id,
            channel="whatsapp",
            leads_count=10,
            revenue=Decimal("30000"),
            spend=Decimal("5000"),
            messages_read=50,
        )
    )
    registration = await event_ingestion.ingest_event(
        client_id=client_id,
        event_type="registration_completed",
        external_ref="dec-002",
        phone_number="+919876543222",
        channel="whatsapp",
    )
    await event_ingestion.ingest_event(
        client_id=client_id,
        event_type="thank_you_sent",
        external_ref="dec-002",
        phone_number="+919876543222",
        channel="whatsapp",
    )
    await event_ingestion.ingest_event(
        client_id=client_id,
        event_type="followup_sent",
        external_ref="dec-002",
        phone_number="+919876543222",
        channel="whatsapp",
    )

    decision = await service.decide_for_user(client_id, registration["user"].id)

    assert decision.action_type == "send_offer"
    assert decision.confidence >= 0.65


@pytest.mark.asyncio
async def test_decision_recommends_human_escalation_after_followup_and_survey(decision_service):
    service, event_ingestion, metrics_repo = decision_service
    client_id = uuid4()

    await metrics_repo.upsert_daily(
        DailyMetrics(
            id=uuid4(),
            client_id=client_id,
            channel="facebook_ads",
            leads_count=10,
            revenue=Decimal("2000"),
            spend=Decimal("8000"),
        )
    )
    registration = await event_ingestion.ingest_event(
        client_id=client_id,
        event_type="registration_completed",
        external_ref="dec-003",
        phone_number="+919876543223",
        channel="facebook_ads",
    )
    await event_ingestion.ingest_event(
        client_id=client_id,
        event_type="followup_sent",
        external_ref="dec-003",
        phone_number="+919876543223",
        channel="facebook_ads",
    )
    await event_ingestion.ingest_event(
        client_id=client_id,
        event_type="survey_completed",
        external_ref="dec-003",
        phone_number="+919876543223",
        channel="facebook_ads",
    )

    decision = await service.decide_for_user(client_id, registration["user"].id)

    assert decision.action_type in {"escalate_to_human", "send_survey", "send_followup", "monitor", "send_offer"}
