from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4
from loguru import logger

from app.core.marketing_stack.models.content import Content
from app.core.marketing_stack.models.campaign import Campaign
from app.core.marketing_stack.models.client import Client
from app.core.marketing_stack.outbound.repositories.content_repository import ContentRepository
from app.core.marketing_stack.outbound.repositories.campaign_repository import CampaignRepository
from app.core.marketing_stack.outbound.external.messaging_port import MessagingPort
from app.core.marketing_stack.outbound.external.social_media_port import SocialMediaPort
from app.core.marketing_stack.constants.channel_constants import Channel, CampaignType
from app.core.marketing_stack.constants.status_constants import (
    ContentStatus,
    CampaignStatus,
    AutonomyLevel,
    RiskLevel,
)


class ExecutionService:
    """Layer 4: Publishes content to channels and manages campaigns."""

    def __init__(
        self,
        content_repository: ContentRepository,
        campaign_repository: CampaignRepository,
        messaging_port: MessagingPort,
        social_media_port: SocialMediaPort,
    ):
        self._content_repo = content_repository
        self._campaign_repo = campaign_repository
        self._messaging = messaging_port
        self._social_media = social_media_port

    async def publish_to_instagram(self, content: Content) -> Campaign:
        logger.info(f"Publishing to Instagram: content_id={content.id}")

        try:
            post_id = await self._social_media.publish_post(
                image_url=content.media_url or "",
                caption=self._build_instagram_caption(content),
            )

            content.mark_published(post_id)
            await self._content_repo.update(content)

            campaign = Campaign(
                id=uuid4(),
                client_id=content.client_id,
                content_id=content.id,
                channel=Channel.INSTAGRAM,
                campaign_type=CampaignType.ORGANIC_POST,
                status=CampaignStatus.COMPLETED,
                platform_id=post_id,
            )
            return await self._campaign_repo.create(campaign)

        except Exception as e:
            logger.error(f"Instagram publish failed: {e}")
            content.mark_failed()
            await self._content_repo.update(content)
            raise

    async def send_whatsapp_campaign(
        self,
        content: Content,
        recipients: List[str],
        template_name: str = "weekly_offer",
        language_code: str = "en",
    ) -> Campaign:
        logger.info(f"Sending WhatsApp campaign to {len(recipients)} recipients")

        sent_count = 0
        for phone in recipients:
            try:
                await self._messaging.send_template(
                    to=phone,
                    template_name=template_name,
                    language_code=language_code,
                    parameters=[{"type": "text", "text": content.caption}],
                )
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to send WhatsApp to {phone}: {e}")

        content.mark_published(f"whatsapp_broadcast_{sent_count}")
        await self._content_repo.update(content)

        campaign = Campaign(
            id=uuid4(),
            client_id=content.client_id,
            content_id=content.id,
            channel=Channel.WHATSAPP,
            campaign_type=CampaignType.WHATSAPP_BROADCAST,
            status=CampaignStatus.COMPLETED,
            platform_id=f"broadcast_{sent_count}_recipients",
        )
        return await self._campaign_repo.create(campaign)

    async def execute_approved_content(self, client: Client) -> List[Campaign]:
        approved = await self._content_repo.list_by_client(
            client_id=client.id,
            status=ContentStatus.APPROVED,
        )

        campaigns = []
        for content in approved:
            try:
                if content.channel == Channel.INSTAGRAM:
                    campaign = await self.publish_to_instagram(content)
                    campaigns.append(campaign)
            except Exception as e:
                logger.error(f"Failed to execute content {content.id}: {e}")

        return campaigns

    def should_auto_execute(self, content: Content, client: Client) -> bool:
        if client.autonomy_level == AutonomyLevel.SUPERVISED:
            return False
        if client.autonomy_level == AutonomyLevel.ASSISTED:
            return content.risk_level == RiskLevel.LOW
        if client.autonomy_level == AutonomyLevel.AUTONOMOUS:
            return content.risk_level != RiskLevel.HIGH
        return False

    def _build_instagram_caption(self, content: Content) -> str:
        caption = content.caption
        if content.hashtags:
            hashtag_str = " ".join(f"#{tag.replace('#', '')}" for tag in content.hashtags)
            caption = f"{caption}\n\n{hashtag_str}"
        return caption
