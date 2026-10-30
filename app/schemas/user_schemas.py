from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

# ----------------- User DTOs -----------------

class UserRegisterDto(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6, max_length=100)
    age: int | None = Field(default=None, ge=18, le=120)
    role: str = Field(default="user", pattern="^(user|admin)$")

class UserLoginDto(BaseModel):
    email: str
    password: str

class TokenResponseDto(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshTokenDto(BaseModel):
    refresh_token: str

class LogoutDto(BaseModel):
    refresh_token: str

# ----------------- Post DTOs -----------------

class PostCreateDto(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    content: str = Field(min_length=5)

class PostResponseDto(BaseModel):
    id: int
    title: str
    content: str
    author_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# ----------------- User Response DTOs -----------------

class UserResponseDto(BaseModel):
    id: int
    name: str
    email: EmailStr
    age: int | None = None
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class UserWithPostsResponseDto(UserResponseDto):
    posts: list[PostResponseDto] = []

    class Config:
        from_attributes = True
