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
