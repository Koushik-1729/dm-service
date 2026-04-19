"""Shared test fixtures and mock implementations for all tests."""
import pytest
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime, date
from decimal import Decimal

from app.core.marketing_stack.models.client import Client
from app.core.marketing_stack.models.conversation import Conversation
from app.core.marketing_stack.models.strategy import Strategy
from app.core.marketing_stack.models.content import Content
from app.core.marketing_stack.models.campaign import Campaign
from app.core.marketing_stack.models.lead import Lead
from app.core.marketing_stack.models.daily_metrics import DailyMetrics
from app.core.marketing_stack.models.usage import Usage
from app.core.marketing_stack.models.user import User
from app.core.marketing_stack.models.user_identity import UserIdentity
from app.core.marketing_stack.models.marketing_event import MarketingEvent
from app.core.marketing_stack.models.conversion_event import ConversionEvent
from app.core.marketing_stack.models.revenue_event import RevenueEvent
from app.core.marketing_stack.models.prediction_score import PredictionScore
from app.core.marketing_stack.models.decision_log import DecisionLog

from app.core.marketing_stack.outbound.repositories.client_repository import ClientRepository
from app.core.marketing_stack.outbound.repositories.conversation_repository import ConversationRepository
from app.core.marketing_stack.outbound.repositories.strategy_repository import StrategyRepository
from app.core.marketing_stack.outbound.repositories.content_repository import ContentRepository
from app.core.marketing_stack.outbound.repositories.campaign_repository import CampaignRepository
from app.core.marketing_stack.outbound.repositories.lead_repository import LeadRepository
from app.core.marketing_stack.outbound.repositories.metrics_repository import MetricsRepository
from app.core.marketing_stack.outbound.repositories.usage_repository import UsageRepository
from app.core.marketing_stack.outbound.repositories.user_repository import UserRepository
from app.core.marketing_stack.outbound.repositories.user_identity_repository import UserIdentityRepository
from app.core.marketing_stack.outbound.repositories.marketing_event_repository import MarketingEventRepository
from app.core.marketing_stack.outbound.repositories.conversion_event_repository import ConversionEventRepository
from app.core.marketing_stack.outbound.repositories.revenue_event_repository import RevenueEventRepository
from app.core.marketing_stack.outbound.repositories.prediction_score_repository import PredictionScoreRepository
from app.core.marketing_stack.outbound.repositories.decision_log_repository import DecisionLogRepository

from app.core.marketing_stack.outbound.external.ai_provider_port import AIProviderPort
from app.core.marketing_stack.outbound.external.web_scraper_port import WebScraperPort
from app.core.marketing_stack.outbound.external.messaging_port import MessagingPort
from app.core.marketing_stack.outbound.external.social_media_port import SocialMediaPort
from app.core.marketing_stack.outbound.external.playbook_loader_port import PlaybookLoaderPort


# Mock Repository Implementations

class MockClientRepository(ClientRepository):
    def __init__(self):
        self._store: Dict[UUID, Client] = {}

    async def create(self, client: Client) -> Client:
        if not client.id:
            client.id = uuid4()
        client.created_at = datetime.utcnow()
        self._store[client.id] = client
        return client

    async def get_by_id(self, client_id: UUID) -> Optional[Client]:
        return self._store.get(client_id)

    async def get_by_phone(self, phone_number: str) -> Optional[Client]:
        for c in self._store.values():
            if c.phone_number == phone_number:
                return c
        return None

    async def update(self, client: Client) -> Client:
        self._store[client.id] = client
        return client

    async def list_active(self) -> List[Client]:
        return [c for c in self._store.values() if c.is_active]

    async def list_by_sector(self, sector: str) -> List[Client]:
        return [c for c in self._store.values() if c.sector == sector]


class MockConversationRepository(ConversationRepository):
    def __init__(self):
        self._store: List[Conversation] = []

    async def create(self, conversation: Conversation) -> Conversation:
        if not conversation.id:
            conversation.id = uuid4()
        conversation.created_at = datetime.utcnow()
        self._store.append(conversation)
        return conversation

    async def get_by_wa_message_id(self, wa_message_id: str) -> Optional[Conversation]:
        for c in self._store:
            if c.wa_message_id == wa_message_id:
                return c
        return None

    async def get_recent_by_client(self, client_id: UUID, limit: int = 20) -> List[Conversation]:
        return [c for c in self._store if c.client_id == client_id][-limit:]

    async def get_recent_by_phone(self, phone_number: str, limit: int = 20) -> List[Conversation]:
        return [c for c in self._store if c.phone_number == phone_number][-limit:]


