from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID

from app.core.marketing_stack.constants.status_constants import (
    OnboardingStatus,
    SubscriptionTier,
    AutonomyLevel,
)
from app.core.marketing_stack.constants.onboarding_constants import (
    ONBOARDING_QUESTIONS,
    TOTAL_QUESTIONS,
)


class Client:
    """Domain model representing a business client."""

    def __init__(
        self,
        id: Optional[UUID] = None,
        phone_number: str = "",
        business_name: Optional[str] = None,
        owner_name: Optional[str] = None,
        sector: Optional[str] = None,
        sub_sector: Optional[str] = None,
        website_url: Optional[str] = None,
        google_maps_url: Optional[str] = None,
        instagram_handle: Optional[str] = None,
        city: Optional[str] = None,
        locality: Optional[str] = None,
        language: str = "english",
        business_profile: Optional[Dict[str, Any]] = None,
        scraped_data: Optional[Dict[str, Any]] = None,
        onboarding_status: str = OnboardingStatus.PENDING_QUESTIONS,
        onboarding_answers: Optional[Dict[str, str]] = None,
        current_question_index: int = 0,
        subscription_tier: str = SubscriptionTier.TRIAL,
        autonomy_level: str = AutonomyLevel.SUPERVISED,
        content_review_state: Optional[Dict[str, Any]] = None,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.phone_number = phone_number
        self.business_name = business_name
        self.owner_name = owner_name
        self.sector = sector
        self.sub_sector = sub_sector
        self.website_url = website_url
        self.google_maps_url = google_maps_url
        self.instagram_handle = instagram_handle
        self.city = city
        self.locality = locality
        self.language = language
        self.business_profile = business_profile or {}
        self.scraped_data = scraped_data or {}
        self.onboarding_status = onboarding_status
        self.onboarding_answers = onboarding_answers or {}
        self.current_question_index = current_question_index
        self.subscription_tier = subscription_tier
        self.autonomy_level = autonomy_level
        self.content_review_state = content_review_state or {}
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at

    def is_onboarding_complete(self) -> bool:
        return self.onboarding_status == OnboardingStatus.COMPLETE

    def get_current_question(self) -> Optional[Dict[str, str]]:
        if self.current_question_index < TOTAL_QUESTIONS:
            return ONBOARDING_QUESTIONS[self.current_question_index]
        return None

    def record_answer(self, answer: str) -> None:
        question = self.get_current_question()
        if question:
            self.onboarding_answers[question["id"]] = answer
            self.current_question_index += 1

    def has_answered_all_questions(self) -> bool:
        return self.current_question_index >= TOTAL_QUESTIONS

    def complete_onboarding(self, profile: Dict[str, Any]) -> None:
        self.business_profile = profile
        self.sector = profile.get("sector")
        self.sub_sector = profile.get("sub_sector")
        self.business_name = profile.get("business_name", self.business_name)
        self.city = profile.get("city", self.city)
        self.locality = profile.get("locality", self.locality)
        self.language = profile.get("language", self.language)
        self.onboarding_status = OnboardingStatus.COMPLETE
        self.updated_at = datetime.utcnow()

    def upgrade_autonomy(self, level: str) -> None:
        self.autonomy_level = level
        self.updated_at = datetime.utcnow()
