from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from app.domain.models import Post, User
from app.schemas.user_schemas import PostCreateDto

class PostService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, dto: PostCreateDto, author_id: int) -> Post:
        post = Post(
            title=dto.title,
            content=dto.content,
            author_id=author_id
        )
        self.db.add(post)
        await self.db.commit()
        await self.db.refresh(post)
        return post

    async def get_all(self, skip: int = 0, limit: int = 50) -> list[Post]:
        result = await self.db.scalars(
            select(Post).offset(skip).limit(limit).order_by(Post.id.desc())
        )
        return list(result.all())

    async def get_by_id(self, post_id: int) -> Post:
        result = await self.db.scalars(select(Post).where(Post.id == post_id))
        post = result.first()
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Maqola topilmadi"
            )
        return post

    async def get_user_posts(self, user_id: int) -> list[Post]:
        result = await self.db.scalars(
            select(Post).where(Post.author_id == user_id)
        )
        return list(result.all())

    async def get_user_with_posts_eager(self, user_id: int) -> User:
        """
        EF Core dagi: _context.Users.Include(u => u.Posts).FirstOrDefaultAsync(...)
        SQLAlchemy 2.0 da: selectinload(User.posts)
        Bu barcha postlarni bitta qo'shimcha SELECT IN (...) bilan yuklaydi va N+1 muammosini yo'q qiladi!
        """
        query = (
            select(User)
            .options(selectinload(User.posts))
            .where(User.id == user_id)
        )
        result = await self.db.scalars(query)
        user = result.first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Foydalanuvchi topilmadi"
            )
        return user
