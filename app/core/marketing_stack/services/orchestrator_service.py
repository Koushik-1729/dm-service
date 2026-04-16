from typing import Optional
from uuid import UUID
from loguru import logger

from app.core.marketing_stack.models.client import Client
from app.core.marketing_stack.outbound.repositories.client_repository import ClientRepository
from app.core.marketing_stack.services.onboarding_service import OnboardingService
from app.core.marketing_stack.services.strategy_service import StrategyService
from app.core.marketing_stack.services.content_service import ContentService
from app.core.marketing_stack.services.execution_service import ExecutionService
from app.core.marketing_stack.services.lead_service import LeadService
from app.core.marketing_stack.services.attribution_service import AttributionService
from app.core.marketing_stack.services.conversation_service import ConversationService
from app.core.marketing_stack.outbound.external.messaging_port import MessagingPort
from app.core.marketing_stack.constants.status_constants import OnboardingStatus


class OrchestratorService:
    """Master dispatcher. Routes incoming WhatsApp messages to the correct service
    based on client state."""

    def __init__(
        self,
        client_repository: ClientRepository,
        onboarding_service: OnboardingService,
        strategy_service: StrategyService,
        content_service: ContentService,
        execution_service: ExecutionService,
        lead_service: LeadService,
        attribution_service: AttributionService,
        conversation_service: ConversationService,
        messaging_port: MessagingPort,
    ):
        self._client_repo = client_repository
        self._onboarding = onboarding_service
        self._strategy = strategy_service
        self._content = content_service
        self._execution = execution_service
        self._lead = lead_service
        self._attribution = attribution_service
        self._conversation = conversation_service
        self._messaging = messaging_port

    async def handle_incoming_message(
        self,
        phone_number: str,
        message_text: str,
        wa_message_id: str,
        message_type: str = "text",
        metadata: Optional[dict] = None,
    ) -> None:
        # Deduplicate
        if await self._conversation.is_duplicate(wa_message_id):
            logger.debug(f"Duplicate message {wa_message_id}, skipping")
            return

        # Mark as read
        await self._messaging.mark_as_read(wa_message_id)

        # Get or create client
        client = await self._onboarding.get_or_create_client(phone_number)

        # Log inbound message
        await self._conversation.log_inbound(
            client_id=client.id,
            phone_number=phone_number,
            content=message_text,
            wa_message_id=wa_message_id,
            message_type=message_type,
            context_type=self._determine_context(client, message_text),
            metadata=metadata,
        )

        # Route based on client state
        response = await self._route_message(client, message_text, message_type)

        if response:
            sent_id = await self._messaging.send_text(to=phone_number, body=response)

            await self._conversation.log_outbound(
                client_id=client.id,
                phone_number=phone_number,
                content=response,
                wa_message_id=sent_id,
                context_type=self._determine_context(client, message_text),
            )

    async def _route_message(
        self,
        client: Client,
        message_text: str,
        message_type: str,
    ) -> Optional[str]:

        # CASE 1: Client still onboarding
        if not client.is_onboarding_complete():
            response = await self._onboarding.handle_message(client.phone_number, message_text)

            # If onboarding just completed, trigger strategy + content generation
            refreshed = await self._client_repo.get_by_phone(client.phone_number)
            if refreshed and refreshed.is_onboarding_complete() and response:
                # Send the "30 seconds" response FIRST, then generate in background
                import asyncio
                asyncio.ensure_future(self._post_onboarding_flow(refreshed))
            return response

        # CASE 2: Client is in content review mode — handle variant picks
        review_state = client.content_review_state or {}
        if review_state.get("reviewing"):
            text_lower = message_text.strip().upper()
            # Check for variant pick from button or text
            picked = None
            if text_lower in ("A", "B", "C", "PICK A", "PICK B", "PICK C"):
                picked = text_lower.replace("PICK ", "")
            elif "pick_" in message_text.lower():
                picked = message_text.lower().replace("pick_", "").upper()

            if picked:
                await self._handle_variant_pick(client, picked)
                return None  # Response sent inside _handle_variant_pick
            else:
                return "Please pick A, B, or C for the current content."

        # CASE 3: Approval response — start content review
        if message_text.strip().lower() in ("yes", "approve", "ok", "👍"):
            await self._handle_approval(client)
            return None  # Response sent inside _handle_approval

        # CASE 4: Revenue check response
        if message_text.strip().lower() in ("0", "1-3", "4+", "none"):
            return self._handle_revenue_response(client, message_text)

        # CASE 5: Lead attribution — message contains a tracking code
        source = self._attribution.parse_source_from_message(message_text)
        if source:
            await self._lead.capture_lead(
                client_id=client.id,
                phone_number=client.phone_number,
                source_channel=source,
                source_campaign_tag=message_text.strip(),
            )
            return None

        # CASE 6: General message from an active client
        return (
            f"Hi! Your marketing is running smoothly.\n\n"
            f"Commands:\n"
            f"- 'report' — get your latest report\n"
            f"- 'pause' — pause all campaigns\n"
            f"- 'help' — talk to a human\n\n"
            f"Your next weekly report will be sent on Monday."
        )

    async def _post_onboarding_flow(self, client: Client) -> None:
        """Runs after onboarding completes: generate strategy + content + send for approval."""
        try:
            # Generate strategy
            strategy = await self._strategy.generate_strategy(client)
            logger.info(f"Strategy generated for {client.id}")

            # Generate content (non-blocking — OK if this fails)
            contents = []
            try:
                contents = await self._content.generate_weekly_content(client, strategy)
                logger.info(f"Generated {len(contents)} content pieces for {client.id}")
            except Exception as e:
                logger.error(f"Content generation failed for {client.id}: {e}")
                # Continue — we can still send the strategy

            # Send strategy summary for approval
            summary = self._format_strategy_summary(client, strategy, contents)
            sent_id = await self._messaging.send_text(to=client.phone_number, body=summary)

            await self._conversation.log_outbound(
                client_id=client.id,
                phone_number=client.phone_number,
                content=summary,
                wa_message_id=sent_id,
                context_type="approval",
            )

            await self._messaging.send_interactive(
                to=client.phone_number,
                body="Approve this marketing plan?",
                buttons=[
                    {"id": "approve_yes", "title": "Approve"},
                    {"id": "approve_edit", "title": "Edit something"},
                    {"id": "approve_no", "title": "Start over"},
                ],
            )

        except Exception as e:
            logger.error(f"Post-onboarding flow failed for {client.id}: {e}")
            try:
                await self._messaging.send_text(
                    to=client.phone_number,
                    body="Something went wrong generating your plan. Our team will look into it and get back to you shortly.",
                )
            except Exception:
                logger.error(f"Failed to send error message to {client.phone_number}")

    async def _handle_approval(self, client: Client) -> None:
        """Start content review flow — send first variant group for review."""
        # Get all unique variant groups that are still draft
        draft_content = await self._content._content_repo.list_by_client(
            client_id=client.id, status="draft"
        )

        if not draft_content:
            await self._messaging.send_text(
                to=client.phone_number,
                body="All content has been reviewed! Your campaigns are ready to go."
            )
            return

        # Group by variant_group
        groups = {}
        for c in draft_content:
            key = c.variant_group or c.id
            if key not in groups:
                groups[key] = []
            groups[key].append(c)

        group_keys = list(groups.keys())

        # Save review state
        client.content_review_state = {
            "groups": group_keys,
            "current_index": 0,
            "reviewing": True,
        }
        await self._client_repo.update(client)

        # Send the first group for review
        await self._send_variant_for_review(client, groups[group_keys[0]])

    async def _send_variant_for_review(self, client, variants):
        """Send A/B/C variants of one content piece for the client to pick."""
        group_index = client.content_review_state.get("current_index", 0)
        total_groups = len(client.content_review_state.get("groups", []))

        header = f"Content {group_index + 1} of {total_groups}"
        channel = variants[0].channel if variants else "unknown"
        content_type = variants[0].content_type if variants else "post"

        await self._messaging.send_text(
            to=client.phone_number,
            body=f"📝 {header} ({channel} {content_type})\n{'━' * 30}"
        )

        for variant in variants[:3]:  # Max 3 variants
            label = variant.variant_label
            caption = variant.caption[:800] if variant.caption else ""
            msg = f"*Option {label}:*\n\n{caption}"
            if variant.cta_text:
                msg += f"\n\n👉 {variant.cta_text}"
            await self._messaging.send_text(to=client.phone_number, body=msg)

        # Send selection buttons
        buttons = [{"id": f"pick_{v.variant_label}", "title": f"Pick {v.variant_label}"} for v in variants[:3]]
        await self._messaging.send_interactive(
            to=client.phone_number,
            body="Which version do you prefer?",
            buttons=buttons,
        )

    async def _handle_variant_pick(self, client, picked_label: str) -> None:
        """Handle when client picks a variant (A, B, or C)."""
        state = client.content_review_state
        if not state or not state.get("reviewing"):
            return

        group_keys = state.get("groups", [])
        current_index = state.get("current_index", 0)

        if current_index >= len(group_keys):
            return

        current_group_key = group_keys[current_index]

        # Approve the picked variant, archive others
        variants = await self._content._content_repo.list_by_variant_group(str(current_group_key))
        for v in variants:
            if v.variant_label.upper() == picked_label.upper():
                v.approve()
            else:
                v.status = "archived"
            await self._content._content_repo.update(v)

        # Move to next group
        next_index = current_index + 1
        client.content_review_state["current_index"] = next_index

        if next_index >= len(group_keys):
            # All reviewed
            client.content_review_state["reviewing"] = False
            await self._client_repo.update(client)
            await self._messaging.send_text(
                to=client.phone_number,
                body=f"All {len(group_keys)} content pieces reviewed and approved!\n\n"
                     f"Your marketing is now LIVE.\n"
                     f"I'll send you a performance report next Monday."
            )
        else:
            await self._client_repo.update(client)
            # Send next variant group
            next_group = await self._content._content_repo.list_by_variant_group(str(group_keys[next_index]))
            if next_group:
                await self._send_variant_for_review(client, next_group)

    def _handle_revenue_response(self, client: Client, response: str) -> str:
        return (
            f"Thanks for the update! This helps me optimize your campaigns.\n"
            f"I'll adjust next week's strategy based on this."
        )

    def _determine_context(self, client: Client, message: str) -> str:
        if not client.is_onboarding_complete():
            return "onboarding"
        lower = message.lower().strip()
        if lower in ("yes", "approve", "ok", "👍"):
            return "approval"
        if lower in ("report", "stats", "results"):
            return "report"
        return "support"

    def _format_strategy_summary(self, client: Client, strategy, contents) -> str:
        channels = ", ".join(ch["name"] for ch in strategy.channels if ch.get("active"))
        content_count = len(contents)

        return (
            f"Your Marketing Plan for {client.business_name}\n"
            f"{'=' * 35}\n\n"
            f"Channels: {channels}\n"
            f"Content ready: {content_count} pieces (with A/B variants)\n\n"
            f"Week 1 schedule:\n"
            + "\n".join(
                f"  {entry.get('day', '').title()}: {entry.get('content_type', '')} on {entry.get('channel', '')}"
                for entry in strategy.content_calendar[:5]
            )
            + f"\n\nStrategy: {strategy.ai_reasoning}\n"
        )