class MockStrategyRepository(StrategyRepository):
    def __init__(self):
        self._store: Dict[UUID, Strategy] = {}

    async def create(self, strategy: Strategy) -> Strategy:
        if not strategy.id:
            strategy.id = uuid4()
        strategy.created_at = datetime.utcnow()
        self._store[strategy.id] = strategy
        return strategy

    async def get_by_id(self, strategy_id: UUID) -> Optional[Strategy]:
        return self._store.get(strategy_id)

    async def get_active_by_client(self, client_id: UUID) -> Optional[Strategy]:
        for s in self._store.values():
            if s.client_id == client_id and s.status == "active":
                return s
        return None

    async def update(self, strategy: Strategy) -> Strategy:
        self._store[strategy.id] = strategy
        return strategy

    async def list_by_client(self, client_id: UUID) -> List[Strategy]:
        return [s for s in self._store.values() if s.client_id == client_id]


class MockContentRepository(ContentRepository):
    def __init__(self):
        self._store: Dict[UUID, Content] = {}

    async def create(self, content: Content) -> Content:
        if not content.id:
            content.id = uuid4()
        content.created_at = datetime.utcnow()
        self._store[content.id] = content
        return content

    async def create_batch(self, contents: List[Content]) -> List[Content]:
        result = []
        for c in contents:
            result.append(await self.create(c))
        return result

    async def get_by_id(self, content_id: UUID) -> Optional[Content]:
        return self._store.get(content_id)

    async def list_by_client(self, client_id: UUID, status: Optional[str] = None, channel: Optional[str] = None) -> List[Content]:
        results = [c for c in self._store.values() if c.client_id == client_id]
        if status:
            results = [c for c in results if c.status == status]
        if channel:
            results = [c for c in results if c.channel == channel]
        return results

    async def get_scheduled(self, before: datetime) -> List[Content]:
        return [c for c in self._store.values() if c.status == "scheduled" and c.scheduled_for and c.scheduled_for <= before]

    async def list_by_variant_group(self, variant_group: str) -> List[Content]:
        return [c for c in self._store.values() if c.variant_group == variant_group]

    async def update(self, content: Content) -> Content:
        self._store[content.id] = content
        return content


class MockCampaignRepository(CampaignRepository):
    def __init__(self):
        self._store: Dict[UUID, Campaign] = {}

    async def create(self, campaign: Campaign) -> Campaign:
        if not campaign.id:
            campaign.id = uuid4()
        campaign.created_at = datetime.utcnow()
        self._store[campaign.id] = campaign
        return campaign

    async def get_by_id(self, campaign_id: UUID) -> Optional[Campaign]:
        return self._store.get(campaign_id)

    async def list_active_by_client(self, client_id: UUID) -> List[Campaign]:
        return [c for c in self._store.values() if c.client_id == client_id and c.status in ("scheduled", "running")]

    async def update(self, campaign: Campaign) -> Campaign:
        self._store[campaign.id] = campaign
        return campaign

    async def list_by_channel(self, client_id: UUID, channel: str) -> List[Campaign]:
        return [c for c in self._store.values() if c.client_id == client_id and c.channel == channel]


class MockLeadRepository(LeadRepository):
    def __init__(self):
        self._store: Dict[UUID, Lead] = {}

    async def create(self, lead: Lead) -> Lead:
        if not lead.id:
            lead.id = uuid4()
        lead.created_at = datetime.utcnow()
        self._store[lead.id] = lead
        return lead

    async def get_by_id(self, lead_id: UUID) -> Optional[Lead]:
        return self._store.get(lead_id)

    async def get_by_phone_and_client(self, phone_number: str, client_id: UUID) -> Optional[Lead]:
        for l in self._store.values():
            if l.phone_number == phone_number and l.client_id == client_id:
                return l
        return None

    async def list_by_client(self, client_id: UUID, status: Optional[str] = None) -> List[Lead]:
        results = [l for l in self._store.values() if l.client_id == client_id]
        if status:
            results = [l for l in results if l.status == status]
        return results

    async def list_needs_followup(self, client_id: UUID, max_followups: int = 3) -> List[Lead]:
        return [l for l in self._store.values() if l.client_id == client_id and l.status in ("new", "notified") and l.followup_count < max_followups]

    async def update(self, lead: Lead) -> Lead:
        self._store[lead.id] = lead
        return lead

    async def count_by_source(self, client_id: UUID, days: int = 7) -> dict:
        counts = {}
        for l in self._store.values():
            if l.client_id == client_id:
                counts[l.source_channel] = counts.get(l.source_channel, 0) + 1
        return counts


