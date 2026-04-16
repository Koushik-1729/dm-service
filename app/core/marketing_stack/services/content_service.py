import json
from typing import List
from uuid import UUID, uuid4
from loguru import logger

from app.core.marketing_stack.models.client import Client
from app.core.marketing_stack.models.strategy import Strategy
from app.core.marketing_stack.models.content import Content
from app.core.marketing_stack.outbound.repositories.content_repository import ContentRepository
from app.core.marketing_stack.outbound.external.ai_provider_port import AIProviderPort
from app.core.marketing_stack.constants.channel_constants import Channel, ContentType
from app.core.marketing_stack.constants.status_constants import RiskLevel


LAYER3_SYSTEM_PROMPT = """You are an expert social media content creator for small businesses in India.

Given a business profile, strategy, and content brief, generate marketing content.

Return ONLY valid JSON array:
[
  {
    "channel": "instagram",
    "content_type": "post",
    "caption": "The full post caption with emojis and line breaks",
    "hashtags": ["hashtag1", "hashtag2", "hashtag3"],
    "cta_text": "Call to action text",
    "variant_label": "A"
  },
  {
    "channel": "instagram",
    "content_type": "post",
    "caption": "Alternative version of the same post",
    "hashtags": ["hashtag1", "hashtag2", "hashtag3"],
    "cta_text": "Call to action text",
    "variant_label": "B"
  }
]

Rules:
- Generate 3 A/B variants (A, B, C) for each content piece
- Use the business's preferred language
- Include relevant local references (city, locality)
- Keep captions engaging, concise, and action-oriented
- Use appropriate emojis but don't overdo it
- For WhatsApp messages: keep under 500 characters
- For Instagram: include 10-15 relevant hashtags"""


class ContentService:
    """Layer 3: Generates marketing content with A/B variants."""

    def __init__(
        self,
        content_repository: ContentRepository,
        ai_provider: AIProviderPort,
    ):
        self._content_repo = content_repository
        self._ai = ai_provider

    async def generate_weekly_content(
        self,
        client: Client,
        strategy: Strategy,
    ) -> List[Content]:
        logger.info(f"Generating weekly content for client {client.id}")

        all_content = []

        for calendar_entry in strategy.content_calendar:
            channel = calendar_entry.get("channel", Channel.INSTAGRAM)
            content_type = calendar_entry.get("content_type", ContentType.POST)
            topic = calendar_entry.get("topic", "General business content")

            variants = await self._generate_variants(
                client=client,
                strategy=strategy,
                channel=channel,
                content_type=content_type,
                topic=topic,
            )
            all_content.extend(variants)

        if all_content:
            all_content = await self._content_repo.create_batch(all_content)

        logger.info(f"Generated {len(all_content)} content pieces for client {client.id}")
        return all_content

    async def _generate_variants(
        self,
        client: Client,
        strategy: Strategy,
        channel: str,
        content_type: str,
        topic: str,
    ) -> List[Content]:
        user_prompt = (
            f"BUSINESS PROFILE:\n{json.dumps(client.business_profile, indent=2, default=str)}\n\n"
            f"CONTENT BRIEF:\n"
            f"Channel: {channel}\n"
            f"Content type: {content_type}\n"
            f"Topic: {topic}\n"
            f"Language: {client.language}\n"
            f"City: {client.city or 'Unknown'}\n"
            f"Locality: {client.locality or 'Unknown'}\n\n"
            f"Generate 3 A/B/C variants of this content."
        )

        response = await self._ai.generate(
            system_prompt=LAYER3_SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        from app.core.marketing_stack.utils.json_utils import safe_parse_json
        variants_data = safe_parse_json(response, fallback=None)
        if not variants_data or not isinstance(variants_data, list):
            logger.warning(f"Using fallback content for {channel}/{content_type}")
            variants_data = [self._fallback_content(channel, content_type, topic, label) for label in ["A", "B", "C"]]

        variant_group = str(uuid4())[:8]
        contents = []

        for item in variants_data:
            risk = self._assess_risk(item.get("caption", ""), client.sector)
            content = Content(
                id=uuid4(),
                client_id=client.id,
                strategy_id=strategy.id,
                channel=item.get("channel", channel),
                content_type=item.get("content_type", content_type),
                variant_group=variant_group,
                variant_label=item.get("variant_label", "A"),
                caption=item.get("caption", ""),
                hashtags=item.get("hashtags", []),
                cta_text=item.get("cta_text", ""),
                language=client.language,
                risk_level=risk,
                status="draft",
            )
            contents.append(content)

        return contents

    def _assess_risk(self, caption: str, sector: str) -> str:
        high_risk_sectors = {"clinic", "hospital", "finance", "legal", "insurance"}
        if sector in high_risk_sectors:
            return RiskLevel.HIGH

        blocked_phrases = ["guaranteed results", "100% success", "no side effects", "get rich"]
        caption_lower = caption.lower()
        for phrase in blocked_phrases:
            if phrase in caption_lower:
                return RiskLevel.BLOCKED

        claim_words = ["best", "cheapest", "#1", "number one", "guaranteed"]
        for word in claim_words:
            if word in caption_lower:
                return RiskLevel.MEDIUM

        return RiskLevel.LOW

    def _fallback_content(self, channel: str, content_type: str, topic: str, label: str) -> dict:
        return {
            "channel": channel,
            "content_type": content_type,
            "caption": f"Check out what we have for you today! {topic}",
            "hashtags": ["smallbusiness", "local", "supportlocal"],
            "cta_text": "Visit us today!",
            "variant_label": label,
        }

    def _extract_json(self, text: str) -> str:
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        return text.strip()
