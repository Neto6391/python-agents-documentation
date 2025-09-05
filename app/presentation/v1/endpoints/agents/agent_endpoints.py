from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import inject, Provide

from app.core.di.container import Container
from app.core.security.api_key import api_key_auth
from app.application.agents.use_cases.create_agent_use_case import CreateAgentUseCase
from app.application.agents.use_cases.list_agents_use_case import ListAgentsUseCase
from app.application.agents.dtos.agent_dtos import (
    CreateAgentRequest,
    AgentResponse,
    UpdateAgentStatusRequest,
    AgentStatusResponse,
    ListAgentsRequest,
    ListAgentsResponse
)
from app.domain.agents.entities.agent import AgentStatus

router = APIRouter(tags=["agents"])


@router.post(
    "/",
    response_model=AgentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar novo agente",
    description="Cria um novo agente no sistema com configurações específicas"
)
@inject
async def create_agent(
    request: CreateAgentRequest,
    api_key: str = Depends(api_key_auth),
    create_agent_use_case: CreateAgentUseCase = Depends(
        Provide[Container.create_agent_use_case]
    )
) -> AgentResponse:
    """Cria um novo agente no sistema."""
    try:
        return await create_agent_use_case.execute(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/",
    response_model=ListAgentsResponse,
    summary="Listar agentes",
    description="Lista agentes com filtros e paginação"
)
@inject
async def list_agents(
    limit: int = 10,
    offset: int = 0,
    agent_type: str = None,
    agent_status: str = None,
    api_key: str = Depends(api_key_auth),
    list_agents_use_case: ListAgentsUseCase = Depends(
        Provide[Container.list_agents_use_case]
    )
) -> ListAgentsResponse:
    """Lista agentes com filtros opcionais."""
    try:
        request = ListAgentsRequest(
            limit=limit,
            offset=offset,
            agent_type=agent_type,
            status=agent_status
        )
        return await list_agents_use_case.execute(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/{agent_id}",
    response_model=AgentResponse,
    summary="Obter agente por ID",
    description="Obtém detalhes de um agente específico"
)
@inject
async def get_agent(
    agent_id: str,
    api_key: str = Depends(api_key_auth),
    agent_repository = Depends(Provide[Container.agent_repository])
) -> AgentResponse:
    """Obtém um agente por ID."""
    try:
        from app.application.agents.mappers.agent_mapper import AgentMapper
        
        agent = await agent_repository.find_by_id(agent_id)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agente com ID '{agent_id}' não encontrado"
            )
        
        return AgentMapper.entity_to_response(agent)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put(
    "/{agent_id}/status",
    response_model=AgentStatusResponse,
    summary="Atualizar status do agente",
    description="Atualiza o status de um agente específico"
)
@inject
async def update_agent_status(
    agent_id: str,
    request: UpdateAgentStatusRequest,
    api_key: str = Depends(api_key_auth),
    agent_repository = Depends(Provide[Container.agent_repository])
) -> AgentStatusResponse:
    """Atualiza o status de um agente."""
    try:
        from app.application.agents.mappers.agent_mapper import AgentMapper
        
        # Verificar se o agente existe
        agent = await agent_repository.find_by_id(agent_id)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agente com ID '{agent_id}' não encontrado"
            )
        
        # Atualizar status
        new_status = AgentStatus(request.status)
        updated_agent = await agent_repository.update_status(agent_id, new_status)
        
        if not updated_agent:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Falha ao atualizar status do agente"
            )
        
        return AgentMapper.entity_to_status_response(updated_agent)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Status inválido: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/{agent_id}/status",
    response_model=AgentStatusResponse,
    summary="Obter status do agente",
    description="Obtém o status atual de um agente"
)
@inject
async def get_agent_status(
    agent_id: str,
    api_key: str = Depends(api_key_auth),
    agent_repository = Depends(Provide[Container.agent_repository]),
    agent_service = Depends(Provide[Container.agent_service])
) -> AgentStatusResponse:
    """Obtém o status atual de um agente."""
    try:
        from app.application.agents.mappers.agent_mapper import AgentMapper
        
        # Verificar se o agente existe
        agent = await agent_repository.find_by_id(agent_id)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agente com ID '{agent_id}' não encontrado"
            )
        
        # Obter status do serviço Agno
        agno_status = await agent_service.get_agent_status(agent_id)
        
        # Atualizar metadados do agente com status do Agno
        if agno_status:
            await agent_repository.update_metadata(agent_id, {
                "agno_status": agno_status.get("status"),
                "last_agno_activity": agno_status.get("last_activity")
            })
            
            # Recarregar agente atualizado
            agent = await agent_repository.find_by_id(agent_id)
        
        return AgentMapper.entity_to_status_response(agent)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete(
    "/{agent_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar agente",
    description="Remove um agente do sistema"
)
@inject
async def delete_agent(
    agent_id: str,
    api_key: str = Depends(api_key_auth),
    agent_repository = Depends(Provide[Container.agent_repository]),
    agent_service = Depends(Provide[Container.agent_service])
):
    """Remove um agente do sistema."""
    try:
        # Verificar se o agente existe
        agent = await agent_repository.find_by_id(agent_id)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agente com ID '{agent_id}' não encontrado"
            )
        
        # Parar agente no serviço Agno
        await agent_service.stop_agent(agent_id)
        
        # Remover do repositório
        success = await agent_repository.delete(agent_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Falha ao deletar agente"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/available",
    response_model=List[AgentResponse],
    summary="Listar agentes disponíveis",
    description="Lista apenas agentes com status IDLE (disponíveis)"
)
@inject
async def list_available_agents(
    api_key: str = Depends(api_key_auth),
    list_agents_use_case: ListAgentsUseCase = Depends(
        Provide[Container.list_agents_use_case]
    )
) -> List[AgentResponse]:
    """Lista agentes disponíveis para uso."""
    try:
        from app.application.agents.mappers.agent_mapper import AgentMapper
        
        agents = await list_agents_use_case.list_available_agents()
        return [AgentMapper.entity_to_response(agent) for agent in agents]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )