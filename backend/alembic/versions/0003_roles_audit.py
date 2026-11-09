"""Ensure user roles and administrator audit logs exist.

Revision ID: 0003_roles_audit
Revises: 0002_guestbook

The initial migration creates tables from current ORM metadata on a fresh
installation. Therefore role/audit_logs may already exist on a fresh database,
while an older deployed database may not have them yet.
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_roles_audit"
down_revision = "0002_guestbook"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "users" in tables:
        user_columns = {column["name"] for column in inspector.get_columns("users")}
        if "role" not in user_columns:
            op.add_column(
                "users",
                sa.Column("role", sa.String(length=20), nullable=False, server_default="user"),
            )
        user_indexes = {index["name"] for index in sa.inspect(bind).get_indexes("users")}
        if "ix_users_role" not in user_indexes:
            op.create_index("ix_users_role", "users", ["role"])

    if "audit_logs" not in tables:
        op.create_table(
            "audit_logs",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("actor_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
            sa.Column("action", sa.String(length=100), nullable=False),
            sa.Column("target_type", sa.String(length=80), nullable=False),
            sa.Column("target_id", sa.String(length=80), nullable=True),
            sa.Column("detail", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        )

    audit_indexes = {index["name"] for index in sa.inspect(bind).get_indexes("audit_logs")}
    for name, columns in (
        ("ix_audit_logs_actor_user_id", ["actor_user_id"]),
        ("ix_audit_logs_action", ["action"]),
        ("ix_audit_logs_created_at", ["created_at"]),
    ):
        if name not in audit_indexes:
            op.create_index(name, "audit_logs", columns)


def downgrade():
    # Keep this migration non-destructive: on fresh databases these schema
    # objects may have been created by the legacy metadata-driven 0001 revision.
    pass
