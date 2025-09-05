from dependency_injector import containers, providers

from app.infrastructure.health.adapters.health_check_adapter import HealthCheckAdapter
from app.application.health.use_cases.check_health import CheckHealthUseCase

# Importações dos agentes
from app.infrastructure.agents.repositories.memory_agent_repository import MemoryAgentRepository
from app.infrastructure.agents.repositories.memory_document_repository import MemoryDocumentRepository
from app.infrastructure.agents.services.agno_agent_service import AgnoAgentService
from app.infrastructure.agents.services.groq_agent_service import GroqAgentService
from app.infrastructure.agents.services.agent_service_factory import AgentServiceFactory
from app.application.agents.use_cases.create_agent_use_case import CreateAgentUseCase
from app.application.agents.use_cases.generate_document_use_case import GenerateDocumentUseCase
from app.application.agents.use_cases.list_agents_use_case import ListAgentsUseCase
from app.application.agents.use_cases.list_documents_use_case import ListDocumentsUseCase


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=["app.presentation.v1.endpoints"]
    )

    # Health check
    health_check_adapter = providers.Singleton(HealthCheckAdapter)
    check_health_uc = providers.Singleton(CheckHealthUseCase, port=health_check_adapter)
    
    # Repositórios de agentes
    agent_repository = providers.Singleton(MemoryAgentRepository)
    document_repository = providers.Singleton(MemoryDocumentRepository)
    
    # Serviços de infraestrutura
    agno_agent_service = providers.Singleton(AgnoAgentService)
    groq_agent_service = providers.Singleton(GroqAgentService)
    agent_service_factory = providers.Singleton(AgentServiceFactory)
    
    # Serviço padrão (usando Groq)
    agent_service = providers.Singleton(GroqAgentService)
    
    # Casos de uso de agentes
    create_agent_use_case = providers.Factory(
        CreateAgentUseCase,
        agent_repository=agent_repository,
        agent_service=agent_service
    )
    
    generate_document_use_case = providers.Factory(
        GenerateDocumentUseCase,
        agent_repository=agent_repository,
        document_repository=document_repository,
        agent_service=agent_service
    )
    
    list_agents_use_case = providers.Factory(
        ListAgentsUseCase,
        agent_repository=agent_repository
    )
    
    list_documents_use_case = providers.Factory(
        ListDocumentsUseCase,
        document_repository=document_repository
    )