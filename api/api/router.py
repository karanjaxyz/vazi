from fastapi import APIRouter

from .auth import router as auth_router
from .projects import router as projects_router
from .dashboard import router as dashboard_router
from .billing import router as billing_router
from .admin import router as admin_router

api_router = APIRouter(prefix="/api")

api_router.include_router(auth_router)
api_router.include_router(projects_router)
api_router.include_router(dashboard_router)
api_router.include_router(billing_router)
api_router.include_router(admin_router)
