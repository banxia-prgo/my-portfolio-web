"""Create CMS content and media tables.

Revision ID: 0004_cms_content
Revises: 0003_roles_audit

The legacy 0001 revision uses metadata.create_all on fresh installs. Use
checkfirst so this revision also works on those databases while adding the
tables to existing installations.
"""
from alembic import op
from app.db import Base
from app import models  # noqa: F401

revision = "0004_cms_content"
down_revision = "0003_roles_audit"
branch_labels = None
depends_on = None

TABLES = (
    "content_categories_lookup",
    "content_tags_lookup",
    "content_items",
    "content_categories",
    "content_tags",
    "media_assets",
    "site_settings",
)


def upgrade():
    bind = op.get_bind()
    for name in TABLES:
        Base.metadata.tables[name].create(bind=bind, checkfirst=True)


def downgrade():
    bind = op.get_bind()
    for name in reversed(TABLES):
        Base.metadata.tables[name].drop(bind=bind, checkfirst=True)
