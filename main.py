from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.database import engine, Base
import app.domain.models
from app.api.v1.router import api_router

# Logging sozlash
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database jadvallari va xizmatlar tayyor!")
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise FastAPI Clean Architecture backend (JWT, RBAC, Relationships, PostgreSQL, Alembic)",
    lifespan=lifespan
)

# CORS Middleware (React frontend uchun)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- Global Exception Handlers -----------------

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Barcha HTTP xatoliklar (400, 401, 403, 404) uchun yagona standart javob"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.status_code,
                "message": exc.detail
            }
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Pydantic validatsiya xatolari (422) uchun chiroyli JSON javob"""
    errors = []
    for err in exc.errors():
        field = " -> ".join(str(loc) for loc in err["loc"] if loc != "body")
        errors.append({
            "field": field,
            "message": err["msg"]
        })
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": 422,
                "message": "Kiritilgan ma'lumotlarda xatolik bor",
                "details": errors
            }
        }
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Kutilmagan server xatolari (500) uchun global tutuvchi"""
    logger.error(f"Kutilmagan server xatosi: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": 500,
                "message": "Ichki server xatoligi yuz berdi. Tez orada bartaraf etiladi."
            }
        }
    )

# ----------------- Routerlarni ulash -----------------
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["Health"])
def health_check():
    return {
        "success": True,
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "docs_url": "/docs"
    }