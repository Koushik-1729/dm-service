from decimal import Decimal
from uuid import uuid4

from app.core.marketing_stack.models.decision_log import DecisionLog
from app.core.marketing_stack.outbound.repositories.decision_log_repository import DecisionLogRepository
from app.core.marketing_stack.outbound.repositories.marketing_event_repository import MarketingEventRepository
from app.core.marketing_stack.outbound.repositories.prediction_score_repository import PredictionScoreRepository
from app.core.marketing_stack.outbound.repositories.user_repository import UserRepository
from app.core.marketing_stack.services.prediction_service import PredictionService


class DecisionService:
    """Chooses the next best action using prediction scores and lightweight policies."""

    def __init__(
        self,
        user_repository: UserRepository,
        marketing_event_repository: MarketingEventRepository,
        prediction_score_repository: PredictionScoreRepository,
        prediction_service: PredictionService,
        decision_log_repository: DecisionLogRepository,
    ):
        self._users = user_repository
        self._events = marketing_event_repository
        self._prediction_repo = prediction_score_repository
        self._prediction_service = prediction_service
        self._decisions = decision_log_repository

    async def decide_for_user(self, client_id, user_id) -> DecisionLog:
        user = await self._users.get_by_id(user_id)
        if not user or user.client_id != client_id:
            raise ValueError(f"User {user_id} not found")

        prediction = await self._prediction_repo.get_latest_by_user(user_id)
        if not prediction:
            prediction = await self._prediction_service.score_user(client_id, user_id)

        events = await self._events.list_by_user(user_id, limit=200)
        event_types = {event.event_type for event in events}

        action_type = "monitor"
        action_payload = {"message": "No action required right now"}
        reason = "User is progressing normally; keep monitoring."
        confidence = 0.55
        impact = Decimal("0")

        if prediction.dropout_risk >= 0.75 and "followup_sent" not in event_types:
            action_type = "send_followup"
            action_payload = {
                "channel": user.phone_number and "whatsapp" or "manual",
                "priority": "high",
            }
            reason = "High dropout risk and no follow-up sent yet."
            confidence = min(0.95, prediction.dropout_risk)
            impact = prediction.expected_revenue
        elif prediction.dropout_risk >= 0.70 and "survey_completed" not in event_types:
            action_type = "send_survey"
            action_payload = {
                "channel": user.phone_number and "whatsapp" or "manual",
                "priority": "high",
            }
            reason = "User shows high dropout risk and we still do not know the friction reason."
            confidence = min(0.92, prediction.dropout_risk)
            impact = prediction.expected_revenue * Decimal("0.50")
        elif prediction.conversion_probability >= 0.65 and "purchase_completed" not in event_types:
            action_type = "send_offer"
            action_payload = {
                "channel": user.phone_number and "whatsapp" or "manual",
                "priority": "medium",
                "offer_type": "conversion_nudge",
            }
            reason = "User has high conversion probability and is worth nudging now."
            confidence = prediction.conversion_probability
            impact = prediction.expected_revenue
        elif "followup_sent" in event_types and "survey_completed" in event_types and prediction.dropout_risk >= 0.60:
            action_type = "escalate_to_human"
            action_payload = {"queue": "sales", "priority": "medium"}
            reason = "Automation has enough negative signals; human intervention is more likely to help."
            confidence = 0.72
            impact = prediction.expected_revenue * Decimal("0.70")

        decision = DecisionLog(
            id=uuid4(),
            client_id=client_id,
            user_id=user_id,
            prediction_score_id=prediction.id,
            action_type=action_type,
            action_payload=action_payload,
            confidence=round(confidence, 4),
            expected_revenue_impact=impact.quantize(Decimal("0.01")),
            reason=reason,
            status="recommended",
        )
        return await self._decisions.create(decision)

    async def decide_for_client(self, client_id, limit: int = 100):
        users = await self._users.list_by_client(client_id, limit=limit)
        decisions = []
        for user in users:
            decisions.append(await self.decide_for_user(client_id, user.id))
        return decisions
