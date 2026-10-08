"""Create the applications table.

Revision ID: 0001_create_applications
Revises:
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001_create_applications"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "applications",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("company", sa.Text(), nullable=False),
        sa.Column("position", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("application_date", sa.Date(), nullable=False),
        sa.Column("job_url", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("applications")
