from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, JSON, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base

def now_utc():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    nickname: Mapped[str] = mapped_column(String(40))
    password_hash: Mapped[str] = mapped_column(String(255))
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="user", server_default="user", nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)

class UserSession(Base):
    __tablename__ = "user_sessions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

class Comment(Base):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    article_slug: Mapped[str] = mapped_column(String(180), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("comments.id", ondelete="CASCADE"), nullable=True)
    content: Mapped[str] = mapped_column(Text)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, index=True)
    user = relationship("User")
    parent = relationship("Comment", remote_side="Comment.id", foreign_keys=[parent_id], back_populates="replies")
    replies = relationship("Comment", foreign_keys=[parent_id], back_populates="parent", cascade="all, delete-orphan", single_parent=True)

class ArticleLike(Base):
    __tablename__ = "article_likes"
    __table_args__ = (UniqueConstraint("article_slug", "user_id", name="uq_article_like_user"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    article_slug: Mapped[str] = mapped_column(String(180), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

class ArticleBookmark(Base):
    __tablename__ = "article_bookmarks"
    __table_args__ = (UniqueConstraint("article_slug", "user_id", name="uq_article_bookmark_user"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    article_slug: Mapped[str] = mapped_column(String(180), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class GuestbookMessage(Base):
    __tablename__ = "guestbook_messages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    content: Mapped[str] = mapped_column(Text)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, index=True)
    user = relationship("User")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    actor_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(80), nullable=False)
    target_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False, index=True)
    actor = relationship("User")



content_categories = Table(
    "content_categories",
    Base.metadata,
    Column("content_id", ForeignKey("content_items.id", ondelete="CASCADE"), primary_key=True),
    Column("category_id", ForeignKey("content_categories_lookup.id", ondelete="CASCADE"), primary_key=True),
)

content_tags = Table(
    "content_tags",
    Base.metadata,
    Column("content_id", ForeignKey("content_items.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("content_tags_lookup.id", ondelete="CASCADE"), primary_key=True),
)


class ContentCategory(Base):
    __tablename__ = "content_categories_lookup"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(300), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)


class ContentTag(Base):
    __tablename__ = "content_tags_lookup"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)


class ContentItem(Base):
    __tablename__ = "content_items"
    __table_args__ = (UniqueConstraint("kind", "slug", name="uq_content_kind_slug"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    kind: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(180), nullable=False)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    summary: Mapped[str] = mapped_column(String(600), default="", nullable=False)
    content: Mapped[str] = mapped_column(Text, default="", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="draft", server_default="draft", nullable=False, index=True)
    featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cover_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    github_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc, nullable=False)
    categories = relationship("ContentCategory", secondary=content_categories, lazy="selectin")
    tags = relationship("ContentTag", secondary=content_tags, lazy="selectin")


class MediaAsset(Base):
    __tablename__ = "media_assets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    public_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    alt_text: Mapped[str] = mapped_column(String(300), default="", nullable=False)
    uploaded_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False, index=True)


class SiteSetting(Base):
    __tablename__ = "site_settings"
    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    updated_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc, nullable=False)
