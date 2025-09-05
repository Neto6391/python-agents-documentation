from typing import List

from app.domain.agents.entities.agent import Agent, AgentConfig, AgentType, AgentStatus
from app.application.agents.dtos.agent_dtos import (
    CreateAgentRequest,
    AgentResponse,
    AgentStatusResponse,
    ListAgentsResponse
)


class AgentMapper:
    """Mapper para conversão entre entidades de agente e DTOs."""
    
    @staticmethod
    def create_request_to_config(request: CreateAgentRequest) -> AgentConfig:
        """Converte CreateAgentRequest para AgentConfig."""
        return AgentConfig(
            model_provider=request.model_provider,
            model_id=request.model_id,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            tools=request.tools.copy() if request.tools else [],
            instructions=request.instructions.copy() if request.instructions else []
        )
    
    @staticmethod
    def create_request_to_entity(request: CreateAgentRequest, agent_id: str) -> Agent:
        """Converte CreateAgentRequest para entidade Agent."""
        config = AgentMapper.create_request_to_config(request)
        
        return Agent(
            id=agent_id,
            name=request.name,
            agent_type=AgentType(request.agent_type),
            description=request.description,
            config=config,
            status=AgentStatus.IDLE
        )
    
    @staticmethod
    def entity_to_response(agent: Agent) -> AgentResponse:
        """Converte entidade Agent para AgentResponse."""
        return AgentResponse(
            id=agent.id,
            name=agent.name,
            agent_type=agent.agent_type.value,
            description=agent.description,
            status=agent.status.value,
            created_at=agent.created_at,
            updated_at=agent.updated_at,
            config={
                "model_provider": agent.config.model_provider,
                "model_id": agent.config.model_id,
                "temperature": agent.config.temperature,
                "max_tokens": agent.config.max_tokens,
                "tools": agent.config.tools,
                "instructions": agent.config.instructions
            },
            metadata=agent.metadata.copy() if agent.metadata else {}
        )
    
    @staticmethod
    def entity_to_status_response(agent: Agent) -> AgentStatusResponse:
        """Converte entidade Agent para AgentStatusResponse."""
        return AgentStatusResponse(
            agent_id=agent.id,
            status=agent.status.value,
            last_activity=agent.updated_at,
            processing_info=agent.metadata.copy() if agent.metadata else {}
        )
    
    @staticmethod
    def entities_to_list_response(
        agents: List[Agent], 
        total: int, 
        limit: int, 
        offset: int
    ) -> ListAgentsResponse:
        """Converte lista de entidades Agent para ListAgentsResponse."""
        agent_responses = [
            AgentMapper.entity_to_response(agent) for agent in agents
        ]
        
        return ListAgentsResponse(
            agents=agent_responses,
            total=total,
            limit=limit,
            offset=offset
        )