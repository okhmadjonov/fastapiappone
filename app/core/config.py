from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Enterprise FastAPI Backend"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # PostgreSQL ulanish manzili
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/appone_db"
    
    # JWT Sozlamalari
    JWT_SECRET_KEY: str = "enterprise_super_secret_jwt_key_2026_change_in_production"
    JWT_REFRESH_SECRET_KEY: str = "enterprise_super_secret_refresh_jwt_key_2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # React Frontend uchun CORS ruxsatlari
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",  # Vite + React
        "http://localhost:3000",  # Create React App / Next.js
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ]

settings = Settings()
