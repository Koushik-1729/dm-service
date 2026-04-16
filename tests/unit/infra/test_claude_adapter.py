import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.infra.marketing_stack.external.claude_adapter import ClaudeAdapter


@pytest.mark.asyncio
async def test_generate_returns_text():
    adapter = ClaudeAdapter(api_key="test-key", default_model="claude-sonnet-4-20250514")

    mock_response = MagicMock()
    mock_response.content = [MagicMock(text='{"sector": "restaurant"}')]
    mock_response.usage = MagicMock(input_tokens=100, output_tokens=50)

    with patch.object(adapter._client.messages, 'create', new_callable=AsyncMock, return_value=mock_response):
        result = await adapter.generate(
            system_prompt="Test system",
            user_prompt="Test user",
        )

    assert "restaurant" in result


@pytest.mark.asyncio
async def test_generate_structured_returns_dict():
    adapter = ClaudeAdapter(api_key="test-key")

    mock_response = MagicMock()
    mock_response.content = [MagicMock(text='{"sector": "salon", "city": "Mumbai"}')]
    mock_response.usage = MagicMock(input_tokens=100, output_tokens=50)

    with patch.object(adapter._client.messages, 'create', new_callable=AsyncMock, return_value=mock_response):
        result = await adapter.generate_structured(
            system_prompt="Return JSON",
            user_prompt="Analyze this business",
        )

    assert result["sector"] == "salon"
    assert result["city"] == "Mumbai"


@pytest.mark.asyncio
async def test_generate_structured_handles_invalid_json():
    adapter = ClaudeAdapter(api_key="test-key")

    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="This is not JSON at all")]
    mock_response.usage = MagicMock(input_tokens=100, output_tokens=50)

    with patch.object(adapter._client.messages, 'create', new_callable=AsyncMock, return_value=mock_response):
        result = await adapter.generate_structured(
            system_prompt="Return JSON",
            user_prompt="Test",
        )

    assert result == {}


def test_extract_json_from_markdown():
    adapter = ClaudeAdapter(api_key="test-key")

    text_with_markdown = 'Here is the result:\n```json\n{"key": "value"}\n```\nDone.'
    result = adapter._extract_json(text_with_markdown)

    assert result == '{"key": "value"}'
