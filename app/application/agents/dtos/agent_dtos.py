from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime


@dataclass
class CreateAgentRequest:
    """DTO para criação de agente."""
    name: str
    agent_type: str
    description: str
    model_provider: str
    model_id: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    tools: List[str] = None
    instructions: List[str] = None
    
    def __post_init__(self):
        if self.tools is None:
            self.tools = []
        if self.instructions is None:
            self.instructions = []


@dataclass
class AgentResponse:
    """DTO de resposta do agente."""
    id: str
    name: str
    agent_type: str
    description: str
    status: str
    created_at: datetime
    updated_at: datetime
    config: Dict[str, Any]
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class UpdateAgentStatusRequest:
    """DTO para atualização de status do agente."""
    agent_id: str
    status: str


@dataclass
class AgentStatusResponse:
    """DTO de resposta do status do agente."""
    agent_id: str
    status: str
    last_activity: datetime
    processing_info: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.processing_info is None:
            self.processing_info = {}


@dataclass
class ListAgentsRequest:
    """DTO para listagem de agentes."""
    agent_type: Optional[str] = None
    status: Optional[str] = None
    limit: int = 50
    offset: int = 0


@dataclass
class ListAgentsResponse:
    """DTO de resposta da listagem de agentes."""
    agents: List[AgentResponse]
    total: int
    limit: int
    offset: int