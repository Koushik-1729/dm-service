"""Add user, identity, and event foundation tables.

Revision ID: 002
Revises: 001
Create Date: 2026-04-17
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID


revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "marketing"


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("client_id", UUID(as_uuid=True), sa.ForeignKey(f"{SCHEMA}.clients.id"), nullable=False, index=True),
        sa.Column("external_ref", sa.Text, index=True),
        sa.Column("email", sa.Text, index=True),
        sa.Column("phone_number", sa.Text, index=True),
        sa.Column("first_name", sa.Text),
        sa.Column("last_name", sa.Text),
        sa.Column("status", sa.Text, server_default="active", index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
        schema=SCHEMA,
    )

    op.create_table(
        "user_identities",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("client_id", UUID(as_uuid=True), sa.ForeignKey(f"{SCHEMA}.clients.id"), nullable=False, index=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey(f"{SCHEMA}.users.id"), nullable=False, index=True),
        sa.Column("identity_type", sa.Text, nullable=False, index=True),
        sa.Column("identity_value", sa.Text, nullable=False, index=True),
        sa.Column("is_primary", sa.Boolean, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("client_id", "identity_type", "identity_value", name="uq_user_identity_key"),
        schema=SCHEMA,
    )

    op.create_table(
        "marketing_events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("client_id", UUID(as_uuid=True), sa.ForeignKey(f"{SCHEMA}.clients.id"), nullable=False, index=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey(f"{SCHEMA}.users.id"), index=True),
        sa.Column("event_type", sa.Text, nullable=False, index=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column("channel", sa.Text, index=True),
        sa.Column("campaign_id", sa.Text, index=True),
        sa.Column("adset_id", sa.Text),
        sa.Column("creative_id", sa.Text),
        sa.Column("message_id", sa.Text, index=True),
        sa.Column("session_id", sa.Text, index=True),
        sa.Column("source_id", sa.Text, index=True),
        sa.Column("revenue_amount", sa.Numeric(precision=12, scale=2)),
        sa.Column("currency", sa.Text, server_default="INR"),
        sa.Column("metadata", JSONB, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema=SCHEMA,
    )

    op.create_table(
        "conversion_events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("client_id", UUID(as_uuid=True), sa.ForeignKey(f"{SCHEMA}.clients.id"), nullable=False, index=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey(f"{SCHEMA}.users.id"), nullable=False, index=True),
        sa.Column("marketing_event_id", UUID(as_uuid=True), sa.ForeignKey(f"{SCHEMA}.marketing_events.id"), index=True),
        sa.Column("conversion_type", sa.Text, nullable=False, index=True),
        sa.Column("conversion_value", sa.Numeric(precision=12, scale=2)),
        sa.Column("currency", sa.Text, server_default="INR"),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema=SCHEMA,
    )

    op.create_table(
        "revenue_events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("client_id", UUID(as_uuid=True), sa.ForeignKey(f"{SCHEMA}.clients.id"), nullable=False, index=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey(f"{SCHEMA}.users.id"), nullable=False, index=True),
        sa.Column("conversion_event_id", UUID(as_uuid=True), sa.ForeignKey(f"{SCHEMA}.conversion_events.id"), index=True),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("currency", sa.Text, server_default="INR"),
        sa.Column("payment_reference", sa.Text, index=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_table("revenue_events", schema=SCHEMA)
    op.drop_table("conversion_events", schema=SCHEMA)
    op.drop_table("marketing_events", schema=SCHEMA)
    op.drop_table("user_identities", schema=SCHEMA)
    op.drop_table("users", schema=SCHEMA)
