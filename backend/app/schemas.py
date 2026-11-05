from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    nickname: str = Field(min_length=1, max_length=40)

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

class CommentIn(BaseModel):
    article_slug: str = Field(min_length=1, max_length=180, pattern=r"^[a-zA-Z0-9/_-]+$")
    content: str = Field(min_length=1, max_length=5000)
    parent_id: int | None = None

class ProfileUpdate(BaseModel):
    nickname: str = Field(min_length=1, max_length=40)
