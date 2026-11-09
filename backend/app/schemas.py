from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator

class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    nickname: str = Field(min_length=1, max_length=40)

    @field_validator("nickname")
    @classmethod
    def normalize_nickname(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("昵称不能为空")
        return normalized

class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    nickname: str
    avatar_url: str | None
    created_at: datetime
    role: str = "user"

class CommentIn(BaseModel):
    article_slug: str = Field(min_length=1, max_length=180, pattern=r"^[a-zA-Z0-9/_-]+$")
    content: str = Field(min_length=1, max_length=5000)
    parent_id: int | None = None

    @field_validator("content")
    @classmethod
    def normalize_content(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("评论内容不能为空")
        return normalized

class ProfileUpdate(BaseModel):
    nickname: str = Field(min_length=1, max_length=40)

    @field_validator("nickname")
    @classmethod
    def normalize_nickname(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("昵称不能为空")
        return normalized


class GuestbookMessageIn(BaseModel):
    content: str = Field(min_length=1, max_length=2000)

    @field_validator("content")
    @classmethod
    def normalize_guestbook_content(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("留言内容不能为空")
        return normalized


class AdminUserUpdate(BaseModel):
    is_active: bool | None = None
    role: str | None = Field(default=None, pattern=r"^(user|admin)$")

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str | None) -> str | None:
        if value is not None and value not in {"user", "admin"}:
            raise ValueError("角色只能是 user 或 admin")
        return value



class ContentCreate(BaseModel):
    kind: str = Field(pattern=r"^(post|project)$")
    slug: str = Field(min_length=1, max_length=180, pattern=r"^[a-zA-Z0-9\u4e00-\u9fff/_-]+$")
    title: str = Field(min_length=1, max_length=240)
    summary: str = Field(default="", max_length=600)
    content: str = Field(default="", max_length=200000)
    status: str = Field(default="draft", pattern=r"^(draft|published|archived)$")
    featured: bool = False
    sort_order: int = 0
    cover_url: str | None = Field(default=None, max_length=1000)
    github_url: str | None = Field(default=None, max_length=1000)
    category_ids: list[int] = Field(default_factory=list, max_length=20)
    tag_ids: list[int] = Field(default_factory=list, max_length=30)

    @field_validator("slug", "title")
    @classmethod
    def trim_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("该字段不能为空")
        return value


class ContentUpdate(BaseModel):
    slug: str | None = Field(default=None, min_length=1, max_length=180, pattern=r"^[a-zA-Z0-9\u4e00-\u9fff/_-]+$")
    title: str | None = Field(default=None, min_length=1, max_length=240)
    summary: str | None = Field(default=None, max_length=600)
    content: str | None = Field(default=None, max_length=200000)
    status: str | None = Field(default=None, pattern=r"^(draft|published|archived)$")
    featured: bool | None = None
    sort_order: int | None = None
    cover_url: str | None = Field(default=None, max_length=1000)
    github_url: str | None = Field(default=None, max_length=1000)
    category_ids: list[int] | None = Field(default=None, max_length=20)
    tag_ids: list[int] | None = Field(default=None, max_length=30)


class TaxonomyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    slug: str = Field(min_length=1, max_length=100, pattern=r"^[a-zA-Z0-9\u4e00-\u9fff_-]+$")
    description: str | None = Field(default=None, max_length=300)


class SiteSettingUpdate(BaseModel):
    value: dict
