from fastapi import Depends
from sqlalchemy.orm import Session

from app.config.app_config import app_config
from app.config.db import get_db

# Repository implementations(WIP)
from app.infra.marketing_stack.repositories.client_repository_impl import ClientRepositoryImpl
from app.infra.marketing_stack.repositories.conversation_repository_impl import ConversationRepositoryImpl
from app.infra.marketing_stack.repositories.strategy_repository_impl import StrategyRepositoryImpl
from app.infra.marketing_stack.repositories.content_repository_impl import ContentRepositoryImpl
from app.infra.marketing_stack.repositories.campaign_repository_impl import CampaignRepositoryImpl
from app.infra.marketing_stack.repositories.lead_repository_impl import LeadRepositoryImpl
from app.infra.marketing_stack.repositories.metrics_repository_impl import MetricsRepositoryImpl
from app.infra.marketing_stack.repositories.usage_repository_impl import UsageRepositoryImpl

# we can use External adapters here if you want(WIP)
from app.infra.marketing_stack.external.claude_adapter import ClaudeAdapter
from app.infra.marketing_stack.external.gemini_adapter import GeminiAdapter
from app.infra.marketing_stack.external.openrouter_adapter import OpenRouterAdapter
from app.infra.marketing_stack.external.model_router_adapter import ModelRouterAdapter
from app.infra.marketing_stack.external.whatsapp_adapter import WhatsAppAdapter
from app.infra.marketing_stack.external.beautifulsoup_scraper import BeautifulSoupScraper
from app.infra.marketing_stack.external.instagram_adapter import InstagramAdapter
from app.infra.marketing_stack.external.json_playbook_adapter import JsonPlaybookAdapter

# app services 
from app.core.marketing_stack.services.conversation_service import ConversationService
from app.core.marketing_stack.services.onboarding_service import OnboardingService
from app.core.marketing_stack.services.strategy_service import StrategyService
from app.core.marketing_stack.services.content_service import ContentService
from app.core.marketing_stack.services.execution_service import ExecutionService
from app.core.marketing_stack.services.optimization_service import OptimizationService
from app.core.marketing_stack.services.lead_service import LeadService
from app.core.marketing_stack.services.attribution_service import AttributionService
from app.core.marketing_stack.services.orchestrator_service import OrchestratorService


# Every Repository That Is Used In this dependences

def get_client_repository(db: Session = Depends(get_db)) -> ClientRepositoryImpl:
    return ClientRepositoryImpl(db)


def get_conversation_repository(db: Session = Depends(get_db)) -> ConversationRepositoryImpl:
    return ConversationRepositoryImpl(db)


def get_strategy_repository(db: Session = Depends(get_db)) -> StrategyRepositoryImpl:
    return StrategyRepositoryImpl(db)


def get_content_repository(db: Session = Depends(get_db)) -> ContentRepositoryImpl:
    return ContentRepositoryImpl(db)


def get_campaign_repository(db: Session = Depends(get_db)) -> CampaignRepositoryImpl:
    return CampaignRepositoryImpl(db)


def get_lead_repository(db: Session = Depends(get_db)) -> LeadRepositoryImpl:
    return LeadRepositoryImpl(db)


def get_metrics_repository(db: Session = Depends(get_db)) -> MetricsRepositoryImpl:
    return MetricsRepositoryImpl(db)


def get_usage_repository(db: Session = Depends(get_db)) -> UsageRepositoryImpl:
    return UsageRepositoryImpl(db)


# ─── External Adapter Factories ─────────────────────────────────────

def get_ai_provider() -> ModelRouterAdapter:
    # Priority: Claude > Gemini > OpenRouter (free)
    # Use whatever keys are available

    primary = None
    fallback = None

    if app_config.anthropic_api_key:
        primary = ClaudeAdapter(
            api_key=app_config.anthropic_api_key,
            default_model=app_config.claude_default_model,
        )

    if app_config.gemini_api_key:
        gemini = GeminiAdapter(
            api_key=app_config.gemini_api_key,
            default_model=app_config.gemini_default_model,
        )
        if not primary:
            primary = gemini
        else:
            fallback = gemini

    if app_config.openrouter_api_key:
        openrouter = OpenRouterAdapter(
            api_key=app_config.openrouter_api_key,
            default_model=app_config.openrouter_default_model,
        )
        if not primary:
            primary = openrouter
        if not fallback:
            fallback = openrouter

    if not primary:
        raise RuntimeError("No AI provider configured. Set GEMINI_API_KEY or OPENROUTER_API_KEY in .env")

    if not fallback:
        fallback = primary

    return ModelRouterAdapter(claude_provider=primary, gemini_provider=fallback)


