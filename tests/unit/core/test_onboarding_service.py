import pytest
import json
from uuid import uuid4

from app.core.marketing_stack.services.onboarding_service import OnboardingService
from app.core.marketing_stack.constants.status_constants import OnboardingStatus


@pytest.mark.asyncio
async def test_first_message_returns_welcome(mock_client_repo, mock_ai_provider, mock_scraper, mock_playbook_loader):
    service = OnboardingService(mock_client_repo, mock_ai_provider, mock_scraper, mock_playbook_loader)

    response = await service.handle_message("+919876543210", "Hi")

    assert "Welcome" in response
    assert "Question 1" in response


@pytest.mark.asyncio
async def test_records_answer_and_asks_next(mock_client_repo, mock_ai_provider, mock_scraper, mock_playbook_loader):
    service = OnboardingService(mock_client_repo, mock_ai_provider, mock_scraper, mock_playbook_loader)

    # First message — get welcome + Q1
    await service.handle_message("+919876543210", "Hi")

    # Answer Q1
    response = await service.handle_message("+919876543210", "Brew Culture, Jubilee Hills, Hyderabad")

    assert "Question 2" in response

    client = await mock_client_repo.get_by_phone("+919876543210")
    assert client.current_question_index == 1
    assert "q1_business_info" in client.onboarding_answers


@pytest.mark.asyncio
async def test_url_triggers_scraping(mock_client_repo, mock_ai_provider, mock_scraper, mock_playbook_loader):
    mock_ai_provider._response = json.dumps({
        "sector": "restaurant",
        "business_name": "Test Cafe",
        "city": "Hyderabad",
        "language": "english",
    })
    service = OnboardingService(mock_client_repo, mock_ai_provider, mock_scraper, mock_playbook_loader)

    # Create client first
    await service.get_or_create_client("+919876543210")

    response = await service.handle_message("+919876543210", "https://www.testcafe.com")

    assert "30 seconds" in response or "marketing plan" in response.lower()

    client = await mock_client_repo.get_by_phone("+919876543210")
    assert client.onboarding_status == OnboardingStatus.COMPLETE
    assert client.scraped_data


@pytest.mark.asyncio
async def test_completed_onboarding_returns_none(mock_client_repo, mock_ai_provider, mock_scraper, mock_playbook_loader):
    service = OnboardingService(mock_client_repo, mock_ai_provider, mock_scraper, mock_playbook_loader)

    # Create a fully onboarded client
    from app.core.marketing_stack.models.client import Client
    client = Client(
        id=uuid4(),
        phone_number="+919999999999",
        onboarding_status=OnboardingStatus.COMPLETE,
        business_profile={"sector": "restaurant"},
    )
    await mock_client_repo.create(client)

    response = await service.handle_message("+919999999999", "Hello")
    assert response is None


@pytest.mark.asyncio
async def test_full_question_flow_completes_onboarding(mock_client_repo, mock_ai_provider, mock_scraper, mock_playbook_loader):
    mock_ai_provider._response = json.dumps({
        "sector": "salon",
        "business_name": "Glow Salon",
        "city": "Mumbai",
        "language": "hindi",
    })
    service = OnboardingService(mock_client_repo, mock_ai_provider, mock_scraper, mock_playbook_loader)

    answers = [
        "Hi",                                          # triggers welcome + Q1
        "Glow Salon, Bandra, Mumbai",                  # Q1
        "Hair styling, facial, bridal makeup",         # Q2
        "Women aged 20-45",                            # Q3
        "Rs 500-3000",                                 # Q4
        "We use only organic products",                # Q5
        "sending photos",                              # Q6
    ]

    for answer in answers:
        response = await service.handle_message("+919876543210", answer)

    client = await mock_client_repo.get_by_phone("+919876543210")
    assert client.onboarding_status == OnboardingStatus.COMPLETE
    assert client.sector == "salon"
    assert len(mock_ai_provider.calls) > 0
