from fastapi import APIRouter, Depends
from app.domain.models import User
from app.schemas.user_schemas import UserResponseDto, UserWithPostsResponseDto
from app.services.user_service import UserService
from app.services.post_service import PostService
from app.api.deps import get_user_service, get_post_service, get_current_user, RoleChecker

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserResponseDto)
async def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    """
    [Authorize] orqali himoyalangan endpoint.
    Faqat yaroqli Bearer tokeni bo'lgan foydalanuvchi o'z profilini ko'radi.
    """
    return current_user

@router.get("/{user_id}/with-posts", response_model=UserWithPostsResponseDto)
async def get_user_with_posts(
    user_id: int,
    post_service: PostService = Depends(get_post_service)
):
    """
    1-to-Many Bog'lanish va Eager Loading namoyishi.
    selectinload (EF Core .Include) orqali N+1 muammosiz user va uning postlarini oladi.
    """
    return await post_service.get_user_with_posts_eager(user_id)

@router.get("/", response_model=list[UserResponseDto])
async def get_all_users(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """Barcha foydalanuvchilar ro'yxati (Tizimga kirganlar uchun)"""
    return await user_service.get_all(skip=skip, limit=limit)

@router.get("/admin/dashboard")
async def admin_only_dashboard(
    admin_user: User = Depends(RoleChecker(["admin"]))  # [Authorize(Roles = "admin")]
):
    """
    RBAC (Role Based Access Control) namunasi:
    Faqat 'admin' roliga ega bo'lgan foydalanuvchilar kira oladi. Oddiy 'user' ga 403 Forbidden qaytadi.
    """
    return {
        "message": f"Xush kelibsiz Admin, {admin_user.name}!",
        "admin_secret_data": "Maxfiy korxona hisobotlari..."
    }
