from fastapi import APIRouter

from app.api.v1.endpoints.admin import router as admin_router
from app.api.v1.endpoints.ai import router as ai_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.information import router as information_router
from app.api.v1.endpoints.engineering import router as engineering_router
from app.api.v1.endpoints.company_secretary import (
    router as company_secretary_router,
)
from app.api.v1.endpoints.soc import router as soc_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(admin_router)
api_router.include_router(ai_router)
api_router.include_router(information_router)
api_router.include_router(engineering_router)
api_router.include_router(company_secretary_router)
api_router.include_router(soc_router)
