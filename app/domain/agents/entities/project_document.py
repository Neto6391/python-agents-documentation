from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime


class DocumentType(Enum):
    """Tipos de documentos de projeto."""
    README = "readme"
    API_DOCUMENTATION = "api_documentation"
    TECHNICAL_SPECIFICATION = "technical_specification"
    USER_GUIDE = "user_guide"
    ARCHITECTURE_DOCUMENT = "architecture_document"
    PROJECT_PROPOSAL = "project_proposal"
    REQUIREMENTS_DOCUMENT = "requirements_document"


class DocumentStatus(Enum):
    """Status do documento."""
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    PUBLISHED = "published"


@dataclass
class ProjectMetadata:
    """Metadados do projeto extraídos do prompt."""
    project_name: str
    project_type: str  # web_app, api, mobile_app, etc.
    technologies: List[str]
    description: str
    target_audience: Optional[str] = None
    complexity_level: Optional[str] = None  # simple, medium, complex
    estimated_duration: Optional[str] = None
    
    def __post_init__(self):
        if not self.technologies:
            self.technologies = []


@dataclass
class ValidationResult:
    """Resultado da validação do prompt."""
    is_valid: bool
    confidence_score: float  # 0.0 to 1.0
    identified_project_type: Optional[str]
    missing_information: List[str]
    suggestions: List[str]
    
    def __post_init__(self):
        if not self.missing_information:
            self.missing_information = []
        if not self.suggestions:
            self.suggestions = []


@dataclass
class ProjectDocument:
    """Entidade principal do documento de projeto."""
    id: str
    title: str
    document_type: DocumentType
    content: str  # Conteúdo em Markdown
    project_metadata: ProjectMetadata
    validation_result: ValidationResult
    status: DocumentStatus = DocumentStatus.DRAFT
    agent_id: str = None  # ID do agente que gerou o documento
    created_at: datetime = None
    updated_at: datetime = None
    version: str = "1.0.0"
    tags: List[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
        if self.tags is None:
            self.tags = []
    
    def update_content(self, content: str) -> None:
        """Atualiza o conteúdo do documento."""
        self.content = content
        self.updated_at = datetime.utcnow()
    
    def update_status(self, status: DocumentStatus) -> None:
        """Atualiza o status do documento."""
        self.status = status
        self.updated_at = datetime.utcnow()
    
    def add_tag(self, tag: str) -> None:
        """Adiciona uma tag ao documento."""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.utcnow()
    
    def get_word_count(self) -> int:
        """Retorna a contagem de palavras do documento."""
        return len(self.content.split())
    
    def is_complete(self) -> bool:
        """Verifica se o documento está completo."""
        return (
            bool(self.content.strip()) and
            self.validation_result.is_valid and
            self.validation_result.confidence_score >= 0.7
        )