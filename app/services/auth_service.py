from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from fastapi import HTTPException, status
from app.services.user_service import UserService
from app.schemas.user_schemas import UserLoginDto, TokenResponseDto
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token
from app.core.config import settings
from app.domain.models import RefreshToken

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_service = UserService(db)

    async def _save_refresh_token(self, user_id: int, token_str: str):
        """Bazada refresh tokenni saqlash (Logout va xavfsizlik uchun)"""
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        db_token = RefreshToken(
            user_id=user_id,
            token=token_str,
            expires_at=expires_at,
            revoked=False
        )
        self.db.add(db_token)
        await self.db.commit()

    async def authenticate(self, dto: UserLoginDto) -> TokenResponseDto:
        user = await self.user_service.get_by_email(dto.email)
        if not user or not verify_password(dto.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email yoki parol noto'g'ri",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Foydalanuvchi hisobi faol emas"
            )

        access_token = create_access_token(user.id, {"email": user.email, "role": user.role})
        refresh_token = create_refresh_token(user.id)

        # Refresh tokenni bazaga yozib qo'yamiz
        await self._save_refresh_token(user.id, refresh_token)

        return TokenResponseDto(
            access_token=access_token,
            refresh_token=refresh_token
        )

    async def refresh_access_token(self, refresh_token: str) -> TokenResponseDto:
        # 1. JWT imzosini tekshirish
        payload = decode_token(refresh_token, is_refresh=True)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token yaroqsiz yoki muddati o'tgan"
            )

        # 2. Bazadan tokenni qidirish va bekor qilinmaganligini (Revoked) tekshirish
        query = select(RefreshToken).where(
            RefreshToken.token == refresh_token,
            RefreshToken.revoked == False
        )
        result = await self.db.scalars(query)
        db_token = result.first()

        if not db_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token bekor qilingan (Logout bo'lgan) yoki topilmadi"
            )

        user_id = int(payload.get("sub"))
        user = await self.user_service.get_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Foydalanuvchi topilmadi yoki bloklangan"
            )

        # 3. Eski tokenni bekor qilamiz (Token Rotation xavfsizlik standarti)
        db_token.revoked = True

        # 4. Yangi tokenlar juftligi
        new_access_token = create_access_token(user.id, {"email": user.email, "role": user.role})
        new_refresh_token = create_refresh_token(user.id)
        
        # Yangi tokenni bazaga saqlaymiz
        await self._save_refresh_token(user.id, new_refresh_token)

        return TokenResponseDto(
            access_token=new_access_token,
            refresh_token=new_refresh_token
        )

    async def logout(self, refresh_token: str) -> dict:
        """Foydalanuvchini tizimdan chiqarish (Logout) - tokenni bekor qilish"""
        query = select(RefreshToken).where(RefreshToken.token == refresh_token)
        result = await self.db.scalars(query)
        db_token = result.first()

        if db_token:
            db_token.revoked = True
            await self.db.commit()

        return {"message": "Muvaffaqiyatli tizimdan chiqildi (Logout)"}
