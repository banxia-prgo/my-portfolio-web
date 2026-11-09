"""Initial interactive website schema.

Revision ID: 0001_initial
Revises:
"""
from alembic import op
from app.db import Base
from app import models  # noqa: F401

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def _legacy_tables():
    # Keep the original migration stable as newer models are added.
    return [table for table in Base.metadata.sorted_tables if table.name != "guestbook_messages"]


def upgrade():
    Base.metadata.create_all(bind=op.get_bind(), tables=_legacy_tables())


def downgrade():
    Base.metadata.drop_all(bind=op.get_bind(), tables=_legacy_tables())
