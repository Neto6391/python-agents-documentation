from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from app.domain.agents.entities.agent import Agent, AgentConfig
from app.domain.agents.entities.project_document import (
    ProjectDocument, 
    ValidationResult, 
    ProjectMetadata
)


class AgentServicePort(ABC):
    """Port para serviços de agentes usando framework Agno."""
    
    @abstractmethod
    async def create_agent(self, config: AgentConfig) -> Agent:
        """Cria uma nova instância de agente."""
        pass
    
    @abstractmethod
    async def validate_prompt(self, prompt: str, agent_id: str) -> ValidationResult:
        """Valida se o prompt é adequado para geração de documento de projeto."""
        pass
    
    @abstractmethod
    async def extract_project_metadata(self, prompt: str, agent_id: str) -> ProjectMetadata:
        """Extrai metadados do projeto a partir do prompt."""
        pass
    
    @abstractmethod
    async def generate_markdown_document(
        self, 
        prompt: str, 
        agent_id: str, 
        document_type: str = "readme"
    ) -> ProjectDocument:
        """Gera documento Markdown a partir do prompt."""
        pass
    
    @abstractmethod
    async def improve_prompt(
        self, 
        original_prompt: str, 
        validation_result: ValidationResult,
        agent_id: str
    ) -> str:
        """Gera sugestões para melhorar o prompt baseado na validação."""
        pass
    
    @abstractmethod
    async def analyze_document_quality(
        self, 
        document: ProjectDocument, 
        agent_id: str
    ) -> Dict[str, Any]:
        """Analisa a qualidade do documento gerado."""
        pass
    
    @abstractmethod
    async def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Obtém o status atual do agente."""
        pass
    
    @abstractmethod
    async def stop_agent(self, agent_id: str) -> bool:
        """Para a execução de um agente."""
        pass
    
    @abstractmethod
    async def restart_agent(self, agent_id: str) -> bool:
        """Reinicia um agente."""
        pass

    @abstractmethod
    def reset(self):
        """Reseta o estado do serviço para testes."""
        pass