class MockMetricsRepository(MetricsRepository):
    def __init__(self):
        self._store: List[DailyMetrics] = []

    async def upsert_daily(self, metrics: DailyMetrics) -> DailyMetrics:
        if not metrics.id:
            metrics.id = uuid4()
        self._store.append(metrics)
        return metrics

    async def get_range(self, client_id: UUID, start_date: date, end_date: date, channel: Optional[str] = None) -> List[DailyMetrics]:
        return [m for m in self._store if m.client_id == client_id]

    async def get_latest(self, client_id: UUID) -> Optional[DailyMetrics]:
        client_metrics = [m for m in self._store if m.client_id == client_id]
        return client_metrics[-1] if client_metrics else None

    async def get_summary(self, client_id: UUID, days: int = 7) -> Dict[str, Any]:
        return {"instagram": {"impressions": 1000, "clicks": 50, "leads": 5, "revenue": 2500, "spend": 500, "roi": 5.0}}


class MockUsageRepository(UsageRepository):
    def __init__(self):
        self._store: List[Usage] = []

    async def create(self, usage: Usage) -> Usage:
        if not usage.id:
            usage.id = uuid4()
        self._store.append(usage)
        return usage

    async def get_total_by_client(self, client_id: UUID, start_date: date, end_date: date) -> Dict[str, Any]:
        return {"breakdown": {}, "total_cost_usd": 0.05}

    async def list_by_client(self, client_id: UUID, limit: int = 100) -> List[Usage]:
        return [u for u in self._store if u.client_id == client_id][:limit]


class MockUserRepository(UserRepository):
    def __init__(self):
        self._store: Dict[UUID, User] = {}

    async def create(self, user: User) -> User:
        if not user.id:
            user.id = uuid4()
        user.created_at = datetime.utcnow()
        self._store[user.id] = user
        return user

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        return self._store.get(user_id)

    async def get_by_external_ref(self, client_id: UUID, external_ref: str) -> Optional[User]:
        for user in self._store.values():
            if user.client_id == client_id and user.external_ref == external_ref:
                return user
        return None

    async def update(self, user: User) -> User:
        self._store[user.id] = user
        return user

    async def list_by_client(self, client_id: UUID, limit: int = 100) -> List[User]:
        return [user for user in self._store.values() if user.client_id == client_id][:limit]


class MockUserIdentityRepository(UserIdentityRepository):
    def __init__(self):
        self._store: Dict[UUID, UserIdentity] = {}

    async def create(self, identity: UserIdentity) -> UserIdentity:
        if not identity.id:
            identity.id = uuid4()
        identity.created_at = datetime.utcnow()
        self._store[identity.id] = identity
        return identity

    async def get_by_type_and_value(
        self,
        client_id: UUID,
        identity_type: str,
        identity_value: str,
    ) -> Optional[UserIdentity]:
        for identity in self._store.values():
            if (
                identity.client_id == client_id
                and identity.identity_type == identity_type
                and identity.identity_value == identity_value
            ):
                return identity
        return None

    async def list_by_user(self, user_id: UUID) -> List[UserIdentity]:
        return [identity for identity in self._store.values() if identity.user_id == user_id]


class MockMarketingEventRepository(MarketingEventRepository):
    def __init__(self):
        self._store: Dict[UUID, MarketingEvent] = {}

    async def create(self, event: MarketingEvent) -> MarketingEvent:
        if not event.id:
            event.id = uuid4()
        event.created_at = datetime.utcnow()
        self._store[event.id] = event
        return event

    async def get_by_id(self, event_id: UUID) -> Optional[MarketingEvent]:
        return self._store.get(event_id)

    async def list_by_user(self, user_id: UUID, limit: int = 100) -> List[MarketingEvent]:
        return [event for event in self._store.values() if event.user_id == user_id][:limit]


class MockConversionEventRepository(ConversionEventRepository):
    def __init__(self):
        self._store: Dict[UUID, ConversionEvent] = {}

    async def create(self, event: ConversionEvent) -> ConversionEvent:
        if not event.id:
            event.id = uuid4()
        event.created_at = datetime.utcnow()
        self._store[event.id] = event
        return event

    async def get_by_id(self, conversion_event_id: UUID) -> Optional[ConversionEvent]:
        return self._store.get(conversion_event_id)

    async def list_by_user(self, user_id: UUID, limit: int = 100) -> List[ConversionEvent]:
        return [event for event in self._store.values() if event.user_id == user_id][:limit]


