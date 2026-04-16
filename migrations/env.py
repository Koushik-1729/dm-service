from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context

from app.config.app_config import app_config
from app.infra.marketing_stack.models import MarketingBase

# here all this will auto detect in alembic
from app.infra.marketing_stack.models.client_entity import ClientEntity
from app.infra.marketing_stack.models.conversation_entity import ConversationEntity
from app.infra.marketing_stack.models.strategy_entity import StrategyEntity
from app.infra.marketing_stack.models.content_entity import ContentEntity
from app.infra.marketing_stack.models.campaign_entity import CampaignEntity
from app.infra.marketing_stack.models.lead_entity import LeadEntity
from app.infra.marketing_stack.models.daily_metrics_entity import DailyMetricsEntity
from app.infra.marketing_stack.models.usage_entity import UsageEntity

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = MarketingBase.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=app_config.db_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(app_config.db_url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table_schema="marketing",
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
