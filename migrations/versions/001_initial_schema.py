"""Initial schema — all 8 tables for marketing-service.

Revision ID: 001
Revises: None
Create Date: 2026-04-13

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "marketing"


def upgrade() -> None:
    # Create schema
    op.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}")

    # 1. clients orm
    op.create_table(
        "clients",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("phone_number", sa.Text, unique=True, nullable=False, index=True),
        sa.Column("business_name", sa.Text),
        sa.Column("owner_name", sa.Text),
        sa.Column("sector", sa.Text, index=True),
        sa.Column("sub_sector", sa.Text),
        sa.Column("website_url", sa.Text),
        sa.Column("google_maps_url", sa.Text),
        sa.Column("instagram_handle", sa.Text),
        sa.Column("city", sa.Text, index=True),
        sa.Column("locality", sa.Text),
        sa.Column("language", sa.Text, server_default="english"),
        sa.Column("business_profile", JSONB, server_default="{}"),
        sa.Column("scraped_data", JSONB, server_default="{}"),
        sa.Column("onboarding_status", sa.Text, server_default="pending_questions", index=True),
        sa.Column("onboarding_answers", JSONB, server_default="{}"),
        sa.Column("current_question_index", sa.Integer, server_default="0"),
        sa.Column("subscription_tier", sa.Text, server_default="trial"),
        sa.Column("autonomy_level", sa.Text, server_default="supervised"),
        sa.Column("is_active", sa.Boolean, server_default="true", index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
        schema=SCHEMA,
    )

    # 2. conversations
    op.create_table(
        "conversations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("client_id", UUID(as_uuid=True), sa.ForeignKey(f"{SCHEMA}.clients.id"), index=True),
        sa.Column("phone_number", sa.Text, nullable=False, index=True),
        sa.Column("direction", sa.Text, nullable=False),
        sa.Column("message_type", sa.Text, server_default="text"),
        sa.Column("wa_message_id", sa.Text, unique=True, index=True),
        sa.Column("content", sa.Text, server_default=""),
        sa.Column("metadata", JSONB, server_default="{}"),
        sa.Column("context_type", sa.Text, server_default="onboarding"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema=SCHEMA,
    )

    # 3. strategies
    op.create_table(
        "strategies",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("client_id", UUID(as_uuid=True), sa.ForeignKey(f"{SCHEMA}.clients.id"), nullable=False, index=True),
        sa.Column("version", sa.Integer, server_default="1"),
        sa.Column("channels", JSONB, server_default="[]"),
        sa.Column("content_calendar", JSONB, server_default="[]"),
        sa.Column("kpis", JSONB, server_default="{}"),
        sa.Column("budget_allocation", JSONB, server_default="{}"),
        sa.Column("festival_campaigns", JSONB, server_default="[]"),
        sa.Column("playbook_id", sa.Text),
        sa.Column("ai_reasoning", sa.Text),
        sa.Column("status", sa.Text, server_default="draft", index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema=SCHEMA,
    )

    # 4. contents
    op.create_table(
        "contents",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("client_id", UUID(as_uuid=True), sa.ForeignKey(f"{SCHEMA}.clients.id"), nullable=False, index=True),
        sa.Column("strategy_id", UUID(as_uuid=True), sa.ForeignKey(f"{SCHEMA}.strategies.id"), index=True),
        sa.Column("channel", sa.Text, nullable=False, index=True),
        sa.Column("content_type", sa.Text, nullable=False),
        sa.Column("variant_group", sa.Text, index=True),
        sa.Column("variant_label", sa.Text, server_default="A"),
        sa.Column("caption", sa.Text, server_default=""),
        sa.Column("media_url", sa.Text),
        sa.Column("hashtags", ARRAY(sa.Text), server_default="{}"),
        sa.Column("cta_text", sa.Text),
        sa.Column("cta_url", sa.Text),
        sa.Column("coupon_code", sa.Text),
        sa.Column("utm_params", sa.Text),
        sa.Column("language", sa.Text, server_default="english"),
        sa.Column("ai_model_used", sa.Text),
        sa.Column("risk_level", sa.Text, server_default="low"),
        sa.Column("status", sa.Text, server_default="draft", index=True),
        sa.Column("scheduled_for", sa.DateTime(timezone=True)),
        sa.Column("published_at", sa.DateTime(timezone=True)),
        sa.Column("platform_post_id", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema=SCHEMA,
    )

    # 5. campaigns
    op.create_table(
        "campaigns",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("client_id", UUID(as_uuid=True), sa.ForeignKey(f"{SCHEMA}.clients.id"), nullable=False, index=True),
        sa.Column("content_id", UUID(as_uuid=True), sa.ForeignKey(f"{SCHEMA}.contents.id"), index=True),
        sa.Column("channel", sa.Text, nullable=False, index=True),
        sa.Column("campaign_type", sa.Text, nullable=False),
        sa.Column("status", sa.Text, server_default="scheduled", index=True),
        sa.Column("platform_id", sa.Text),
        sa.Column("target_audience", JSONB, server_default="{}"),
        sa.Column("budget", sa.Numeric(precision=12, scale=2)),
        sa.Column("start_date", sa.Date),
        sa.Column("end_date", sa.Date),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
        schema=SCHEMA,
    )

    # 6. leads
    op.create_table(
        "leads",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("client_id", UUID(as_uuid=True), sa.ForeignKey(f"{SCHEMA}.clients.id"), nullable=False, index=True),
        sa.Column("campaign_id", UUID(as_uuid=True), sa.ForeignKey(f"{SCHEMA}.campaigns.id"), nullable=True, index=True),
        sa.Column("name", sa.Text),
        sa.Column("phone_number", sa.Text, nullable=False, index=True),
        sa.Column("source_channel", sa.Text, nullable=False, index=True),
        sa.Column("source_campaign_tag", sa.Text),
        sa.Column("status", sa.Text, server_default="new", index=True),
        sa.Column("notes", sa.Text),
        sa.Column("revenue_amount", sa.Numeric(precision=12, scale=2)),
        sa.Column("payment_verified", sa.Boolean, server_default="false"),
        sa.Column("followup_count", sa.Integer, server_default="0"),
        sa.Column("last_followup_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
        schema=SCHEMA,
    )

    # 7. daily_metrics
    op.create_table(
        "daily_metrics",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("client_id", UUID(as_uuid=True), sa.ForeignKey(f"{SCHEMA}.clients.id"), nullable=False, index=True),
        sa.Column("date", sa.Date, nullable=False, index=True),
        sa.Column("channel", sa.Text, nullable=False, index=True),
        sa.Column("impressions", sa.Integer, server_default="0"),
        sa.Column("reach", sa.Integer, server_default="0"),
        sa.Column("engagement", sa.Integer, server_default="0"),
        sa.Column("clicks", sa.Integer, server_default="0"),
        sa.Column("leads_count", sa.Integer, server_default="0"),
        sa.Column("revenue", sa.Numeric(precision=12, scale=2), server_default="0"),
        sa.Column("spend", sa.Numeric(precision=12, scale=2), server_default="0"),
        sa.Column("followers_gained", sa.Integer, server_default="0"),
        sa.Column("messages_sent", sa.Integer, server_default="0"),
        sa.Column("messages_delivered", sa.Integer, server_default="0"),
        sa.Column("messages_read", sa.Integer, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("client_id", "date", "channel", name="uq_client_date_channel"),
        schema=SCHEMA,
    )

    # 8. usage_events
    op.create_table(
        "usage_events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("client_id", UUID(as_uuid=True), sa.ForeignKey(f"{SCHEMA}.clients.id"), nullable=False, index=True),
        sa.Column("event_type", sa.Text, nullable=False, index=True),
        sa.Column("model_used", sa.Text),
        sa.Column("tokens_input", sa.Integer, server_default="0"),
        sa.Column("tokens_output", sa.Integer, server_default="0"),
        sa.Column("cost_usd", sa.Numeric(precision=10, scale=6), server_default="0"),
        sa.Column("metadata", JSONB, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), index=True),
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_table("usage_events", schema=SCHEMA)
    op.drop_table("daily_metrics", schema=SCHEMA)
    op.drop_table("leads", schema=SCHEMA)
    op.drop_table("campaigns", schema=SCHEMA)
    op.drop_table("contents", schema=SCHEMA)
    op.drop_table("strategies", schema=SCHEMA)
    op.drop_table("conversations", schema=SCHEMA)
    op.drop_table("clients", schema=SCHEMA)
    op.execute(f"DROP SCHEMA IF EXISTS {SCHEMA}")
