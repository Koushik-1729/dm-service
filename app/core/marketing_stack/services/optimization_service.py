import json
from datetime import date, timedelta
from typing import Optional, Dict, Any
from uuid import UUID
from loguru import logger

from app.core.marketing_stack.models.client import Client
from app.core.marketing_stack.outbound.repositories.metrics_repository import MetricsRepository
from app.core.marketing_stack.outbound.repositories.lead_repository import LeadRepository
from app.core.marketing_stack.outbound.external.ai_provider_port import AIProviderPort
from app.core.marketing_stack.outbound.external.messaging_port import MessagingPort


WEEKLY_REPORT_PROMPT = """You are a marketing performance analyst. Given the weekly metrics for a small business,
generate a clear, concise WhatsApp-friendly report.

Rules:
- Keep it under 800 characters
- Use simple language the business owner understands
- Show real numbers: leads, estimated revenue, spend, ROI
- Highlight best and worst performing channels
- End with what AI will do differently next week
- Use minimal emojis (2-3 max)
- DO NOT use markdown formatting — plain text only"""


class OptimizationService:
    """Layer 5: Daily optimization and weekly reporting."""

    def __init__(
        self,
        metrics_repository: MetricsRepository,
        lead_repository: LeadRepository,
        ai_provider: AIProviderPort,
        messaging_port: MessagingPort,
    ):
        self._metrics_repo = metrics_repository
        self._lead_repo = lead_repository
        self._ai = ai_provider
        self._messaging = messaging_port

    async def generate_weekly_report(self, client: Client) -> str:
        logger.info(f"Generating weekly report for client {client.id}")

        today = date.today()
        week_ago = today - timedelta(days=7)

        metrics_summary = await self._metrics_repo.get_summary(client.id, days=7)
        leads_by_source = await self._lead_repo.count_by_source(client.id, days=7)

        user_prompt = (
            f"BUSINESS: {client.business_name} ({client.sector})\n"
            f"CITY: {client.city}\n"
            f"PERIOD: {week_ago} to {today}\n\n"
            f"METRICS:\n{json.dumps(metrics_summary, indent=2, default=str)}\n\n"
            f"LEADS BY SOURCE:\n{json.dumps(leads_by_source, indent=2, default=str)}\n\n"
            f"Generate a weekly performance report for the business owner."
        )

        report = await self._ai.generate(
            system_prompt=WEEKLY_REPORT_PROMPT,
            user_prompt=user_prompt,
        )

        return report

    async def send_weekly_report(self, client: Client) -> None:
        report = await self.generate_weekly_report(client)

        await self._messaging.send_text(
            to=client.phone_number,
            body=report,
        )

        # Send follow-up with interactive buttons
        await self._messaging.send_interactive(
            to=client.phone_number,
            body="How was this week's marketing performance?",
            buttons=[
                {"id": "report_good", "title": "Keep going"},
                {"id": "report_change", "title": "Need changes"},
                {"id": "report_talk", "title": "Talk to human"},
            ],
        )

        logger.info(f"Weekly report sent to {client.phone_number}")

    async def send_revenue_check(self, client: Client) -> None:
        leads_count = await self._lead_repo.count_by_source(client.id, days=7)
        total_leads = sum(leads_count.values()) if leads_count else 0

        if total_leads == 0:
            return

        await self._messaging.send_interactive(
            to=client.phone_number,
            body=f"Quick check: {total_leads} people contacted you this week from your marketing.\nHow many became customers?",
            buttons=[
                {"id": "rev_0", "title": "None yet"},
                {"id": "rev_1_3", "title": "1-3 customers"},
                {"id": "rev_4_plus", "title": "4+ customers"},
            ],
        )
