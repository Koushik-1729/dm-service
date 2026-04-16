import json
import time
from typing import Dict, Any, Optional
from loguru import logger
import httpx

from app.core.marketing_stack.outbound.external.ai_provider_port import AIProviderPort
from app.monitoring.metrics import AI_CALL_COUNT, AI_CALL_LATENCY


class OpenRouterAdapter(AIProviderPort):
    """OpenRouter API adapter — access free and paid models via unified API.

    Free models available:
    - google/gemma-3-4b-it:free
    - deepseek-ai/deepseek-v3:free (very capable)
    - qwen/qwen3.5-122b-a10b:free
    - mistralai/mistral-small-4-119b-2603:free
    """

    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self, api_key: str, default_model: str = "deepseek/deepseek-chat-v3-0324:free"):
        self._api_key = api_key
        self._default_model = default_model
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://marketingos.in",
            "X-Title": "Marketing Service",
        }

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 4096,
    ) -> str:
        start = time.time()

        payload = {
            "model": self._default_model,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.BASE_URL,
                    json=payload,
                    headers=self._headers,
                )

                if response.status_code != 200:
                    logger.error(f"OpenRouter error: {response.status_code} {response.text[:500]}")
                    response.raise_for_status()

                data = response.json()
                result = data["choices"][0]["message"]["content"]
                duration = time.time() - start

                usage = data.get("usage", {})
                AI_CALL_COUNT.labels(provider="openrouter", model=self._default_model, layer="generate").inc()
                AI_CALL_LATENCY.labels(provider="openrouter", layer="generate").observe(duration)

                logger.debug(
                    f"OpenRouter generate: model={self._default_model} "
                    f"input_tokens={usage.get('prompt_tokens', 0)} "
                    f"output_tokens={usage.get('completion_tokens', 0)} "
                    f"duration={duration:.2f}s"
                )

                return result

        except httpx.TimeoutException:
            logger.error(f"OpenRouter timeout for model {self._default_model}")
            raise
        except Exception as e:
            logger.error(f"OpenRouter error: {type(e).__name__}: {e}")
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
            logger.error(f"OpenRouter returned invalid JSON: {e}\nRaw: {raw[:500]}")
            return {}

    def _extract_json(self, text: str) -> str:
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        return text.strip()

    def get_usage_info(self) -> Dict[str, str]:
        return {"provider": "openrouter", "model": self._default_model}
