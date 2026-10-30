from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.services.user_service import UserService
from app.schemas.user_schemas import UserLoginDto, TokenResponseDto
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_service = UserService(db)

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

        access_token = create_access_token(user.id, {"email": user.email})
        refresh_token = create_refresh_token(user.id)

        return TokenResponseDto(
            access_token=access_token,
            refresh_token=refresh_token
        )

    async def refresh_access_token(self, refresh_token: str) -> TokenResponseDto:
        payload = decode_token(refresh_token, is_refresh=True)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token yaroqsiz yoki muddati o'tgan"
            )

        user_id = int(payload.get("sub"))
        user = await self.user_service.get_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Foydalanuvchi topilmadi yoki bloklangan"
            )

        new_access_token = create_access_token(user.id, {"email": user.email})
        new_refresh_token = create_refresh_token(user.id)

        return TokenResponseDto(
            access_token=new_access_token,
            refresh_token=new_refresh_token
        )