def get_messaging_port() -> WhatsAppAdapter:
    return WhatsAppAdapter(
        phone_number_id=app_config.whatsapp_phone_number_id,
        access_token=app_config.whatsapp_access_token,
    )


def get_web_scraper() -> BeautifulSoupScraper:
    return BeautifulSoupScraper()


def get_social_media_port() -> InstagramAdapter:
    return InstagramAdapter(
        business_account_id=app_config.instagram_business_account_id,
        access_token=app_config.instagram_access_token,
    )


def get_playbook_loader() -> JsonPlaybookAdapter:
    return JsonPlaybookAdapter(playbooks_dir="playbooks")


# ─── Service Factories ──────────────────────────────────────────────

def get_conversation_service(
    conversation_repo: ConversationRepositoryImpl = Depends(get_conversation_repository),
) -> ConversationService:
    return ConversationService(conversation_repository=conversation_repo)


def get_onboarding_service(
    client_repo: ClientRepositoryImpl = Depends(get_client_repository),
    ai_provider: ModelRouterAdapter = Depends(get_ai_provider),
    web_scraper: BeautifulSoupScraper = Depends(get_web_scraper),
    playbook_loader: JsonPlaybookAdapter = Depends(get_playbook_loader),
) -> OnboardingService:
    return OnboardingService(
        client_repository=client_repo,
        ai_provider=ai_provider,
        web_scraper=web_scraper,
        playbook_loader=playbook_loader,
    )


def get_strategy_service(
    strategy_repo: StrategyRepositoryImpl = Depends(get_strategy_repository),
    ai_provider: ModelRouterAdapter = Depends(get_ai_provider),
    playbook_loader: JsonPlaybookAdapter = Depends(get_playbook_loader),
) -> StrategyService:
    return StrategyService(
        strategy_repository=strategy_repo,
        ai_provider=ai_provider,
        playbook_loader=playbook_loader,
    )


def get_content_service(
    content_repo: ContentRepositoryImpl = Depends(get_content_repository),
    ai_provider: ModelRouterAdapter = Depends(get_ai_provider),
) -> ContentService:
    return ContentService(
        content_repository=content_repo,
        ai_provider=ai_provider,
    )


def get_execution_service(
    content_repo: ContentRepositoryImpl = Depends(get_content_repository),
    campaign_repo: CampaignRepositoryImpl = Depends(get_campaign_repository),
    messaging_port: WhatsAppAdapter = Depends(get_messaging_port),
    social_media_port: InstagramAdapter = Depends(get_social_media_port),
) -> ExecutionService:
    return ExecutionService(
        content_repository=content_repo,
        campaign_repository=campaign_repo,
        messaging_port=messaging_port,
        social_media_port=social_media_port,
    )


def get_optimization_service(
    metrics_repo: MetricsRepositoryImpl = Depends(get_metrics_repository),
    lead_repo: LeadRepositoryImpl = Depends(get_lead_repository),
    ai_provider: ModelRouterAdapter = Depends(get_ai_provider),
    messaging_port: WhatsAppAdapter = Depends(get_messaging_port),
) -> OptimizationService:
    return OptimizationService(
        metrics_repository=metrics_repo,
        lead_repository=lead_repo,
        ai_provider=ai_provider,
        messaging_port=messaging_port,
    )


def get_lead_service(
    lead_repo: LeadRepositoryImpl = Depends(get_lead_repository),
    messaging_port: WhatsAppAdapter = Depends(get_messaging_port),
) -> LeadService:
    return LeadService(
        lead_repository=lead_repo,
        messaging_port=messaging_port,
    )


def get_attribution_service(
    lead_repo: LeadRepositoryImpl = Depends(get_lead_repository),
    metrics_repo: MetricsRepositoryImpl = Depends(get_metrics_repository),
) -> AttributionService:
    return AttributionService(
        lead_repository=lead_repo,
        metrics_repository=metrics_repo,
    )


def get_orchestrator_service(
    client_repo: ClientRepositoryImpl = Depends(get_client_repository),
    onboarding: OnboardingService = Depends(get_onboarding_service),
    strategy: StrategyService = Depends(get_strategy_service),
    content: ContentService = Depends(get_content_service),
    execution: ExecutionService = Depends(get_execution_service),
    lead: LeadService = Depends(get_lead_service),
    attribution: AttributionService = Depends(get_attribution_service),
    conversation: ConversationService = Depends(get_conversation_service),
    messaging_port: WhatsAppAdapter = Depends(get_messaging_port),
) -> OrchestratorService:
    return OrchestratorService(
        client_repository=client_repo,
        onboarding_service=onboarding,
        strategy_service=strategy,
        content_service=content,
        execution_service=execution,
        lead_service=lead,
        attribution_service=attribution,
        conversation_service=conversation,
        messaging_port=messaging_port,
    )
