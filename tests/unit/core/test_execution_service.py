import pytest
from uuid import uuid4

from app.core.marketing_stack.services.execution_service import ExecutionService
from app.core.marketing_stack.models.content import Content
from app.core.marketing_stack.constants.status_constants import AutonomyLevel, RiskLevel


@pytest.mark.asyncio
async def test_publish_to_instagram(mock_content_repo, mock_campaign_repo, mock_messaging, mock_social_media):
    service = ExecutionService(mock_content_repo, mock_campaign_repo, mock_messaging, mock_social_media)

    content = Content(
        id=uuid4(),
        client_id=uuid4(),
        channel="instagram",
        content_type="post",
        caption="Test post",
        media_url="https://example.com/image.jpg",
        hashtags=["coffee", "hyderabad"],
        status="approved",
    )
    await mock_content_repo.create(content)

    campaign = await service.publish_to_instagram(content)

    assert campaign.channel == "instagram"
    assert campaign.status == "completed"
    assert len(mock_social_media.published) == 1


@pytest.mark.asyncio
async def test_should_auto_execute_supervised(mock_content_repo, mock_campaign_repo, mock_messaging, mock_social_media, sample_client):
    service = ExecutionService(mock_content_repo, mock_campaign_repo, mock_messaging, mock_social_media)

    sample_client.autonomy_level = AutonomyLevel.SUPERVISED
    content = Content(id=uuid4(), risk_level=RiskLevel.LOW)

    assert service.should_auto_execute(content, sample_client) is False


@pytest.mark.asyncio
async def test_should_auto_execute_assisted_low_risk(mock_content_repo, mock_campaign_repo, mock_messaging, mock_social_media, sample_client):
    service = ExecutionService(mock_content_repo, mock_campaign_repo, mock_messaging, mock_social_media)

    sample_client.autonomy_level = AutonomyLevel.ASSISTED
    content = Content(id=uuid4(), risk_level=RiskLevel.LOW)

    assert service.should_auto_execute(content, sample_client) is True


@pytest.mark.asyncio
async def test_should_auto_execute_assisted_high_risk(mock_content_repo, mock_campaign_repo, mock_messaging, mock_social_media, sample_client):
    service = ExecutionService(mock_content_repo, mock_campaign_repo, mock_messaging, mock_social_media)

    sample_client.autonomy_level = AutonomyLevel.ASSISTED
    content = Content(id=uuid4(), risk_level=RiskLevel.HIGH)

    assert service.should_auto_execute(content, sample_client) is False
