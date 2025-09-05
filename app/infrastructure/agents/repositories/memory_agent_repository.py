from typing import Dict, List, Optional
from datetime import datetime

from app.domain.agents.entities.agent import Agent, AgentType, AgentStatus
from app.domain.agents.ports.agent_repository import AgentRepositoryPort


class MemoryAgentRepository(AgentRepositoryPort):
    """Implementação em memória do repositório de agentes."""
    
    def __init__(self):
        self._agents: Dict[str, Agent] = {}
    
    async def save(self, agent: Agent) -> Agent:
        """Salva um agente no repositório."""
        agent.updated_at = datetime.utcnow()
        self._agents[agent.id] = agent
        return agent
    
    async def find_by_id(self, agent_id: str) -> Optional[Agent]:
        """Busca um agente por ID."""
        return self._agents.get(agent_id)
    
    async def find_by_name(self, name: str) -> Optional[Agent]:
        """Busca um agente por nome."""
        for agent in self._agents.values():
            if agent.name == name:
                return agent
        return None
    
    async def find_by_type(self, agent_type: AgentType) -> List[Agent]:
        """Busca agentes por tipo."""
        return [
            agent for agent in self._agents.values() 
            if agent.agent_type == agent_type
        ]
    
    async def find_available_agents(self) -> List[Agent]:
        """Busca agentes disponíveis (status IDLE)."""
        return [
            agent for agent in self._agents.values() 
            if agent.status == AgentStatus.IDLE
        ]
    
    async def update_status(self, agent_id: str, status: AgentStatus) -> Optional[Agent]:
        """Atualiza o status de um agente."""
        agent = self._agents.get(agent_id)
        if agent:
            agent.status = status
            agent.updated_at = datetime.utcnow()
            return agent
        return None
    
    async def delete(self, agent_id: str) -> bool:
        """Remove um agente do repositório."""
        if agent_id in self._agents:
            del self._agents[agent_id]
            return True
        return False
    
    async def list_all(self) -> List[Agent]:
        """Lista todos os agentes."""
        return list(self._agents.values())
    
    async def update_metadata(self, agent_id: str, metadata: Dict) -> Optional[Agent]:
        """Atualiza os metadados de um agente."""
        agent = self._agents.get(agent_id)
        if agent:
            agent.metadata.update(metadata)
            agent.updated_at = datetime.utcnow()
            return agent
        return None
    
    async def count_by_status(self, status: AgentStatus) -> int:
        """Conta agentes por status."""
        return len([
            agent for agent in self._agents.values() 
            if agent.status == status
        ])
    
    async def count_by_type(self, agent_type: AgentType) -> int:
        """Conta agentes por tipo."""
        return len([
            agent for agent in self._agents.values() 
            if agent.agent_type == agent_type
        ])
    
    def clear(self) -> None:
        """Limpa todos os agentes (útil para testes)."""
        self._agents.clear()
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas do repositório."""
        total = len(self._agents)
        by_status = {}
        by_type = {}
        
        for agent in self._agents.values():
            # Contar por status
            status_key = agent.status.value
            by_status[status_key] = by_status.get(status_key, 0) + 1
            
            # Contar por tipo
            type_key = agent.agent_type.value
            by_type[type_key] = by_type.get(type_key, 0) + 1
        
        return {
            "total_agents": total,
            "by_status": by_status,
            "by_type": by_type
        }