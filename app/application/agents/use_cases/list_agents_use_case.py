from typing import Optional, List

from app.domain.agents.entities.agent import Agent, AgentType, AgentStatus
from app.domain.agents.ports.agent_repository import AgentRepositoryPort
from app.application.agents.dtos.agent_dtos import ListAgentsRequest, ListAgentsResponse
from app.application.agents.mappers.agent_mapper import AgentMapper


class ListAgentsUseCase:
    """Caso de uso para listagem de agentes."""
    
    def __init__(self, agent_repository: AgentRepositoryPort):
        self._agent_repository = agent_repository
    
    async def execute(self, request: ListAgentsRequest) -> ListAgentsResponse:
        """Executa a listagem de agentes com filtros e paginação.
        
        Args:
            request: Parâmetros de listagem
            
        Returns:
            ListAgentsResponse: Lista paginada de agentes
            
        Raises:
            ValueError: Se os parâmetros forem inválidos
            RuntimeError: Se houver erro na consulta
        """
        try:
            # Validar parâmetros de paginação
            self._validate_pagination_params(request.limit, request.offset)
            
            # Aplicar filtros
            agents = await self._apply_filters(request)
            
            # Contar total de registros
            total = await self._count_filtered_agents(request)
            
            # Aplicar paginação
            paginated_agents = agents[request.offset:request.offset + request.limit]
            
            # Converter para response
            return AgentMapper.entities_to_list_response(
                agents=paginated_agents,
                total=total,
                limit=request.limit,
                offset=request.offset
            )
            
        except ValueError as e:
            raise e
        except Exception as e:
            raise RuntimeError(f"Erro ao listar agentes: {str(e)}")
    
    async def list_available_agents(self) -> List[Agent]:
        """Lista apenas agentes disponíveis (status IDLE).
        
        Returns:
            List[Agent]: Lista de agentes disponíveis
        """
        try:
            return await self._agent_repository.find_available_agents()
        except Exception as e:
            raise RuntimeError(f"Erro ao listar agentes disponíveis: {str(e)}")
    
    async def list_by_type(self, agent_type: AgentType) -> List[Agent]:
        """Lista agentes por tipo.
        
        Args:
            agent_type: Tipo de agente a filtrar
            
        Returns:
            List[Agent]: Lista de agentes do tipo especificado
        """
        try:
            return await self._agent_repository.find_by_type(agent_type)
        except Exception as e:
            raise RuntimeError(f"Erro ao listar agentes por tipo: {str(e)}")
    
    async def _apply_filters(self, request: ListAgentsRequest) -> List[Agent]:
        """Aplica filtros na consulta de agentes.
        
        Args:
            request: Parâmetros de filtro
            
        Returns:
            List[Agent]: Lista filtrada de agentes
        """
        # Se não há filtros, retornar todos
        if not any([request.agent_type, request.status]):
            return await self._agent_repository.list_all()
        
        # Aplicar filtros específicos
        agents = await self._agent_repository.list_all()
        
        if request.agent_type:
            agent_type = AgentType(request.agent_type)
            agents = [a for a in agents if a.agent_type == agent_type]
        
        if request.status:
            status = AgentStatus(request.status)
            agents = [a for a in agents if a.status == status]
        
        return agents
    
    async def _count_filtered_agents(self, request: ListAgentsRequest) -> int:
        """Conta o total de agentes após aplicar filtros.
        
        Args:
            request: Parâmetros de filtro
            
        Returns:
            int: Total de agentes filtrados
        """
        filtered_agents = await self._apply_filters(request)
        return len(filtered_agents)
    
    def _validate_pagination_params(self, limit: int, offset: int) -> None:
        """Valida parâmetros de paginação.
        
        Args:
            limit: Limite de registros por página
            offset: Offset para paginação
            
        Raises:
            ValueError: Se os parâmetros forem inválidos
        """
        if limit <= 0:
            raise ValueError("Limit deve ser maior que 0")
        
        if limit > 100:
            raise ValueError("Limit não pode ser maior que 100")
        
        if offset < 0:
            raise ValueError("Offset deve ser maior ou igual a 0")