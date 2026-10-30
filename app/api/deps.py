from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import decode_token
from app.domain.models import User
from app.services.user_service import UserService
from app.services.auth_service import AuthService
from app.services.post_service import PostService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)

def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)

def get_post_service(db: AsyncSession = Depends(get_db)) -> PostService:
    return PostService(db)

# .NET dagi [Authorize] atributining muqobili:
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Autentifikatsiyadan o'tilmagan (Token yaroqsiz)",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_token(token, is_refresh=False)
    if not payload or payload.get("type") != "access":
        raise credentials_exception

    user_id = payload.get("sub")
    if not user_id:
        raise credentials_exception

    user = await user_service.get_by_id(int(user_id))
    if not user or not user.is_active:
        raise credentials_exception

    return user

# .NET dagi [Authorize(Roles = "Admin")] atributining to'liq muqobili:
class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)) -> User:
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Ushbu amalni bajarish uchun ruxsat yetarli emas! Talab qilinadigan rol: {self.allowed_roles}"
            )
        return user
