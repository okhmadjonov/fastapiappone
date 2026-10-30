from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.user_schemas import (
    UserRegisterDto, 
    UserResponseDto, 
    TokenResponseDto, 
    RefreshTokenDto,
    UserLoginDto,
    LogoutDto
)
from app.services.user_service import UserService
from app.services.auth_service import AuthService
from app.api.deps import get_user_service, get_auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponseDto, status_code=status.HTTP_201_CREATED)
async def register(
    dto: UserRegisterDto,
    user_service: UserService = Depends(get_user_service)
):
    """Yangi foydalanuvchini ro'yxatdan o'tkazish"""
    return await user_service.register(dto)

@router.post("/login", response_model=TokenResponseDto)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Swagger va mijozlar uchun standart OAuth2 Login endpoint.
    username sifatida email yuboriladi.
    """
    dto = UserLoginDto(email=form_data.username, password=form_data.password)
    return await auth_service.authenticate(dto)

@router.post("/login-json", response_model=TokenResponseDto)
async def login_json(
    dto: UserLoginDto,
    auth_service: AuthService = Depends(get_auth_service)
):
    """React frontend uchun qulay to'g'ridan-to'g'ri JSON Login endpoint"""
    return await auth_service.authenticate(dto)

@router.post("/refresh", response_model=TokenResponseDto)
async def refresh_token(
    dto: RefreshTokenDto,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Eski refresh token evaziga yangi Access + Refresh token olish (Database tekshiruvi bilan)"""
    return await auth_service.refresh_access_token(dto.refresh_token)

@router.post("/logout")
async def logout(
    dto: LogoutDto,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Foydalanuvchini tizimdan chiqarish (Refresh tokenni bazada bekor qilish)"""
    return await auth_service.logout(dto.refresh_token)
