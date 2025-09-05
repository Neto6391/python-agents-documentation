from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime


class AgentStatus(Enum):
    """Status do agente."""
    IDLE = "idle"
    PROCESSING = "processing"
    ERROR = "error"
    COMPLETED = "completed"


class AgentType(Enum):
    """Tipos de agentes disponíveis."""
    MARKDOWN_GENERATOR = "markdown_generator"
    PROJECT_ANALYZER = "project_analyzer"
    DOCUMENT_VALIDATOR = "document_validator"


@dataclass
class AgentConfig:
    """Configuração do agente."""
    model_provider: str  # openai, anthropic, etc.
    model_id: str  # gpt-4o, claude-3-sonnet, etc.
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
class Agent:
    """Entidade principal do agente."""
    id: str
    name: str
    agent_type: AgentType
    description: str
    config: AgentConfig
    status: AgentStatus = AgentStatus.IDLE
    created_at: datetime = None
    updated_at: datetime = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}
    
    def update_status(self, status: AgentStatus) -> None:
        """Atualiza o status do agente."""
        self.status = status
        self.updated_at = datetime.utcnow()
    
    def is_available(self) -> bool:
        """Verifica se o agente está disponível para processar."""
        return self.status in [AgentStatus.IDLE, AgentStatus.COMPLETED]