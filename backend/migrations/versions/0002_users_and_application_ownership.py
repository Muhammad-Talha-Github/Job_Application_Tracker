"""Create users and attach each existing application to its designated owner.

Revision ID: 0002_users_and_application_ownership
Revises: 0001_create_applications
"""
import os
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from argon2 import PasswordHasher


revision: str = "0002_user_ownership"
down_revision: Union[str, None] = "0001_create_applications"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("email"),
    )

    # Add as nullable so existing rows can be backfilled before enforcing ownership.
    op.add_column("applications", sa.Column("user_id", sa.Integer(), nullable=True))
    connection = op.get_bind()
    existing_count = connection.execute(
        sa.text("SELECT count(*) FROM applications")
    ).scalar_one()

    if existing_count:
        # The operator designates the owner locally; no existing job row is discarded.
        email = os.getenv("LEGACY_OWNER_EMAIL", "").strip().lower()
        password = os.getenv("LEGACY_OWNER_PASSWORD", "")
        if not email or len(password) < 12:
            raise RuntimeError(
                "Existing applications need LEGACY_OWNER_EMAIL and a 12+ character "
                "LEGACY_OWNER_PASSWORD in backend/.env before this migration."
            )

        users = sa.table(
            "users",
            sa.column("id", sa.Integer),
            sa.column("email", sa.String),
            sa.column("password_hash", sa.Text),
        )
        owner_id = connection.execute(
            sa.insert(users)
            .values(email=email, password_hash=PasswordHasher().hash(password))
            .returning(users.c.id)
        ).scalar_one()
        connection.execute(
            sa.text("UPDATE applications SET user_id = :owner_id"),
            {"owner_id": owner_id},
        )

    op.alter_column("applications", "user_id", nullable=False)
    op.create_foreign_key(
        "fk_applications_user_id_users",
        "applications",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index("ix_applications_user_id", "applications", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_applications_user_id", table_name="applications")
    op.drop_constraint("fk_applications_user_id_users", "applications", type_="foreignkey")
    op.drop_column("applications", "user_id")
    op.drop_table("users")
