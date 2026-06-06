from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.database import engine, Base
from app.api.v1 import router
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("✅ NewsEye API Server Started")
    yield
    logger.info("❌ NewsEye API Server Stopped")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="IT 범죄 예방 및 대응 시스템",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # MVP 개발용 - 추후 제한 필요
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router.router, prefix="/api/v1")

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}
