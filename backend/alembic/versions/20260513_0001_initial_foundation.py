"""initial foundation schema

Revision ID: 20260513_0001
Revises:
Create Date: 2026-05-13
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260513_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Foundation migration marker. Full autogeneration will be refreshed in STEP 003
    # after auth/user schemas are finalized. Models are already defined in code.
    pass


def downgrade() -> None:
    pass