class MockRevenueEventRepository(RevenueEventRepository):
    def __init__(self):
        self._store: Dict[UUID, RevenueEvent] = {}

    async def create(self, event: RevenueEvent) -> RevenueEvent:
        if not event.id:
            event.id = uuid4()
        event.created_at = datetime.utcnow()
        self._store[event.id] = event
        return event

    async def get_by_id(self, revenue_event_id: UUID) -> Optional[RevenueEvent]:
        return self._store.get(revenue_event_id)

    async def list_by_user(self, user_id: UUID, limit: int = 100) -> List[RevenueEvent]:
        return [event for event in self._store.values() if event.user_id == user_id][:limit]


class MockPredictionScoreRepository(PredictionScoreRepository):
    def __init__(self):
        self._store: Dict[UUID, PredictionScore] = {}

    async def create(self, prediction: PredictionScore) -> PredictionScore:
        if not prediction.id:
            prediction.id = uuid4()
        prediction.created_at = datetime.utcnow()
        self._store[prediction.id] = prediction
        return prediction

    async def get_latest_by_user(self, user_id: UUID) -> Optional[PredictionScore]:
        for prediction in reversed(list(self._store.values())):
            if prediction.user_id == user_id:
                return prediction
        return None

    async def list_latest_by_client(self, client_id: UUID, limit: int = 100) -> List[PredictionScore]:
        predictions = [prediction for prediction in self._store.values() if prediction.client_id == client_id]
        return predictions[:limit]


class MockDecisionLogRepository(DecisionLogRepository):
    def __init__(self):
        self._store: Dict[UUID, DecisionLog] = {}

    async def create(self, decision: DecisionLog) -> DecisionLog:
        if not decision.id:
            decision.id = uuid4()
        decision.created_at = datetime.utcnow()
        self._store[decision.id] = decision
        return decision

    async def get_latest_by_user(self, user_id: UUID) -> Optional[DecisionLog]:
        for decision in reversed(list(self._store.values())):
            if decision.user_id == user_id:
                return decision
        return None

    async def list_by_client(self, client_id: UUID, limit: int = 100) -> List[DecisionLog]:
        decisions = [decision for decision in self._store.values() if decision.client_id == client_id]
        return decisions[:limit]


# ─── Mock External Adapters ─────────────────────────────────────────

class MockAIProvider(AIProviderPort):
    def __init__(self, response: str = '{"sector": "restaurant", "business_name": "Test Cafe"}'):
        self._response = response
        self.calls: List[Dict] = []

    async def generate(self, system_prompt: str, user_prompt: str, max_tokens: int = 4096) -> str:
        self.calls.append({"system": system_prompt[:50], "user": user_prompt[:50]})
        return self._response

    async def generate_structured(self, system_prompt: str, user_prompt: str, response_schema=None, max_tokens: int = 4096) -> Dict[str, Any]:
        import json
        self.calls.append({"system": system_prompt[:50], "user": user_prompt[:50]})
        try:
            return json.loads(self._response)
        except:
            return {}


class MockWebScraper(WebScraperPort):
    async def scrape_url(self, url: str) -> Dict[str, Any]:
        return {
            "url": url,
            "title": "Test Business",
            "meta_description": "A great local business",
            "headings": ["Welcome", "Our Services"],
            "body_text": "We are a local coffee shop serving fresh coffee daily.",
            "contact": {"phone": "+919876543210"},
        }

    async def scrape_google_maps(self, url: str) -> Dict[str, Any]:
        return {"url": url, "name": "Test Business", "rating": 4.5, "review_count": 120}


class MockMessagingPort(MessagingPort):
    def __init__(self):
        self.sent_messages: List[Dict] = []

    async def send_text(self, to: str, body: str) -> str:
        msg_id = f"wamid.mock_{len(self.sent_messages)}"
        self.sent_messages.append({"to": to, "body": body, "type": "text", "id": msg_id})
        return msg_id

    async def send_template(self, to: str, template_name: str, language_code: str, parameters=None) -> str:
        msg_id = f"wamid.mock_{len(self.sent_messages)}"
        self.sent_messages.append({"to": to, "template": template_name, "type": "template", "id": msg_id})
        return msg_id

    async def send_interactive(self, to: str, body: str, buttons: list) -> str:
        msg_id = f"wamid.mock_{len(self.sent_messages)}"
        self.sent_messages.append({"to": to, "body": body, "buttons": buttons, "type": "interactive", "id": msg_id})
        return msg_id

    async def send_image(self, to: str, image_url: str, caption=None) -> str:
        msg_id = f"wamid.mock_{len(self.sent_messages)}"
        self.sent_messages.append({"to": to, "image_url": image_url, "type": "image", "id": msg_id})
        return msg_id

    async def mark_as_read(self, message_id: str) -> bool:
        return True


