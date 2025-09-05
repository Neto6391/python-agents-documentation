from typing import Dict, Any
from pydantic import BaseModel, Field


class AgentModelConfig(BaseModel):
    """Configuração para modelos de IA dos agentes."""
    
    provider: str = Field(default="openai", description="Provedor do modelo (openai, anthropic, etc.)")
    model_name: str = Field(default="gpt-4", description="Nome do modelo")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Temperatura do modelo")
    max_tokens: int = Field(default=2000, gt=0, description="Máximo de tokens")
    timeout: int = Field(default=30, gt=0, description="Timeout em segundos")


class AgentFrameworkConfig(BaseModel):
    """Configuração para o framework Agno."""
    
    base_url: str = Field(default="http://localhost:8080", description="URL base do framework Agno")
    api_key: str = Field(default="", description="Chave de API do framework")
    timeout: int = Field(default=60, gt=0, description="Timeout para requisições")
    retry_attempts: int = Field(default=3, ge=0, description="Tentativas de retry")
    retry_delay: float = Field(default=1.0, ge=0.0, description="Delay entre tentativas (segundos)")


class DocumentGenerationConfig(BaseModel):
    """Configuração para geração de documentos."""
    
    max_content_length: int = Field(default=50000, gt=0, description="Tamanho máximo do conteúdo")
    supported_formats: list[str] = Field(default=["markdown", "html"], description="Formatos suportados")
    quality_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Limite mínimo de qualidade")
    auto_improve_prompts: bool = Field(default=True, description="Melhorar prompts automaticamente")


class AgentsConfig(BaseModel):
    """Configuração principal do sistema de agentes."""
    
    # Configurações do modelo
    model: AgentModelConfig = Field(default_factory=AgentModelConfig)
    
    # Configurações do framework
    framework: AgentFrameworkConfig = Field(default_factory=AgentFrameworkConfig)
    
    # Configurações de geração de documentos
    document_generation: DocumentGenerationConfig = Field(default_factory=DocumentGenerationConfig)
    
    # Configurações de repositório
    repository_max_items: int = Field(default=10000, gt=0, description="Máximo de itens no repositório")
    
    # Configurações de cache
    cache_enabled: bool = Field(default=True, description="Habilitar cache")
    cache_ttl: int = Field(default=3600, gt=0, description="TTL do cache em segundos")
    
    # Configurações de logging
    log_agent_interactions: bool = Field(default=True, description="Logar interações com agentes")
    log_level: str = Field(default="INFO", description="Nível de log")
    
    # Configurações de segurança
    validate_prompts: bool = Field(default=True, description="Validar prompts antes de processar")
    sanitize_content: bool = Field(default=True, description="Sanitizar conteúdo gerado")
    
    class Config:
        env_prefix = "AGENTS_"
        case_sensitive = False


# Configurações padrão para diferentes tipos de agentes
DEFAULT_AGENT_CONFIGS: Dict[str, Dict[str, Any]] = {
    "markdown_generator": {
        "name": "Gerador de Markdown",
        "description": "Agente especializado em gerar documentação em Markdown",
        "model_config": {
            "provider": "openai",
            "model_name": "gpt-4",
            "temperature": 0.3,
            "max_tokens": 4000
        },
        "capabilities": [
            "generate_markdown",
            "validate_prompts",
            "extract_metadata",
            "improve_prompts",
            "analyze_quality"
        ]
    },
    "code_analyzer": {
        "name": "Analisador de Código",
        "description": "Agente especializado em análise e documentação de código",
        "model_config": {
            "provider": "openai",
            "model_name": "gpt-4",
            "temperature": 0.2,
            "max_tokens": 3000
        },
        "capabilities": [
            "analyze_code",
            "generate_documentation",
            "extract_patterns",
            "suggest_improvements"
        ]
    },
    "project_planner": {
        "name": "Planejador de Projeto",
        "description": "Agente especializado em planejamento e estruturação de projetos",
        "model_config": {
            "provider": "openai",
            "model_name": "gpt-4",
            "temperature": 0.5,
            "max_tokens": 2500
        },
        "capabilities": [
            "create_project_structure",
            "generate_roadmap",
            "identify_requirements",
            "suggest_architecture"
        ]
    }
}


# Instância global da configuração
agents_config = AgentsConfig()


def get_agents_config() -> AgentsConfig:
    """Retorna a configuração dos agentes."""
    return agents_config


def get_default_agent_config(agent_type: str) -> Dict[str, Any]:
    """Retorna a configuração padrão para um tipo de agente."""
    return DEFAULT_AGENT_CONFIGS.get(agent_type, DEFAULT_AGENT_CONFIGS["markdown_generator"])