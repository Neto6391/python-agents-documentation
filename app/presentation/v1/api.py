from fastapi import APIRouter
from app.presentation.v1.endpoints.health.endpoints import router as health_router
from app.presentation.v1.endpoints.agents import agents_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router)
api_router.include_router(agents_router)
