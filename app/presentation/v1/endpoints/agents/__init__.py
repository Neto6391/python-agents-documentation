from fastapi import APIRouter
from .agent_endpoints import router as agent_router
from .document_endpoints import router as document_router

# Router principal para todos os endpoints de agentes
agents_router = APIRouter(prefix="/agents", tags=["agents"])

# Incluir rotas de agentes
agents_router.include_router(agent_router)

# Incluir rotas de documentos
agents_router.include_router(document_router, prefix="/documents")

__all__ = ["agents_router"]