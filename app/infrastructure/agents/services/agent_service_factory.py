from typing import Dict, Type

from app.domain.agents.entities.model_provider import ModelProvider
from app.domain.agents.ports.agent_service import AgentServicePort
from app.infrastructure.agents.services.agno_agent_service import AgnoAgentService
from app.infrastructure.agents.services.groq_agent_service import GroqAgentService


class AgentServiceFactory:
    """Factory para criar serviços de agentes baseado no provedor."""
    
    _services: Dict[str, Type[AgentServicePort]] = {
        ModelProvider.OPENAI.value: AgnoAgentService,
        ModelProvider.ANTHROPIC.value: AgnoAgentService,
        ModelProvider.LOCAL.value: AgnoAgentService,
        ModelProvider.GROQ.value: GroqAgentService
    }
    
    _instances: Dict[str, AgentServicePort] = {}
    
    @classmethod
    def get_service(cls, provider: str) -> AgentServicePort:
        """Obtém o serviço de agente para o provedor especificado.
        
        Args:
            provider: Nome do provedor (openai, anthropic, groq, local)
            
        Returns:
            Instância do serviço de agente
            
        Raises:
            ValueError: Se o provedor não for suportado
        """
        if provider not in cls._services:
            raise ValueError(f"Provedor '{provider}' não suportado. Provedores disponíveis: {list(cls._services.keys())}")
        
        # Usar singleton para cada provedor
        if provider not in cls._instances:
            service_class = cls._services[provider]
            cls._instances[provider] = service_class()
        
        return cls._instances[provider]
    
    @classmethod
    def get_supported_providers(cls) -> list[str]:
        """Retorna a lista de provedores suportados."""
        return list(cls._services.keys())
    
    @classmethod
    def register_service(cls, provider: str, service_class: Type[AgentServicePort]) -> None:
        """Registra um novo serviço de agente.
        
        Args:
            provider: Nome do provedor
            service_class: Classe do serviço
        """
        cls._services[provider] = service_class
        # Limpar instância existente se houver
        if provider in cls._instances:
            del cls._instances[provider]