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
    return [table for table in Base.metadata.sorted_tables if table.name not in {"guestbook_messages", "audit_logs", "content_categories_lookup", "content_tags_lookup", "content_items", "content_categories", "content_tags", "media_assets", "site_settings"}]


def upgrade():
    Base.metadata.create_all(bind=op.get_bind(), tables=_legacy_tables())


def downgrade():
    Base.metadata.drop_all(bind=op.get_bind(), tables=_legacy_tables())
