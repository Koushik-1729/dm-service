from decimal import Decimal
from typing import Any, Dict, Optional
from uuid import UUID

from app.core.marketing_stack.constants.status_constants import ConversationContextType
from app.core.marketing_stack.outbound.external.messaging_port import MessagingPort
from app.core.marketing_stack.outbound.repositories.marketing_event_repository import MarketingEventRepository
from app.core.marketing_stack.outbound.repositories.user_repository import UserRepository
from app.core.marketing_stack.services.conversation_service import ConversationService
from app.core.marketing_stack.services.event_ingestion_service import EventIngestionService


class JourneyService:
    """Coordinates registration, follow-up, survey, and conversion lifecycle flows."""

    def __init__(
        self,
        user_repository: UserRepository,
        marketing_event_repository: MarketingEventRepository,
        event_ingestion_service: EventIngestionService,
        messaging_port: MessagingPort,
        conversation_service: ConversationService,
    ):
        self._users = user_repository
        self._events = marketing_event_repository
        self._event_ingestion = event_ingestion_service
        self._messaging = messaging_port
        self._conversation = conversation_service

    async def register_user(
        self,
        *,
        client_id: UUID,
        external_ref: Optional[str] = None,
        email: Optional[str] = None,
        phone_number: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        channel: Optional[str] = None,
        campaign_id: Optional[str] = None,
        adset_id: Optional[str] = None,
        creative_id: Optional[str] = None,
        session_id: Optional[str] = None,
        source_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        registration = await self._event_ingestion.ingest_event(
            client_id=client_id,
            event_type="registration_completed",
            external_ref=external_ref,
            email=email,
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            channel=channel,
            campaign_id=campaign_id,
            adset_id=adset_id,
            creative_id=creative_id,
            session_id=session_id,
            source_id=source_id,
            metadata=metadata,
        )

        thank_you_message_id = None
        user = registration["user"]
        if user.phone_number:
            thank_you_text = self._build_thank_you_message(user.first_name)
            thank_you_message_id = await self._messaging.send_text(
                to=user.phone_number,
                body=thank_you_text,
            )
            await self._conversation.log_outbound(
                client_id=client_id,
                phone_number=user.phone_number,
                content=thank_you_text,
                wa_message_id=thank_you_message_id,
                context_type=ConversationContextType.LEAD_FOLLOWUP,
            )
            await self._event_ingestion.ingest_event(
                client_id=client_id,
                event_type="thank_you_sent",
                external_ref=user.external_ref,
                email=user.email,
                phone_number=user.phone_number,
                first_name=user.first_name,
                last_name=user.last_name,
                channel=channel,
                campaign_id=campaign_id,
                session_id=session_id,
                message_id=thank_you_message_id,
                source_id=source_id,
                metadata={"trigger": "registration_completed"},
            )

        return {
            "user": user,
            "registration_event": registration["marketing_event"],
            "thank_you_message_id": thank_you_message_id,
        }

    async def trigger_no_conversion_followup(
        self,
        *,
        client_id: UUID,
        user_id: UUID,
        channel: str = "whatsapp",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        user = await self._users.get_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        user_events = await self._events.list_by_user(user_id, limit=200)
        converted = any(
            event.event_type in EventIngestionService.CONVERSION_EVENT_TYPES
            for event in user_events
        )
        if converted:
            return {
                "user": user,
                "followup_sent": False,
                "reason": "user_already_converted",
            }

        if not user.phone_number:
            return {
                "user": user,
                "followup_sent": False,
                "reason": "missing_phone_number",
            }

        followup_text = self._build_followup_message(user.first_name)
        followup_message_id = await self._messaging.send_text(
            to=user.phone_number,
            body=followup_text,
        )
        await self._conversation.log_outbound(
            client_id=client_id,
            phone_number=user.phone_number,
            content=followup_text,
            wa_message_id=followup_message_id,
            context_type=ConversationContextType.LEAD_FOLLOWUP,
        )

        survey_prompt = "What stopped you from completing signup or purchase?"
        survey_message_id = await self._messaging.send_interactive(
            to=user.phone_number,
            body=survey_prompt,
            buttons=[
                {"id": "survey_price", "title": "Too expensive"},
                {"id": "survey_not_ready", "title": "Not ready"},
                {"id": "survey_confused", "title": "Need more info"},
            ],
        )
        await self._conversation.log_outbound(
            client_id=client_id,
            phone_number=user.phone_number,
            content=survey_prompt,
            wa_message_id=survey_message_id,
            message_type="interactive",
            context_type=ConversationContextType.LEAD_FOLLOWUP,
            metadata={"buttons": ["survey_price", "survey_not_ready", "survey_confused"]},
        )

        await self._event_ingestion.ingest_event(
            client_id=client_id,
            event_type="followup_sent",
            external_ref=user.external_ref,
            email=user.email,
            phone_number=user.phone_number,
            first_name=user.first_name,
            last_name=user.last_name,
            channel=channel,
            message_id=followup_message_id,
            metadata=metadata or {"flow": "no_conversion"},
        )
        survey_event = await self._event_ingestion.ingest_event(
            client_id=client_id,
            event_type="survey_sent",
            external_ref=user.external_ref,
            email=user.email,
            phone_number=user.phone_number,
            first_name=user.first_name,
            last_name=user.last_name,
            channel=channel,
            message_id=survey_message_id,
            metadata={"question": survey_prompt},
        )

        return {
            "user": user,
            "followup_sent": True,
            "followup_message_id": followup_message_id,
            "survey_event": survey_event["marketing_event"],
        }

    async def record_survey_response(
        self,
        *,
        client_id: UUID,
        user_id: UUID,
        response_text: str,
        response_code: Optional[str] = None,
        channel: str = "whatsapp",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        user = await self._users.get_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        result = await self._event_ingestion.ingest_event(
            client_id=client_id,
            event_type="survey_completed",
            external_ref=user.external_ref,
            email=user.email,
            phone_number=user.phone_number,
            first_name=user.first_name,
            last_name=user.last_name,
            channel=channel,
            metadata={
                "response_text": response_text,
                "response_code": response_code,
                **(metadata or {}),
            },
        )
        return {
            "user": user,
            "survey_event": result["marketing_event"],
        }

    async def record_conversion(
        self,
        *,
        client_id: UUID,
        user_id: UUID,
        conversion_type: str,
        revenue_amount: Decimal,
        currency: str = "INR",
        payment_reference: Optional[str] = None,
        channel: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        user = await self._users.get_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        result = await self._event_ingestion.ingest_event(
            client_id=client_id,
            event_type="purchase_completed",
            external_ref=user.external_ref,
            email=user.email,
            phone_number=user.phone_number,
            first_name=user.first_name,
            last_name=user.last_name,
            channel=channel,
            revenue_amount=revenue_amount,
            currency=currency,
            conversion_type=conversion_type,
            payment_reference=payment_reference,
            metadata=metadata,
        )
        return result

    def _build_thank_you_message(self, first_name: Optional[str]) -> str:
        name = f" {first_name}" if first_name else ""
        return (
            f"Thanks{name} for signing up. We have your request and will guide you through the next steps shortly."
        )

    def _build_followup_message(self, first_name: Optional[str]) -> str:
        name = f" {first_name}" if first_name else ""
        return (
            f"Hi{name}, just checking in. You started the process but did not complete it yet. "
            f"If you want, we can help you finish in a few minutes."
        )
