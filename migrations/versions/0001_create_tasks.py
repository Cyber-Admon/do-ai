"""create tasks table

Revision ID: 0001
Revises:
Create Date: 2026-10-04
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("clickup_id", sa.String(64), nullable=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(100), nullable=True),
        sa.Column(
            "assignees",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "source", sa.String(20), nullable=False, server_default="clickup"
        ),
        sa.Column("url", sa.String(500), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_tasks_clickup_id", "tasks", ["clickup_id"], unique=True)
    op.create_index("ix_tasks_due_at", "tasks", ["due_at"])


def downgrade() -> None:
    op.drop_index("ix_tasks_due_at", table_name="tasks")
    op.drop_index("ix_tasks_clickup_id", table_name="tasks")
    op.drop_table("tasks")