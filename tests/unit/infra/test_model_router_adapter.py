import pytest
from unittest.mock import AsyncMock

from app.infra.marketing_stack.external.model_router_adapter import ModelRouterAdapter
from tests.conftest import MockAIProvider


@pytest.mark.asyncio
async def test_routes_layer1_to_claude():
    claude = MockAIProvider(response='{"sector": "restaurant"}')
    gemini = MockAIProvider(response='{"sector": "general"}')

    router = ModelRouterAdapter(claude_provider=claude, gemini_provider=gemini)

    # Layer 1 prompt contains "business analyst"
    result = await router.generate(
        system_prompt="You are an expert business analyst. Analyze this business.",
        user_prompt="Test business data",
    )

    assert len(claude.calls) == 1
    assert len(gemini.calls) == 0


@pytest.mark.asyncio
async def test_routes_layer3_to_gemini():
    claude = MockAIProvider(response="claude response")
    gemini = MockAIProvider(response="gemini response")

    router = ModelRouterAdapter(claude_provider=claude, gemini_provider=gemini)

    # Layer 3 prompt contains "content creator"
    result = await router.generate(
        system_prompt="You are an expert social media content creator.",
        user_prompt="Generate instagram post",
    )

    assert len(gemini.calls) == 1
    assert len(claude.calls) == 0


@pytest.mark.asyncio
async def test_falls_back_on_primary_failure():
    claude = MockAIProvider(response="claude response")
    gemini = MockAIProvider(response="gemini fallback")

    # Make claude raise an exception
    async def failing_generate(*args, **kwargs):
        raise Exception("Claude API down")

    claude.generate = failing_generate

    router = ModelRouterAdapter(claude_provider=claude, gemini_provider=gemini)

    result = await router.generate(
        system_prompt="You are an expert business analyst.",
        user_prompt="Test",
    )

    assert result == "gemini fallback"
    assert len(gemini.calls) == 1


@pytest.mark.asyncio
async def test_defaults_to_gemini_for_unknown_prompts():
    claude = MockAIProvider(response="claude")
    gemini = MockAIProvider(response="gemini")

    router = ModelRouterAdapter(claude_provider=claude, gemini_provider=gemini)

    result = await router.generate(
        system_prompt="Do something random.",
        user_prompt="Test",
    )

    assert len(gemini.calls) == 1
    assert len(claude.calls) == 0


def test_detect_layer():
    router = ModelRouterAdapter(
        claude_provider=MockAIProvider(),
        gemini_provider=MockAIProvider(),
    )

    assert router._detect_layer("You are an expert business analyst") == "layer1"
    assert router._detect_layer("You are a marketing strategist") == "layer2"
    assert router._detect_layer("You are a content creator") == "layer3"
    assert router._detect_layer("You are a performance analyst") == "layer5"
    assert router._detect_layer("Random prompt") == "layer3"  # default to cheap
