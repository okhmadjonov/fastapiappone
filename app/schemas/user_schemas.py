from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

# User Registration DTO
class UserRegisterDto(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6, max_length=100)
    age: int | None = Field(default=None, ge=18, le=120)

# User Login DTO (email yoki username qabul qiladi)
class UserLoginDto(BaseModel):
    email: str
    password: str

# Token Response DTO
class TokenResponseDto(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

# Refresh Request DTO
class RefreshTokenDto(BaseModel):
    refresh_token: str

# User Response DTO (Clientga parol hech qachon chiqmaydi)
class UserResponseDto(BaseModel):
    id: int
    name: str
    email: EmailStr
    age: int | None = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
