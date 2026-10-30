from fastapi import APIRouter, Depends, status
from app.domain.models import User
from app.schemas.user_schemas import PostCreateDto, PostResponseDto
from app.services.post_service import PostService
from app.api.deps import get_post_service, get_current_user

router = APIRouter(prefix="/posts", tags=["Posts"])

@router.post("/", response_model=PostResponseDto, status_code=status.HTTP_201_CREATED)
async def create_post(
    dto: PostCreateDto,
    current_user: User = Depends(get_current_user),
    post_service: PostService = Depends(get_post_service)
):
    """Yangi maqola yaratish (Muallif joriy token egasi)"""
    return await post_service.create(dto, author_id=current_user.id)

@router.get("/", response_model=list[PostResponseDto])
async def get_posts(
    skip: int = 0,
    limit: int = 50,
    post_service: PostService = Depends(get_post_service)
):
    """Barcha maqolalar ro'yxatini olish"""
    return await post_service.get_all(skip=skip, limit=limit)

@router.get("/{post_id}", response_model=PostResponseDto)
async def get_post_by_id(
    post_id: int,
    post_service: PostService = Depends(get_post_service)
):
    """Bitta maqolani ID bo'yicha olish"""
    return await post_service.get_by_id(post_id)
