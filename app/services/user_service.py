from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.domain.models import User
from app.schemas.user_schemas import UserRegisterDto
from app.core.security import hash_password

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.db.scalars(select(User).where(User.id == user_id))
        return result.first()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.scalars(select(User).where(User.email == email))
        return result.first()

    async def get_all(self, skip: int = 0, limit: int = 50) -> list[User]:
        result = await self.db.scalars(select(User).offset(skip).limit(limit))
        return list(result.all())

    async def register(self, dto: UserRegisterDto) -> User:
        # Email bandligini tekshirish
        existing = await self.get_by_email(dto.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ushbu email bilan foydalanuvchi allaqachon mavjud"
            )
        
        user = User(
            name=dto.name,
            email=dto.email,
            hashed_password=hash_password(dto.password),
            age=dto.age
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
