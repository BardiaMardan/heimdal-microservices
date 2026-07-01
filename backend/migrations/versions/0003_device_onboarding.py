"""device onboarding: ownership + claim codes

Revision ID: 0003_device_onboarding
Revises: 0002_create_users
Create Date: 2026-06-27

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003_device_onboarding"
down_revision: Union[str, None] = "0002_create_users"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("devices", sa.Column("owner_id", sa.Integer(), nullable=True))
    op.add_column("devices", sa.Column("hardware_id", sa.String(length=128), nullable=True))
    op.add_column("devices", sa.Column("device_token_hash", sa.String(length=64), nullable=True))
    op.add_column("devices", sa.Column("claimed_at", sa.DateTime(timezone=True), nullable=True))
    op.create_foreign_key(
        "fk_devices_owner_id_users",
        "devices",
        "users",
        ["owner_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_devices_owner_id", "devices", ["owner_id"])
    op.create_index("ix_devices_hardware_id", "devices", ["hardware_id"], unique=True)

    op.create_table(
        "device_claims",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("device_id", sa.Uuid(), nullable=False),
        sa.Column("code_hash", sa.String(length=64), nullable=False),
        sa.Column("provisioning_secret_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("attempts", sa.Integer(), server_default="0", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_device_claims_device_id", "device_claims", ["device_id"])
    op.create_index("ix_device_claims_code_hash", "device_claims", ["code_hash"])
    op.create_index(
        "uq_device_claims_one_active_per_device",
        "device_claims",
        ["device_id"],
        unique=True,
        postgresql_where=sa.text("consumed_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_index("uq_device_claims_one_active_per_device", table_name="device_claims")
    op.drop_index("ix_device_claims_code_hash", table_name="device_claims")
    op.drop_index("ix_device_claims_device_id", table_name="device_claims")
    op.drop_table("device_claims")

    op.drop_index("ix_devices_hardware_id", table_name="devices")
    op.drop_index("ix_devices_owner_id", table_name="devices")
    op.drop_constraint("fk_devices_owner_id_users", "devices", type_="foreignkey")
    op.drop_column("devices", "claimed_at")
    op.drop_column("devices", "device_token_hash")
    op.drop_column("devices", "hardware_id")
    op.drop_column("devices", "owner_id")
