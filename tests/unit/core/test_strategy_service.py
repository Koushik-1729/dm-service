import pytest
import json
from uuid import uuid4

from app.core.marketing_stack.services.strategy_service import StrategyService


@pytest.mark.asyncio
async def test_generate_strategy_creates_active_strategy(mock_strategy_repo, mock_ai_provider, mock_playbook_loader, sample_client):
    mock_ai_provider._response = json.dumps({
        "channels": [
            {"name": "instagram", "priority": 1, "active": True, "posts_per_week": 4},
            {"name": "whatsapp", "priority": 2, "active": True, "messages_per_week": 2},
        ],
        "content_calendar": [
            {"day": "monday", "channel": "instagram", "content_type": "post", "topic": "Coffee spotlight"},
        ],
        "kpis": {"weekly_posts": 4, "monthly_leads_target": 15},
        "budget_allocation": {"total_monthly": 5000},
        "reasoning": "Instagram + WhatsApp are the best channels for a cafe.",
    })

    service = StrategyService(mock_strategy_repo, mock_ai_provider, mock_playbook_loader)

    strategy = await service.generate_strategy(sample_client)

    assert strategy.status == "active"
    assert strategy.client_id == sample_client.id
    assert len(strategy.channels) == 2
    assert strategy.version == 1
    assert len(mock_ai_provider.calls) == 1


@pytest.mark.asyncio
async def test_regenerate_archives_old_strategy(mock_strategy_repo, mock_ai_provider, mock_playbook_loader, sample_client, sample_strategy):
    # Pre-insert existing strategy
    await mock_strategy_repo.create(sample_strategy)

    mock_ai_provider._response = json.dumps({
        "channels": [{"name": "instagram", "priority": 1, "active": True}],
        "content_calendar": [],
        "kpis": {},
        "reasoning": "Updated strategy",
    })

    service = StrategyService(mock_strategy_repo, mock_ai_provider, mock_playbook_loader)
    new_strategy = await service.generate_strategy(sample_client)

    assert new_strategy.version == 2
    old = await mock_strategy_repo.get_by_id(sample_strategy.id)
    assert old.status == "archived"


@pytest.mark.asyncio
async def test_uses_default_strategy_on_ai_failure(mock_strategy_repo, mock_ai_provider, mock_playbook_loader, sample_client):
    mock_ai_provider._response = "not valid json {{{{"

    service = StrategyService(mock_strategy_repo, mock_ai_provider, mock_playbook_loader)
    strategy = await service.generate_strategy(sample_client)

    assert strategy.status == "active"
    assert len(strategy.channels) > 0  # Falls back to defaults