class MockSocialMediaPort(SocialMediaPort):
    def __init__(self):
        self.published: List[Dict] = []

    async def publish_post(self, image_url: str, caption: str) -> str:
        post_id = f"ig_post_{len(self.published)}"
        self.published.append({"image_url": image_url, "caption": caption, "id": post_id})
        return post_id

    async def publish_carousel(self, image_urls: list, caption: str) -> str:
        post_id = f"ig_carousel_{len(self.published)}"
        self.published.append({"image_urls": image_urls, "caption": caption, "id": post_id})
        return post_id

    async def get_post_insights(self, post_id: str) -> Dict[str, Any]:
        return {"impressions": 500, "reach": 300, "engagement": 45}

    async def get_account_insights(self, period: str = "day", metrics=None) -> Dict[str, Any]:
        return {"impressions": 5000, "reach": 3000, "follower_count": 1200}


class MockPlaybookLoader(PlaybookLoaderPort):
    def load(self, sector: str) -> Dict[str, Any]:
        return {
            "sector": sector,
            "channels": [
                {"name": "instagram", "priority": 1, "posts_per_week": 4},
                {"name": "whatsapp", "priority": 2, "messages_per_week": 2},
            ],
            "content_types": ["post", "reel_script", "campaign_message"],
            "posting_schedule": {
                "monday": {"channel": "instagram", "type": "post", "topic": "Test topic"},
            },
            "cold_start_defaults": {"avg_cpc": 15, "avg_ctr": 2.5, "avg_conversion_rate": 0.15, "avg_order_value": 500},
        }

    def list_sectors(self) -> List[str]:
        return ["restaurant", "clinic", "salon", "general"]


# ─── Fixtures ────────────────────────────────────────────────────────

@pytest.fixture
def mock_client_repo():
    return MockClientRepository()


@pytest.fixture
def mock_conversation_repo():
    return MockConversationRepository()


@pytest.fixture
def mock_strategy_repo():
    return MockStrategyRepository()


@pytest.fixture
def mock_content_repo():
    return MockContentRepository()


@pytest.fixture
def mock_campaign_repo():
    return MockCampaignRepository()


@pytest.fixture
def mock_lead_repo():
    return MockLeadRepository()


@pytest.fixture
def mock_metrics_repo():
    return MockMetricsRepository()


@pytest.fixture
def mock_ai_provider():
    return MockAIProvider()


@pytest.fixture
def mock_scraper():
    return MockWebScraper()


@pytest.fixture
def mock_messaging():
    return MockMessagingPort()


@pytest.fixture
def mock_social_media():
    return MockSocialMediaPort()


@pytest.fixture
def mock_playbook_loader():
    return MockPlaybookLoader()


@pytest.fixture
def mock_user_repo():
    return MockUserRepository()


@pytest.fixture
def mock_user_identity_repo():
    return MockUserIdentityRepository()


@pytest.fixture
def mock_marketing_event_repo():
    return MockMarketingEventRepository()


@pytest.fixture
def mock_conversion_event_repo():
    return MockConversionEventRepository()


@pytest.fixture
def mock_revenue_event_repo():
    return MockRevenueEventRepository()


@pytest.fixture
def mock_prediction_score_repo():
    return MockPredictionScoreRepository()


@pytest.fixture
def mock_decision_log_repo():
    return MockDecisionLogRepository()


@pytest.fixture
def sample_client():
    return Client(
        id=uuid4(),
        phone_number="+919876543210",
        business_name="Brew Culture",
        sector="restaurant",
        city="Hyderabad",
        locality="Jubilee Hills",
        language="english",
        onboarding_status="complete",
        business_profile={
            "sector": "restaurant",
            "business_name": "Brew Culture",
            "city": "Hyderabad",
            "target_audience": {"demographics": "IT professionals, college students"},
            "unique_selling_points": ["Own roasted beans", "Pet friendly", "Open till 1 AM"],
            "services_offered": ["Specialty coffee", "Cold brew", "Sandwiches"],
        },
    )


@pytest.fixture
def sample_strategy(sample_client):
    return Strategy(
        id=uuid4(),
        client_id=sample_client.id,
        version=1,
        channels=[
            {"name": "instagram", "priority": 1, "active": True, "posts_per_week": 4},
            {"name": "whatsapp", "priority": 2, "active": True, "messages_per_week": 2},
        ],
        content_calendar=[
            {"day": "monday", "channel": "instagram", "content_type": "post", "topic": "Signature drink"},
            {"day": "friday", "channel": "whatsapp", "content_type": "campaign_message", "topic": "Weekend offer"},
        ],
        kpis={"weekly_posts": 4, "monthly_leads_target": 20},
        status="active",
    )
