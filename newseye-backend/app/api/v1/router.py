from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, news, risk, notifications, analytics, websockets, soar

router = APIRouter()

router.include_router(auth.router)
router.include_router(users.router)
router.include_router(news.router)
router.include_router(risk.router)
router.include_router(notifications.router)
router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
router.include_router(websockets.router)
router.include_router(soar.router)
