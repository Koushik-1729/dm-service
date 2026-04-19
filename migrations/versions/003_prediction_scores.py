"""Add prediction score snapshots.

Revision ID: 003
Revises: 002
Create Date: 2026-04-17
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID


revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "marketing"


def upgrade() -> None:
    op.create_table(
        "prediction_scores",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("client_id", UUID(as_uuid=True), sa.ForeignKey(f"{SCHEMA}.clients.id"), nullable=False, index=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey(f"{SCHEMA}.users.id"), nullable=False, index=True),
        sa.Column("model_name", sa.Text, nullable=False, index=True),
        sa.Column("conversion_probability", sa.Float, nullable=False, server_default="0"),
        sa.Column("dropout_risk", sa.Float, nullable=False, server_default="0"),
        sa.Column("expected_revenue", sa.Numeric(precision=12, scale=2), nullable=False, server_default="0"),
        sa.Column("feature_snapshot", JSONB, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), index=True),
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_table("prediction_scores", schema=SCHEMA)
