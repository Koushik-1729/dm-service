import json
from typing import Optional
from uuid import UUID, uuid4
from loguru import logger

from app.core.marketing_stack.models.client import Client
from app.core.marketing_stack.models.strategy import Strategy
from app.core.marketing_stack.outbound.repositories.strategy_repository import StrategyRepository
from app.core.marketing_stack.outbound.external.ai_provider_port import AIProviderPort
from app.core.marketing_stack.outbound.external.playbook_loader_port import PlaybookLoaderPort


LAYER2_SYSTEM_PROMPT = """You are an expert digital marketing strategist for small businesses in India.

Given a business profile and sector playbook, create a complete 30-day marketing strategy.

Return ONLY valid JSON:
{
  "channels": [
    {"name": "instagram", "priority": 1, "active": true, "budget_pct": 40, "posts_per_week": 4},
    {"name": "whatsapp", "priority": 2, "active": true, "budget_pct": 10, "messages_per_week": 2}
  ],
  "content_calendar": [
    {"day": "monday", "channel": "instagram", "content_type": "post", "topic": "string"},
    {"day": "wednesday", "channel": "instagram", "content_type": "reel_script", "topic": "string"},
    {"day": "friday", "channel": "whatsapp", "content_type": "campaign_message", "topic": "string"}
  ],
  "kpis": {
    "weekly_posts": 4,
    "weekly_whatsapp_messages": 2,
    "monthly_leads_target": 20,
    "monthly_reach_target": 5000
  },
  "budget_allocation": {
    "total_monthly": 0,
    "instagram_ads": 0,
    "google_ads": 0,
    "whatsapp_messaging": 0
  },
  "campaign_ideas": [
    {"name": "string", "description": "string", "channel": "string", "duration_days": 7}
  ],
  "reasoning": "2-3 sentences explaining why this strategy"
}"""


class StrategyService:
    """Layer 2: Creates marketing strategy based on business profile and sector playbook."""

    def __init__(
        self,
        strategy_repository: StrategyRepository,
        ai_provider: AIProviderPort,
        playbook_loader: PlaybookLoaderPort,
    ):
        self._strategy_repo = strategy_repository
        self._ai = ai_provider
        self._playbook_loader = playbook_loader

    async def generate_strategy(self, client: Client) -> Strategy:
        logger.info(f"Generating strategy for client {client.id}, sector={client.sector}")

        playbook = self._playbook_loader.load(client.sector or "general")

        user_prompt = self._build_strategy_prompt(client, playbook)
        strategy_json = await self._ai.generate(
            system_prompt=LAYER2_SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        from app.core.marketing_stack.utils.json_utils import safe_parse_json
        parsed = safe_parse_json(strategy_json, fallback=None)
        if not parsed:
            logger.warning(f"Using default strategy for {client.id}")
            parsed = self._default_strategy(client.sector)

        # Archive existing active strategy
        existing = await self._strategy_repo.get_active_by_client(client.id)
        if existing:
            existing.archive()
            await self._strategy_repo.update(existing)

        strategy = Strategy(
            id=uuid4(),
            client_id=client.id,
            version=(existing.version + 1) if existing else 1,
            channels=parsed.get("channels", []),
            content_calendar=parsed.get("content_calendar", []),
            kpis=parsed.get("kpis", {}),
            budget_allocation=parsed.get("budget_allocation", {}),
            festival_campaigns=parsed.get("festival_campaigns", []),
            playbook_id=client.sector or "general",
            ai_reasoning=parsed.get("reasoning", ""),
            status="active",
        )

        return await self._strategy_repo.create(strategy)

    def _build_strategy_prompt(self, client: Client, playbook: dict) -> str:
        return (
            f"BUSINESS PROFILE:\n{json.dumps(client.business_profile, indent=2, default=str)}\n\n"
            f"SECTOR PLAYBOOK:\n{json.dumps(playbook, indent=2, default=str)}\n\n"
            f"LANGUAGE PREFERENCE: {client.language}\n"
            f"CITY: {client.city or 'Unknown'}\n"
            f"LOCALITY: {client.locality or 'Unknown'}\n\n"
            f"Create a 30-day marketing strategy for this business. "
            f"For MVP, focus on Instagram (organic posts) and WhatsApp campaigns only."
        )

    def _default_strategy(self, sector: Optional[str]) -> dict:
        return {
            "channels": [
                {"name": "instagram", "priority": 1, "active": True, "budget_pct": 60, "posts_per_week": 4},
                {"name": "whatsapp", "priority": 2, "active": True, "budget_pct": 40, "messages_per_week": 2},
            ],
            "content_calendar": [
                {"day": "monday", "channel": "instagram", "content_type": "post", "topic": "Product/service highlight"},
                {"day": "wednesday", "channel": "instagram", "content_type": "reel_script", "topic": "Behind the scenes"},
                {"day": "friday", "channel": "instagram", "content_type": "post", "topic": "Weekend offer"},
                {"day": "saturday", "channel": "whatsapp", "content_type": "campaign_message", "topic": "Weekly deals"},
            ],
            "kpis": {"weekly_posts": 4, "weekly_whatsapp_messages": 2, "monthly_leads_target": 15},
            "budget_allocation": {"total_monthly": 0},
            "reasoning": "Default strategy applied. Will optimize based on performance data.",
        }

    def _extract_json(self, text: str) -> str:
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        return text.strip()
