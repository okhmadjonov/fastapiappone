from fastapi import APIRouter, Depends
from app.domain.models import User
from app.schemas.user_schemas import UserResponseDto
from app.services.user_service import UserService
from app.api.deps import get_user_service, get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserResponseDto)
async def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    """
    [Authorize] orqali himoyalangan endpoint.
    Faqat yaroqli Bearer tokeni bo'lgan foydalanuvchi o'z profilini ko'ra oladi.
    """
    return current_user

@router.get("/", response_model=list[UserResponseDto])
async def get_all_users(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),  # [Authorize]
    user_service: UserService = Depends(get_user_service)
):
    """Barcha foydalanuvchilar ro'yxatini olish (faqat tizimga kirganlar uchun)"""
    return await user_service.get_all(skip=skip, limit=limit)
