"""create telemetry table

Revision ID: 0004_create_telemetry
Revises: 0003_device_onboarding
Create Date: 2026-07-02

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004_create_telemetry"
down_revision: Union[str, None] = "0003_device_onboarding"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "telemetry",
        sa.Column("device_id", sa.Uuid(), nullable=False),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "ingested_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"], ondelete="CASCADE"),
        # (device_id, ts) is the idempotency key and a Timescale-ready layout.
        sa.PrimaryKeyConstraint("device_id", "ts"),
    )
    # Newest-first reads per device: latest reading and bounded time ranges.
    op.create_index(
        "ix_telemetry_device_id_ts_desc",
        "telemetry",
        ["device_id", sa.text("ts DESC")],
    )


def downgrade() -> None:
    op.drop_index("ix_telemetry_device_id_ts_desc", table_name="telemetry")
    op.drop_table("telemetry")
