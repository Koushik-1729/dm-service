import hashlib
from typing import Optional, Dict, Any
from uuid import UUID
from urllib.parse import urlencode
from loguru import logger

from app.core.marketing_stack.outbound.repositories.lead_repository import LeadRepository
from app.core.marketing_stack.outbound.repositories.metrics_repository import MetricsRepository


class AttributionService:
    """Generates tracking links, coupon codes, and attributes revenue to channels."""

    def __init__(
        self,
        lead_repository: LeadRepository,
        metrics_repository: MetricsRepository,
    ):
        self._lead_repo = lead_repository
        self._metrics_repo = metrics_repository

    def generate_tracking_link(
        self,
        base_url: str,
        client_id: UUID,
        channel: str,
        campaign_name: Optional[str] = None,
    ) -> str:
        utm_params = {
            "utm_source": channel,
            "utm_medium": "ai_marketing",
            "utm_campaign": campaign_name or "general",
            "utm_content": str(client_id)[:8],
        }
        return f"{base_url}?{urlencode(utm_params)}"

    def generate_whatsapp_link(
        self,
        whatsapp_number: str,
        client_id: UUID,
        channel: str,
    ) -> str:
        tag = self._generate_coupon_code(client_id, channel)
        return f"https://wa.me/{whatsapp_number}?text={tag}"

    def generate_coupon_code(
        self,
        client_id: UUID,
        channel: str,
    ) -> str:
        return self._generate_coupon_code(client_id, channel)

    def _generate_coupon_code(self, client_id: UUID, channel: str) -> str:
        channel_short = {
            "instagram": "IG",
            "whatsapp": "WA",
            "google_ads": "GO",
            "facebook": "FB",
            "google_business": "GB",
            "email": "EM",
        }.get(channel, "XX")

        client_hash = hashlib.md5(str(client_id).encode()).hexdigest()[:4].upper()
        return f"{client_hash}-{channel_short}"

    def parse_source_from_message(self, message: str) -> Optional[str]:
        message_upper = message.upper()

        channel_tags = {
            "-IG": "instagram",
            "-WA": "whatsapp",
            "-GO": "google_ads",
            "-FB": "facebook",
            "-GB": "google_business",
            "-EM": "email",
        }

        for tag, channel in channel_tags.items():
            if tag in message_upper:
                return channel

        return None

    async def get_revenue_summary(self, client_id: UUID, days: int = 7) -> Dict[str, Any]:
        leads_by_source = await self._lead_repo.count_by_source(client_id, days=days)
        metrics_summary = await self._metrics_repo.get_summary(client_id, days=days)

        return {
            "leads_by_source": leads_by_source,
            "metrics": metrics_summary,
            "period_days": days,
        }
