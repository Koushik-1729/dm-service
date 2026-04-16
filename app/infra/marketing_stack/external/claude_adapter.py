import json
import time
from typing import Dict, Any, Optional
from loguru import logger
import anthropic

from app.core.marketing_stack.outbound.external.ai_provider_port import AIProviderPort
from app.monitoring.metrics import AI_CALL_COUNT, AI_CALL_LATENCY


class ClaudeAdapter(AIProviderPort):
    """Anthropic Claude API adapter implementing AIProviderPort."""

    def __init__(self, api_key: str, default_model: str = "claude-sonnet-4-20250514"):
        self._client = anthropic.AsyncAnthropic(api_key=api_key)
        self._default_model = default_model

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 4096,
    ) -> str:
        start = time.time()
        try:
            response = await self._client.messages.create(
                model=self._default_model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )

            result = response.content[0].text
            duration = time.time() - start

            AI_CALL_COUNT.labels(provider="claude", model=self._default_model, layer="generate").inc()
            AI_CALL_LATENCY.labels(provider="claude", layer="generate").observe(duration)

            logger.debug(
                f"Claude generate: model={self._default_model} "
                f"input_tokens={response.usage.input_tokens} "
                f"output_tokens={response.usage.output_tokens} "
                f"duration={duration:.2f}s"
            )

            return result

        except anthropic.APIConnectionError as e:
            logger.error(f"Claude connection error: {e}")
            raise
        except anthropic.RateLimitError as e:
            logger.warning(f"Claude rate limit hit: {e}")
            raise
        except anthropic.APIStatusError as e:
            logger.error(f"Claude API error: status={e.status_code} message={e.message}")
            raise

    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_schema: Optional[Dict[str, Any]] = None,
        max_tokens: int = 4096,
    ) -> Dict[str, Any]:
        enhanced_system = system_prompt + "\n\nReturn ONLY valid JSON. No markdown, no explanation."

        raw = await self.generate(
            system_prompt=enhanced_system,
            user_prompt=user_prompt,
            max_tokens=max_tokens,
        )

        cleaned = self._extract_json(raw)

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"Claude returned invalid JSON: {e}\nRaw: {raw[:500]}")
            return {}

    def _extract_json(self, text: str) -> str:
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        return text.strip()

    def get_usage_info(self) -> Dict[str, str]:
        return {"provider": "anthropic", "model": self._default_model}
