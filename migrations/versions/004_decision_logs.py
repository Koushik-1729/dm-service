"""Add decision log table.

Revision ID: 004
Revises: 003
Create Date: 2026-04-17
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID


revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "marketing"


def upgrade() -> None:
    op.create_table(
        "decision_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("client_id", UUID(as_uuid=True), sa.ForeignKey(f"{SCHEMA}.clients.id"), nullable=False, index=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey(f"{SCHEMA}.users.id"), nullable=False, index=True),
        sa.Column("prediction_score_id", UUID(as_uuid=True), sa.ForeignKey(f"{SCHEMA}.prediction_scores.id"), index=True),
        sa.Column("action_type", sa.Text, nullable=False, index=True),
        sa.Column("action_payload", JSONB, server_default="{}"),
        sa.Column("confidence", sa.Float, nullable=False, server_default="0"),
        sa.Column("expected_revenue_impact", sa.Numeric(precision=12, scale=2), nullable=False, server_default="0"),
        sa.Column("reason", sa.Text, nullable=False),
        sa.Column("status", sa.Text, nullable=False, server_default="recommended", index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), index=True),
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_table("decision_logs", schema=SCHEMA)
