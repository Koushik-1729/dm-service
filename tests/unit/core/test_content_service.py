import pytest
import json
from uuid import uuid4

from app.core.marketing_stack.services.content_service import ContentService


@pytest.mark.asyncio
async def test_generate_weekly_content_creates_variants(mock_content_repo, mock_ai_provider, sample_client, sample_strategy):
    mock_ai_provider._response = json.dumps([
        {"channel": "instagram", "content_type": "post", "caption": "Variant A caption", "hashtags": ["coffee"], "cta_text": "Visit us", "variant_label": "A"},
        {"channel": "instagram", "content_type": "post", "caption": "Variant B caption", "hashtags": ["coffee"], "cta_text": "Come today", "variant_label": "B"},
        {"channel": "instagram", "content_type": "post", "caption": "Variant C caption", "hashtags": ["coffee"], "cta_text": "Try now", "variant_label": "C"},
    ])

    service = ContentService(mock_content_repo, mock_ai_provider)
    contents = await service.generate_weekly_content(sample_client, sample_strategy)

    assert len(contents) > 0
    labels = [c.variant_label for c in contents]
    assert "A" in labels
    assert "B" in labels


@pytest.mark.asyncio
async def test_risk_assessment_flags_high_risk_sectors(mock_content_repo, mock_ai_provider):
    service = ContentService(mock_content_repo, mock_ai_provider)

    risk = service._assess_risk("Great dental care for your family", "clinic")
    assert risk == "high"


@pytest.mark.asyncio
async def test_risk_assessment_blocks_guaranteed_claims(mock_content_repo, mock_ai_provider):
    service = ContentService(mock_content_repo, mock_ai_provider)

    risk = service._assess_risk("Guaranteed results in 7 days!", "restaurant")
    assert risk == "blocked"


@pytest.mark.asyncio
async def test_risk_assessment_low_for_normal_content(mock_content_repo, mock_ai_provider):
    service = ContentService(mock_content_repo, mock_ai_provider)

    risk = service._assess_risk("Come try our new cold brew today!", "restaurant")
    assert risk == "low"
