from decimal import Decimal
from uuid import uuid4

from app.core.marketing_stack.models.prediction_score import PredictionScore
from app.core.marketing_stack.outbound.repositories.prediction_score_repository import PredictionScoreRepository
from app.core.marketing_stack.outbound.repositories.user_repository import UserRepository
from app.core.marketing_stack.services.feature_service import FeatureService


class PredictionService:
    """Produces baseline conversion and dropout scores for users."""

    MODEL_NAME = "baseline_v1"

    def __init__(
        self,
        user_repository: UserRepository,
        feature_service: FeatureService,
        prediction_score_repository: PredictionScoreRepository,
    ):
        self._users = user_repository
        self._features = feature_service
        self._predictions = prediction_score_repository

    async def score_user(self, client_id, user_id) -> PredictionScore:
        user = await self._users.get_by_id(user_id)
        if not user or user.client_id != client_id:
            raise ValueError(f"User {user_id} not found")

        features = await self._features.build_user_features(client_id, user_id)
        conversion_probability = self._score_conversion_probability(features)
        dropout_risk = self._score_dropout_risk(features)
        expected_revenue = self._score_expected_revenue(features, conversion_probability)

        prediction = PredictionScore(
            id=uuid4(),
            client_id=client_id,
            user_id=user_id,
            model_name=self.MODEL_NAME,
            conversion_probability=conversion_probability,
            dropout_risk=dropout_risk,
            expected_revenue=expected_revenue,
            feature_snapshot=features,
        )
        return await self._predictions.create(prediction)

    async def score_client_users(self, client_id, limit: int = 100):
        users = await self._users.list_by_client(client_id, limit=limit)
        scored = []
        for user in users:
            scored.append(await self.score_user(client_id, user.id))
        return scored

    def _score_conversion_probability(self, features) -> float:
        if features["has_conversion"]:
            return 0.99

        score = 0.10
        if features["has_registration"]:
            score += 0.20
        if features["has_thank_you"]:
            score += 0.08
        if features["has_followup"]:
            score += 0.12
        if features["has_survey"]:
            score += 0.05
        if features["days_since_last_event"] <= 1:
            score += 0.15
        elif features["days_since_last_event"] <= 3:
            score += 0.08
        elif features["days_since_last_event"] >= 14:
            score -= 0.10
        if features["channel_roi_30d"] >= 3:
            score += 0.10
        elif features["channel_roi_30d"] > 0:
            score += 0.05
        if features["channel_messages_read_30d"] > 0:
            score += 0.05
        return round(max(0.01, min(score, 0.95)), 4)

    def _score_dropout_risk(self, features) -> float:
        if features["has_conversion"]:
            return 0.01

        risk = 0.25
        if not features["has_thank_you"]:
            risk += 0.15
        if features["days_since_last_event"] >= 3:
            risk += 0.15
        if features["days_since_last_event"] >= 7:
            risk += 0.20
        if features["has_followup"] and not features["has_survey"]:
            risk += 0.08
        if features["channel_roi_30d"] < 1 and features["channel_leads_30d"] > 0:
            risk += 0.07
        if features["has_survey"]:
            risk += 0.05
        return round(max(0.01, min(risk, 0.99)), 4)

    def _score_expected_revenue(self, features, conversion_probability: float) -> Decimal:
        revenue_per_lead = Decimal(str(features["channel_revenue_per_lead_30d"]))
        if revenue_per_lead <= 0:
            revenue_per_lead = Decimal("1000")
        expected = revenue_per_lead * Decimal(str(conversion_probability))
        return expected.quantize(Decimal("0.01"))
