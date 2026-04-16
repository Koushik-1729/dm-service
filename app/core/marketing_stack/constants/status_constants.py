class OnboardingStatus:
    PENDING_QUESTIONS = "pending_questions"
    AWAITING_URL = "awaiting_url"
    PROFILING = "profiling"
    COMPLETE = "complete"


class StrategyStatus:
    DRAFT = "draft"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    ACTIVE = "active"
    ARCHIVED = "archived"


class ContentStatus:
    DRAFT = "draft"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
    ARCHIVED = "archived"


class CampaignStatus:
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class LeadStatus:
    NEW = "new"
    NOTIFIED = "notified"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    CONVERTED = "converted"
    LOST = "lost"


class SubscriptionTier:
    TRIAL = "trial"
    STARTER = "starter"
    GROWTH = "growth"
    SCALE = "scale"


class RiskLevel:
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    BLOCKED = "blocked"


class AutonomyLevel:
    SUPERVISED = "supervised"
    ASSISTED = "assisted"
    AUTONOMOUS = "autonomous"


class ConversationDirection:
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class ConversationContextType:
    ONBOARDING = "onboarding"
    APPROVAL = "approval"
    REPORT = "report"
    LEAD_FOLLOWUP = "lead_followup"
    SUPPORT = "support"
    REVENUE_CHECK = "revenue_check"
