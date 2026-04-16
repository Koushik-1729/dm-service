"""
Integration test for the full onboarding flow.
Tests the complete WhatsApp message → onboarding → strategy → content pipeline.

Requires mock AI and messaging adapters (no real API calls).
"""
import pytest
import json
from uuid import uuid4

from app.core.marketing_stack.services.orchestrator_service import OrchestratorService
from app.core.marketing_stack.services.onboarding_service import OnboardingService
from app.core.marketing_stack.services.strategy_service import StrategyService
from app.core.marketing_stack.services.content_service import ContentService
from app.core.marketing_stack.services.execution_service import ExecutionService
from app.core.marketing_stack.services.lead_service import LeadService
from app.core.marketing_stack.services.attribution_service import AttributionService
from app.core.marketing_stack.services.conversation_service import ConversationService
from tests.conftest import (
    MockClientRepository, MockConversationRepository, MockStrategyRepository,
    MockContentRepository, MockCampaignRepository, MockLeadRepository,
    MockMetricsRepository, MockAIProvider, MockWebScraper,
    MockMessagingPort, MockSocialMediaPort, MockPlaybookLoader,
)


@pytest.fixture
def orchestrator():
    client_repo = MockClientRepository()
    conversation_repo = MockConversationRepository()
    strategy_repo = MockStrategyRepository()
    content_repo = MockContentRepository()
    campaign_repo = MockCampaignRepository()
    lead_repo = MockLeadRepository()
    metrics_repo = MockMetricsRepository()
    messaging = MockMessagingPort()
    social_media = MockSocialMediaPort()
    playbook_loader = MockPlaybookLoader()

    # AI that returns valid JSON for each layer
    ai_provider = MockAIProvider(response=json.dumps({
        "sector": "restaurant",
        "business_name": "Test Cafe",
        "city": "Hyderabad",
        "locality": "Jubilee Hills",
        "language": "english",
        "target_audience": {"demographics": "IT professionals"},
        "unique_selling_points": ["Great coffee"],
        "services_offered": ["Coffee", "Snacks"],
    }))

    onboarding = OnboardingService(client_repo, ai_provider, MockWebScraper(), playbook_loader)
    strategy = StrategyService(strategy_repo, ai_provider, playbook_loader)
    content = ContentService(content_repo, ai_provider)
    execution = ExecutionService(content_repo, campaign_repo, messaging, social_media)
    lead = LeadService(lead_repo, messaging)
    attribution = AttributionService(lead_repo, metrics_repo)
    conversation = ConversationService(conversation_repo)

    return OrchestratorService(
        client_repository=client_repo,
        onboarding_service=onboarding,
        strategy_service=strategy,
        content_service=content,
        execution_service=execution,
        lead_service=lead,
        attribution_service=attribution,
        conversation_service=conversation,
        messaging_port=messaging,
    ), messaging, client_repo


@pytest.mark.asyncio
async def test_full_onboarding_flow(orchestrator):
    service, messaging, client_repo = orchestrator

    # Message 1: Hi
    await service.handle_incoming_message("+919876543210", "Hi", "wamid.1")

    # Should have sent welcome + Q1
    assert len(messaging.sent_messages) >= 1
    assert "Welcome" in messaging.sent_messages[0]["body"]

    # Answer all 6 questions
    answers = [
        ("Test Cafe, Jubilee Hills, Hyderabad", "wamid.2"),
        ("Coffee, snacks, cold brew", "wamid.3"),
        ("IT professionals, students", "wamid.4"),
        ("Rs 150-400", "wamid.5"),
        ("Open till midnight, pet friendly", "wamid.6"),
        ("photos coming", "wamid.7"),
    ]

    for answer, msg_id in answers:
        await service.handle_incoming_message("+919876543210", answer, msg_id)

    # Client should be onboarded
    client = await client_repo.get_by_phone("+919876543210")
    assert client is not None
    assert client.onboarding_status == "complete"

    # Strategy + content should have been generated (post-onboarding flow)
    # Messaging should have sent the strategy summary + approval buttons
    assert len(messaging.sent_messages) > 6  # welcome + 5 question responses + strategy


@pytest.mark.asyncio
async def test_duplicate_message_ignored(orchestrator):
    service, messaging, client_repo = orchestrator

    await service.handle_incoming_message("+919876543210", "Hi", "wamid.dup1")
    msg_count_after_first = len(messaging.sent_messages)

    await service.handle_incoming_message("+919876543210", "Hi", "wamid.dup1")
    msg_count_after_dup = len(messaging.sent_messages)

    assert msg_count_after_first == msg_count_after_dup  # No new messages sent


@pytest.mark.asyncio
async def test_url_based_onboarding(orchestrator):
    service, messaging, client_repo = orchestrator

    await service.handle_incoming_message("+919876543210", "Hi", "wamid.url1")
    await service.handle_incoming_message("+919876543210", "https://www.testcafe.com", "wamid.url2")

    client = await client_repo.get_by_phone("+919876543210")
    assert client.onboarding_status == "complete"
    assert client.website_url == "https://www.testcafe.com"
