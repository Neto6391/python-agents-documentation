import uuid
from typing import Optional

from app.domain.agents.entities.agent import Agent
from app.domain.agents.entities.model_provider import ModelProvider
from app.domain.agents.ports.agent_repository import AgentRepositoryPort
from app.domain.agents.ports.agent_service import AgentServicePort
from app.infrastructure.agents.services.agent_service_factory import AgentServiceFactory
from app.application.agents.dtos.agent_dtos import CreateAgentRequest, AgentResponse
from app.application.agents.mappers.agent_mapper import AgentMapper


class CreateAgentUseCase:
    """Caso de uso para criação de agentes."""
    
    def __init__(
        self,
        agent_repository: AgentRepositoryPort,
        agent_service: AgentServicePort
    ):
        self._agent_repository = agent_repository
        self._agent_service = agent_service
    
    async def execute(self, request: CreateAgentRequest) -> AgentResponse:
        """Executa a criação de um novo agente.
        
        Args:
            request: Dados para criação do agente
            
        Returns:
            AgentResponse: Dados do agente criado
            
        Raises:
            ValueError: Se os dados de entrada forem inválidos
            RuntimeError: Se houver erro na criação do agente
        """
        try:
            # Gerar ID único para o agente
            agent_id = str(uuid.uuid4())
            
            # Converter request para entidade
            agent = AgentMapper.create_request_to_entity(request, agent_id)
            
            # Validar configuração do agente
            await self._validate_agent_config(agent)
            
            # Usar o serviço injetado pelo DI (que já é o GroqAgentService configurado)
            # Passar o ID do agente para manter consistência
            created_agent = await self._agent_service.create_agent(agent.config, agent_id)
            
            # Atualizar metadados do agente com informações do serviço
            agent.metadata.update({
                "provider_agent_id": created_agent.id,
                "provider_status": "created",
                "creation_source": "api"
            })
            
            # Salvar agente no repositório
            saved_agent = await self._agent_repository.save(agent)
            
            # Converter para response
            return AgentMapper.entity_to_response(saved_agent)
            
        except ValueError as e:
            raise ValueError(f"Dados inválidos para criação do agente: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Erro ao criar agente: {str(e)}")
    
    async def _validate_agent_config(self, agent: Agent) -> None:
        """Valida a configuração do agente.
        
        Args:
            agent: Entidade do agente a ser validada
            
        Raises:
            ValueError: Se a configuração for inválida
        """
        config = agent.config
        
        # Validar provider de modelo
        if not ModelProvider.is_valid_provider(config.model_provider):
            raise ValueError(
                f"Provider '{config.model_provider}' não suportado. "
                f"Providers válidos: {ModelProvider.get_supported_providers()}"
            )
        
        # Validar temperatura
        if not 0.0 <= config.temperature <= 2.0:
            raise ValueError("Temperatura deve estar entre 0.0 e 2.0")
        
        # Validar max_tokens
        if config.max_tokens <= 0 or config.max_tokens > 32000:
            raise ValueError("max_tokens deve estar entre 1 e 32000")
        
        # Validar nome único
        existing_agent = await self._agent_repository.find_by_name(agent.name)
        if existing_agent:
            raise ValueError(f"Já existe um agente com o nome '{agent.name}'")