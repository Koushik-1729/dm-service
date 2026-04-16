import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.config.app_config import app_config


@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)


def test_webhook_verification_success(client):
    response = client.get(
        "/marketing-service/api/v1/webhook/whatsapp",
        params={
            "hub.mode": "subscribe",
            "hub.challenge": "test_challenge_123",
            "hub.verify_token": app_config.whatsapp_verify_token,
        },
    )

    assert response.status_code == 200
    assert response.text == "test_challenge_123"


def test_webhook_verification_failure(client):
    response = client.get(
        "/marketing-service/api/v1/webhook/whatsapp",
        params={
            "hub.mode": "subscribe",
            "hub.challenge": "test_challenge",
            "hub.verify_token": "wrong_token",
        },
    )

    assert response.status_code == 403


def test_webhook_post_returns_ok(client):
    payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "123",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {"phone_number_id": "123"},
                    "messages": [],
                    "statuses": [],
                },
                "field": "messages",
            }],
        }],
    }

    response = client.post(
        "/marketing-service/api/v1/webhook/whatsapp",
        json=payload,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health_endpoint(client):
    response = client.get("/marketing-service/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_health_live_endpoint(client):
    response = client.get("/marketing-service/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "live"
