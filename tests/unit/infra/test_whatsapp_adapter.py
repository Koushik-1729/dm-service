import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from app.infra.marketing_stack.external.whatsapp_adapter import WhatsAppAdapter


@pytest.fixture
def wa_adapter():
    return WhatsAppAdapter(phone_number_id="123456", access_token="test-token")


@pytest.mark.asyncio
async def test_send_text_returns_message_id(wa_adapter):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"messages": [{"id": "wamid.test123"}]}

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response):
        msg_id = await wa_adapter.send_text("+919876543210", "Hello!")

    assert msg_id == "wamid.test123"


@pytest.mark.asyncio
async def test_send_interactive_limits_buttons(wa_adapter):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"messages": [{"id": "wamid.btn123"}]}

    buttons = [
        {"id": "btn1", "title": "Option 1"},
        {"id": "btn2", "title": "Option 2"},
        {"id": "btn3", "title": "Option 3"},
        {"id": "btn4", "title": "Option 4 (should be ignored)"},
    ]

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response) as mock_post:
        await wa_adapter.send_interactive("+919876543210", "Choose:", buttons)

        call_args = mock_post.call_args
        payload = call_args.kwargs.get("json", {})
        sent_buttons = payload.get("interactive", {}).get("action", {}).get("buttons", [])
        assert len(sent_buttons) <= 3  # WhatsApp max


@pytest.mark.asyncio
async def test_send_template_sends_correct_format(wa_adapter):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"messages": [{"id": "wamid.tpl123"}]}

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response) as mock_post:
        msg_id = await wa_adapter.send_template(
            to="+919876543210",
            template_name="weekly_offer",
            language_code="en",
            parameters=[{"type": "text", "text": "10% off this week!"}],
        )

    assert msg_id == "wamid.tpl123"
    payload = mock_post.call_args.kwargs["json"]
    assert payload["type"] == "template"
    assert payload["template"]["name"] == "weekly_offer"
