import json
import time
from typing import Dict, Any, Optional
from loguru import logger
from google import genai
from google.genai import types

from app.core.marketing_stack.outbound.external.ai_provider_port import AIProviderPort
from app.monitoring.metrics import AI_CALL_COUNT, AI_CALL_LATENCY


class GeminiAdapter(AIProviderPort):
    """Google Gemini API adapter implementing AIProviderPort."""

    def __init__(self, api_key: str, default_model: str = "gemini-2.5-flash"):
        self._client = genai.Client(api_key=api_key)
        self._default_model = default_model

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 4096,
    ) -> str:
        start = time.time()
        try:
            response = await self._client.aio.models.generate_content(
                model=self._default_model,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    max_output_tokens=max_tokens,
                    temperature=0.7,
                ),
            )

            result = response.text
            duration = time.time() - start

            AI_CALL_COUNT.labels(provider="gemini", model=self._default_model, layer="generate").inc()
            AI_CALL_LATENCY.labels(provider="gemini", layer="generate").observe(duration)

            input_tokens = getattr(response.usage_metadata, "prompt_token_count", 0) if response.usage_metadata else 0
            output_tokens = getattr(response.usage_metadata, "candidates_token_count", 0) if response.usage_metadata else 0

            logger.debug(
                f"Gemini generate: model={self._default_model} "
                f"input_tokens={input_tokens} "
                f"output_tokens={output_tokens} "
                f"duration={duration:.2f}s"
            )

            return result

        except Exception as e:
            logger.error(f"Gemini API error: {type(e).__name__}: {e}")
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
            logger.error(f"Gemini returned invalid JSON: {e}\nRaw: {raw[:500]}")
            return {}

    def _extract_json(self, text: str) -> str:
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        return text.strip()

    def get_usage_info(self) -> Dict[str, str]:
        return {"provider": "google", "model": self._default_model}
