from datetime import datetime
from typing import Optional, List
from uuid import UUID


class Content:
    """Domain model representing a generated content piece."""

    def __init__(
        self,
        id: Optional[UUID] = None,
        client_id: Optional[UUID] = None,
        strategy_id: Optional[UUID] = None,
        channel: str = "",
        content_type: str = "",
        variant_group: Optional[str] = None,
        variant_label: str = "A",
        caption: str = "",
        media_url: Optional[str] = None,
        hashtags: Optional[List[str]] = None,
        cta_text: Optional[str] = None,
        cta_url: Optional[str] = None,
        coupon_code: Optional[str] = None,
        utm_params: Optional[str] = None,
        language: str = "english",
        ai_model_used: Optional[str] = None,
        risk_level: str = "low",
        status: str = "draft",
        scheduled_for: Optional[datetime] = None,
        published_at: Optional[datetime] = None,
        platform_post_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ):
        self.id = id
        self.client_id = client_id
        self.strategy_id = strategy_id
        self.channel = channel
        self.content_type = content_type
        self.variant_group = variant_group
        self.variant_label = variant_label
        self.caption = caption
        self.media_url = media_url
        self.hashtags = hashtags or []
        self.cta_text = cta_text
        self.cta_url = cta_url
        self.coupon_code = coupon_code
        self.utm_params = utm_params
        self.language = language
        self.ai_model_used = ai_model_used
        self.risk_level = risk_level
        self.status = status
        self.scheduled_for = scheduled_for
        self.published_at = published_at
        self.platform_post_id = platform_post_id
        self.created_at = created_at

    def approve(self) -> None:
        self.status = "approved"

    def mark_published(self, platform_post_id: str) -> None:
        self.status = "published"
        self.platform_post_id = platform_post_id
        self.published_at = datetime.utcnow()

    def mark_failed(self) -> None:
        self.status = "failed"

    def is_publishable(self) -> bool:
        return self.status in ("approved", "scheduled")
