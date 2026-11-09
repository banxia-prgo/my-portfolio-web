"""Add guestbook messages.

Revision ID: 0002_guestbook
Revises: 0001_initial
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_guestbook"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "guestbook_messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_guestbook_messages_user_id", "guestbook_messages", ["user_id"])
    op.create_index("ix_guestbook_messages_created_at", "guestbook_messages", ["created_at"])


def downgrade():
    op.drop_index("ix_guestbook_messages_created_at", table_name="guestbook_messages")
    op.drop_index("ix_guestbook_messages_user_id", table_name="guestbook_messages")
    op.drop_table("guestbook_messages")
