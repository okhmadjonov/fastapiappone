from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base
import app.domain.models  # Modellar metadatasi yuklanishi uchun
from app.api.v1.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Server yoqilganda PostgreSQL da jadvallarni avtomatik tayyorlaydi:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="React frontend uchun tayyorlangan Clean Architecture Enterprise FastAPI loyihasi",
    lifespan=lifespan
)

# React / Frontend bilan to'siqsiz ishlash uchun CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Asosiy API routerlarni ulash
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "docs_url": "/docs"
    }