import time
from typing import Dict, Any, Optional
from loguru import logger

from app.core.marketing_stack.outbound.external.ai_provider_port import AIProviderPort


class ModelRouterAdapter(AIProviderPort):
    """Routes AI calls to the appropriate model per intelligence layer.

    Layer 1-2 (reasoning-heavy): Claude Sonnet
    Layer 3-5 (volume, speed):   Gemini Flash

    Falls back to the other provider if the primary fails.
    """

    def __init__(
        self,
        claude_provider: AIProviderPort,
        gemini_provider: AIProviderPort,
    ):
        self._claude = claude_provider
        self._gemini = gemini_provider

        self._layer_routing = {
            "layer1": self._claude,   # Business understanding — needs strong reasoning
            "layer2": self._claude,   # Strategy generation — needs strong reasoning
            "layer3": self._gemini,   # Content generation — volume, speed
            "layer4": self._gemini,   # Execution planning — structured output
            "layer5": self._gemini,   # Optimization — number crunching
        }

    def get_provider_for_layer(self, layer: str) -> AIProviderPort:
        return self._layer_routing.get(layer, self._gemini)

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 4096,
    ) -> str:
        layer = self._detect_layer(system_prompt)
        primary = self.get_provider_for_layer(layer)
        fallback = self._gemini if primary == self._claude else self._claude

        try:
            return await primary.generate(system_prompt, user_prompt, max_tokens)
        except Exception as e:
            logger.warning(
                f"Primary provider failed for {layer}: {type(e).__name__}: {e}. "
                f"Falling back to secondary provider."
            )
            try:
                return await fallback.generate(system_prompt, user_prompt, max_tokens)
            except Exception as e2:
                logger.error(f"Both providers failed for {layer}: {type(e2).__name__}: {e2}")
                raise

    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_schema: Optional[Dict[str, Any]] = None,
        max_tokens: int = 4096,
    ) -> Dict[str, Any]:
        layer = self._detect_layer(system_prompt)
        primary = self.get_provider_for_layer(layer)
        fallback = self._gemini if primary == self._claude else self._claude

        try:
            return await primary.generate_structured(system_prompt, user_prompt, response_schema, max_tokens)
        except Exception as e:
            logger.warning(f"Primary structured generation failed for {layer}: {e}. Falling back.")
            try:
                return await fallback.generate_structured(system_prompt, user_prompt, response_schema, max_tokens)
            except Exception as e2:
                logger.error(f"Both providers failed structured generation for {layer}: {e2}")
                raise

    def _detect_layer(self, system_prompt: str) -> str:
        prompt_lower = system_prompt.lower()
        if "business analyst" in prompt_lower or "business profile" in prompt_lower:
            return "layer1"
        if "marketing strategist" in prompt_lower or "marketing strategy" in prompt_lower:
            return "layer2"
        if "content creator" in prompt_lower or "generate marketing content" in prompt_lower:
            return "layer3"
        if "execution" in prompt_lower or "campaign plan" in prompt_lower:
            return "layer4"
        if "performance analyst" in prompt_lower or "optimization" in prompt_lower:
            return "layer5"
        return "layer3"  # Default to cheaper model
