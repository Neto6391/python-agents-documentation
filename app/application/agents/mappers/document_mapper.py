from typing import List

from app.domain.agents.entities.project_document import (
    ProjectDocument,
    ProjectMetadata,
    ValidationResult,
    DocumentType,
    DocumentStatus
)
from app.application.agents.dtos.document_dtos import (
    GenerateDocumentRequest,
    DocumentResponse,
    ProjectMetadataResponse,
    ValidationResultResponse,
    DocumentQualityResponse,
    ListDocumentsResponse
)


class DocumentMapper:
    """Mapper para conversão entre entidades de documento e DTOs."""
    
    @staticmethod
    def validation_result_to_response(validation: ValidationResult) -> ValidationResultResponse:
        """Converte ValidationResult para ValidationResultResponse."""
        feedback_message = "Prompt válido para geração de documento." if validation.is_valid else "Prompt precisa de melhorias."
        
        return ValidationResultResponse(
            is_valid=validation.is_valid,
            confidence_score=validation.confidence_score,
            identified_project_type=validation.identified_project_type,
            missing_information=validation.missing_information.copy(),
            suggestions=validation.suggestions.copy(),
            feedback_message=feedback_message
        )
    
    @staticmethod
    def project_metadata_to_response(metadata: ProjectMetadata) -> ProjectMetadataResponse:
        """Converte ProjectMetadata para ProjectMetadataResponse."""
        return ProjectMetadataResponse(
            project_name=metadata.project_name,
            project_type=metadata.project_type,
            technologies=metadata.technologies.copy(),
            description=metadata.description,
            target_audience=metadata.target_audience,
            complexity_level=metadata.complexity_level,
            estimated_duration=metadata.estimated_duration
        )
    
    @staticmethod
    def entity_to_response(document: ProjectDocument) -> DocumentResponse:
        """Converte entidade ProjectDocument para DocumentResponse."""
        return DocumentResponse(
            id=document.id,
            title=document.title,
            document_type=document.document_type.value,
            content=document.content,
            project_metadata=DocumentMapper.project_metadata_to_response(document.project_metadata),
            validation_result=DocumentMapper.validation_result_to_response(document.validation_result),
            status=document.status.value,
            agent_id=document.agent_id,
            created_at=document.created_at,
            updated_at=document.updated_at,
            version=document.version,
            tags=document.tags.copy(),
            word_count=document.get_word_count(),
            is_complete=document.is_complete()
        )
    
    @staticmethod
    def response_to_validation_result(response: ValidationResultResponse) -> ValidationResult:
        """Converte ValidationResultResponse para ValidationResult."""
        return ValidationResult(
            is_valid=response.is_valid,
            confidence_score=response.confidence_score,
            identified_project_type=response.identified_project_type,
            missing_information=response.missing_information.copy(),
            suggestions=response.suggestions.copy()
        )
    
    @staticmethod
    def response_to_project_metadata(response: ProjectMetadataResponse) -> ProjectMetadata:
        """Converte ProjectMetadataResponse para ProjectMetadata."""
        return ProjectMetadata(
            project_name=response.project_name,
            project_type=response.project_type,
            technologies=response.technologies.copy(),
            description=response.description,
            target_audience=response.target_audience,
            complexity_level=response.complexity_level,
            estimated_duration=response.estimated_duration
        )
    
    @staticmethod
    def create_document_entity(
        document_id: str,
        request: GenerateDocumentRequest,
        content: str,
        metadata: ProjectMetadata,
        validation: ValidationResult,
        agent_id: str = None
    ) -> ProjectDocument:
        """Cria uma entidade ProjectDocument a partir dos dados."""
        title = f"{metadata.project_name} - {request.document_type.replace('_', ' ').title()}"
        
        return ProjectDocument(
            id=document_id,
            title=title,
            document_type=DocumentType(request.document_type),
            content=content,
            project_metadata=metadata,
            validation_result=validation,
            status=DocumentStatus.DRAFT,
            agent_id=agent_id or request.agent_id
        )
    
    @staticmethod
    def entities_to_list_response(
        documents: List[ProjectDocument],
        total: int,
        limit: int,
        offset: int
    ) -> ListDocumentsResponse:
        """Converte lista de entidades ProjectDocument para ListDocumentsResponse."""
        document_responses = [
            DocumentMapper.entity_to_response(document) for document in documents
        ]
        
        return ListDocumentsResponse(
            documents=document_responses,
            total=total,
            limit=limit,
            offset=offset
        )
    
    @staticmethod
    def create_quality_response(
        document_id: str,
        quality_data: dict
    ) -> DocumentQualityResponse:
        """Cria DocumentQualityResponse a partir dos dados de qualidade."""
        return DocumentQualityResponse(
            document_id=document_id,
            quality_score=quality_data.get("quality_score", 0.0),
            completeness_score=quality_data.get("completeness_score", 0.0),
            readability_score=quality_data.get("readability_score", 0.0),
            structure_score=quality_data.get("structure_score", 0.0),
            content_relevance_score=quality_data.get("content_relevance_score", 0.0),
            suggestions=quality_data.get("suggestions", []),
            issues_found=quality_data.get("issues_found", [])
        )