from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime


@dataclass
class GenerateDocumentRequest:
    """DTO para solicitação de geração de documento."""
    prompt: str
    document_type: str = "readme"
    agent_id: Optional[str] = None
    project_name: Optional[str] = None
    additional_context: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.additional_context is None:
            self.additional_context = {}


@dataclass
class ValidatePromptRequest:
    """DTO para validação de prompt."""
    prompt: str
    agent_id: Optional[str] = None
    expected_project_type: Optional[str] = None


@dataclass
class ValidationResultResponse:
    """DTO de resposta da validação."""
    is_valid: bool
    confidence_score: float
    identified_project_type: Optional[str]
    missing_information: List[str]
    suggestions: List[str]
    feedback_message: str
    
    def __post_init__(self):
        if not self.missing_information:
            self.missing_information = []
        if not self.suggestions:
            self.suggestions = []


@dataclass
class ProjectMetadataResponse:
    """DTO de resposta dos metadados do projeto."""
    project_name: str
    project_type: str
    technologies: List[str]
    description: str
    target_audience: Optional[str] = None
    complexity_level: Optional[str] = None
    estimated_duration: Optional[str] = None
    
    def __post_init__(self):
        if not self.technologies:
            self.technologies = []


@dataclass
class DocumentResponse:
    """DTO de resposta do documento."""
    id: str
    title: str
    document_type: str
    content: str
    project_metadata: ProjectMetadataResponse
    validation_result: ValidationResultResponse
    status: str
    agent_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    version: str
    tags: List[str]
    word_count: int
    is_complete: bool
    
    def __post_init__(self):
        if not self.tags:
            self.tags = []


@dataclass
class UpdateDocumentRequest:
    """DTO para atualização de documento."""
    document_id: str
    content: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None


@dataclass
class DocumentQualityResponse:
    """DTO de resposta da análise de qualidade do documento."""
    document_id: str
    quality_score: float  # 0.0 to 1.0
    completeness_score: float
    readability_score: float
    structure_score: float
    content_relevance_score: float
    suggestions: List[str]
    issues_found: List[str]
    
    def __post_init__(self):
        if not self.suggestions:
            self.suggestions = []
        if not self.issues_found:
            self.issues_found = []


@dataclass
class ListDocumentsRequest:
    """DTO para listagem de documentos."""
    document_type: Optional[str] = None
    status: Optional[str] = None
    agent_id: Optional[str] = None
    project_name: Optional[str] = None
    tags: Optional[List[str]] = None
    limit: int = 50
    offset: int = 0
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class ListDocumentsResponse:
    """DTO de resposta da listagem de documentos."""
    documents: List[DocumentResponse]
    total: int
    limit: int
    offset: int


@dataclass
class ImprovePromptRequest:
    """DTO para solicitação de melhoria de prompt."""
    original_prompt: str
    validation_result: ValidationResultResponse
    agent_id: Optional[str] = None


@dataclass
class ImprovePromptResponse:
    """DTO de resposta da melhoria de prompt."""
    improved_prompt: str
    improvements_made: List[str]
    explanation: str
    confidence_score: float
    
    def __post_init__(self):
        if not self.improvements_made:
            self.improvements_made = []