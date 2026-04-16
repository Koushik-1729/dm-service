import json
import re
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from loguru import logger

from app.core.marketing_stack.models.client import Client
from app.core.marketing_stack.outbound.repositories.client_repository import ClientRepository
from app.core.marketing_stack.outbound.external.ai_provider_port import AIProviderPort
from app.core.marketing_stack.outbound.external.web_scraper_port import WebScraperPort
from app.core.marketing_stack.outbound.external.playbook_loader_port import PlaybookLoaderPort
from app.core.marketing_stack.constants.onboarding_constants import (
    ONBOARDING_QUESTIONS,
    ONBOARDING_WELCOME,
    ONBOARDING_COMPLETE,
    TOTAL_QUESTIONS,
)
from app.core.marketing_stack.constants.status_constants import OnboardingStatus


LAYER1_SYSTEM_PROMPT = """You are an expert business analyst. Given information about a business
(from answers to questions and/or scraped website data), create a comprehensive business profile.

Return ONLY valid JSON with these fields:
{
  "business_name": "string",
  "sector": "restaurant|clinic|salon|gym|coaching|retail|real_estate|ecommerce|local_service|general",
  "sub_sector": "string (e.g. 'north_indian', 'dental', 'unisex_salon')",
  "city": "string",
  "locality": "string",
  "language": "english|hindi|telugu|tamil|marathi|bengali|kannada|hinglish",
  "target_audience": {
    "demographics": "string",
    "psychographics": "string",
    "age_range": "string"
  },
  "unique_selling_points": ["string"],
  "competitors_likely": ["string"],
  "price_positioning": "budget|mid_range|premium",
  "services_offered": ["string"],
  "business_hours": "string or null",
  "summary": "2-3 sentence business summary"
}"""


class OnboardingService:
    """Layer 1: Understands the business through questions and/or website scraping."""

    def __init__(
        self,
        client_repository: ClientRepository,
        ai_provider: AIProviderPort,
        web_scraper: WebScraperPort,
        playbook_loader: PlaybookLoaderPort,
    ):
        self._client_repo = client_repository
        self._ai = ai_provider
        self._scraper = web_scraper
        self._playbook_loader = playbook_loader

    async def get_or_create_client(self, phone_number: str) -> Client:
        client = await self._client_repo.get_by_phone(phone_number)
        if not client:
            client = Client(
                id=uuid4(),
                phone_number=phone_number,
                onboarding_status=OnboardingStatus.PENDING_QUESTIONS,
                current_question_index=0,
            )
            client = await self._client_repo.create(client)
            logger.info(f"New client created: {phone_number}")
        return client

    async def handle_message(self, phone_number: str, message: str) -> str:
        client = await self.get_or_create_client(phone_number)

        if client.is_onboarding_complete():
            return None  # Not an onboarding message — let orchestrator handle

        # Check if message is a URL
        if self._is_url(message):
            return await self._handle_url(client, message)

        # First message — send welcome + Q1
        if client.current_question_index == 0 and not client.onboarding_answers:
            # Mark that welcome was sent by storing a flag
            client.onboarding_answers["_welcome_sent"] = "true"
            await self._client_repo.update(client)
            welcome = ONBOARDING_WELCOME.format(total=TOTAL_QUESTIONS)
            first_q = ONBOARDING_QUESTIONS[0]
            return f"{welcome}\n\n*Question 1/{TOTAL_QUESTIONS}:*\n{first_q['question']}\n\n_{first_q['example']}_"

        # Record answer and ask next question
        client.record_answer(message)
        await self._client_repo.update(client)

        if client.has_answered_all_questions():
            return await self._complete_onboarding(client)

        # Ask next question
        next_q = client.get_current_question()
        idx = client.current_question_index + 1
        return f"*Question {idx}/{TOTAL_QUESTIONS}:*\n{next_q['question']}\n\n_{next_q['example']}_"

    async def _handle_url(self, client: Client, url: str) -> str:
        logger.info(f"Scraping URL for client {client.phone_number}: {url}")

        try:
            if "google.com/maps" in url or "goo.gl/maps" in url:
                scraped = await self._scraper.scrape_google_maps(url)
                client.google_maps_url = url
            else:
                scraped = await self._scraper.scrape_url(url)
                client.website_url = url

            client.scraped_data = scraped
            await self._client_repo.update(client)

            return await self._complete_onboarding(client)
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            first_q = ONBOARDING_QUESTIONS[0]
            return (
                "I couldn't read that link. No worries — let me ask you a few questions instead.\n\n"
                f"*Question 1/{TOTAL_QUESTIONS}:*\n{first_q['question']}\n\n_{first_q['example']}_"
            )

    async def _complete_onboarding(self, client: Client) -> str:
        logger.info(f"Completing onboarding for {client.phone_number}")

        user_prompt = self._build_profile_prompt(client)
        profile_json = await self._ai.generate(
            system_prompt=LAYER1_SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        from app.core.marketing_stack.utils.json_utils import safe_parse_json
        profile = safe_parse_json(profile_json, fallback={"sector": "general", "business_name": client.business_name or "Business"})

        client.complete_onboarding(profile)
        await self._client_repo.update(client)

        return ONBOARDING_COMPLETE

    def _build_profile_prompt(self, client: Client) -> str:
        parts = []

        if client.onboarding_answers:
            parts.append("ANSWERS FROM BUSINESS OWNER:")
            for q in ONBOARDING_QUESTIONS:
                answer = client.onboarding_answers.get(q["id"], "Not provided")
                parts.append(f"Q: {q['question']}\nA: {answer}")

        if client.scraped_data:
            parts.append("\nSCRAPED WEBSITE/GMB DATA:")
            parts.append(json.dumps(client.scraped_data, indent=2, default=str))

        return "\n\n".join(parts)

    def _is_url(self, text: str) -> bool:
        url_pattern = r'https?://[^\s]+'
        return bool(re.match(url_pattern, text.strip()))

    def _extract_json(self, text: str) -> str:
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        return text.strip()
