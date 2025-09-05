from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.agents.entities.agent import Agent, AgentType, AgentStatus


class AgentRepositoryPort(ABC):
    """Port para repositório de agentes."""
    
    @abstractmethod
    async def save(self, agent: Agent) -> Agent:
        """Salva um agente."""
        pass
    
    @abstractmethod
    async def find_by_id(self, agent_id: str) -> Optional[Agent]:
        """Busca um agente por ID."""
        pass
    
    @abstractmethod
    async def find_by_name(self, name: str) -> Optional[Agent]:
        """Busca um agente por nome."""
        pass
    
    @abstractmethod
    async def find_by_type(self, agent_type: AgentType) -> List[Agent]:
        """Busca agentes por tipo."""
        pass
    
    @abstractmethod
    async def find_available_agents(self) -> List[Agent]:
        """Busca agentes disponíveis para processamento."""
        pass
    
    @abstractmethod
    async def update_status(self, agent_id: str, status: AgentStatus) -> bool:
        """Atualiza o status de um agente."""
        pass
    
    @abstractmethod
    async def delete(self, agent_id: str) -> bool:
        """Remove um agente."""
        pass
    
    @abstractmethod
    async def list_all(self) -> List[Agent]:
        """Lista todos os agentes."""
        pass