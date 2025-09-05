import uuid
from typing import Optional

from app.domain.agents.entities.project_document import ProjectDocument, DocumentType
from app.domain.agents.ports.agent_repository import AgentRepositoryPort
from app.domain.agents.ports.document_repository import DocumentRepositoryPort
from app.domain.agents.ports.agent_service import AgentServicePort
from app.application.agents.dtos.document_dtos import (
    GenerateDocumentRequest,
    DocumentResponse,
    ValidationResultResponse,
    ProjectMetadataResponse
)
from app.application.agents.mappers.document_mapper import DocumentMapper


class GenerateDocumentUseCase:
    """Caso de uso para geração de documentos de projeto."""
    
    def __init__(
        self,
        agent_repository: AgentRepositoryPort,
        document_repository: DocumentRepositoryPort,
        agent_service: AgentServicePort
    ):
        self._agent_repository = agent_repository
        self._document_repository = document_repository
        self._agent_service = agent_service
    
    async def execute(self, request: GenerateDocumentRequest) -> DocumentResponse:
        """Executa a geração de um documento de projeto.
        
        Args:
            request: Dados para geração do documento
            
        Returns:
            DocumentResponse: Documento gerado
            
        Raises:
            ValueError: Se os dados de entrada forem inválidos
            RuntimeError: Se houver erro na geração do documento
        """
        try:
            # Validar se o agente existe
            agent = await self._agent_repository.find_by_id(request.agent_id)
            if not agent:
                raise ValueError(f"Agente com ID '{request.agent_id}' não encontrado")
            
            # Validar prompt e extrair metadados
            validation_result = await self._agent_service.validate_prompt(
                prompt=request.prompt,
                agent_id=request.agent_id
            )
            
            # Se o prompt não for válido, retornar erro com sugestões
            if not validation_result.is_valid:
                raise ValueError(
                    f"Prompt inválido: {validation_result.suggestions}"
                )
            
            # Extrair metadados do projeto
            project_metadata = await self._agent_service.extract_project_metadata(
                prompt=request.prompt,
                agent_id=request.agent_id
            )
            
            # Gerar conteúdo do documento
            content = await self._agent_service.generate_markdown_document(
                prompt=request.prompt,
                document_type=DocumentType(request.document_type),
                project_metadata=project_metadata,
                agent_id=request.agent_id,
                custom_instructions=None
            )
            
            # Criar entidade do documento
            document_id = str(uuid.uuid4())
            document = DocumentMapper.create_document_entity(
                document_id=document_id,
                request=request,
                content=content,
                metadata=project_metadata,
                validation=validation_result,
                agent_id=request.agent_id
            )
            
            # Tags serão definidas pelo sistema automaticamente
            
            # Salvar documento
            saved_document = await self._document_repository.save(document)
            
            # Converter para response
            return DocumentMapper.entity_to_response(saved_document)
            
        except ValueError as e:
            raise e
        except Exception as e:
            raise RuntimeError(f"Erro ao gerar documento: {str(e)}")
    
    async def validate_prompt_only(
        self, 
        prompt: str, 
        agent_id: str
    ) -> ValidationResultResponse:
        """Valida apenas o prompt sem gerar o documento.
        
        Args:
            prompt: Prompt a ser validado
            agent_id: ID do agente para validação
            
        Returns:
            ValidationResultResponse: Resultado da validação
            
        Raises:
            ValueError: Se o agente não for encontrado
            RuntimeError: Se houver erro na validação
        """
        try:
            # Validar se o agente existe
            agent = await self._agent_repository.find_by_id(agent_id)
            if not agent:
                raise ValueError(f"Agente com ID '{agent_id}' não encontrado")
            
            # Validar prompt
            validation_result = await self._agent_service.validate_prompt(
                prompt=prompt,
                agent_id=agent_id
            )
            
            return DocumentMapper.validation_result_to_response(validation_result)
            
        except ValueError as e:
            raise e
        except Exception as e:
            raise RuntimeError(f"Erro ao validar prompt: {str(e)}")
    
    async def extract_metadata_only(
        self, 
        prompt: str, 
        agent_id: str
    ) -> ProjectMetadataResponse:
        """Extrai apenas os metadados do projeto sem gerar o documento.
        
        Args:
            prompt: Prompt para extração de metadados
            agent_id: ID do agente para extração
            
        Returns:
            ProjectMetadataResponse: Metadados extraídos
            
        Raises:
            ValueError: Se o agente não for encontrado
            RuntimeError: Se houver erro na extração
        """
        try:
            # Validar se o agente existe
            agent = await self._agent_repository.find_by_id(agent_id)
            if not agent:
                raise ValueError(f"Agente com ID '{agent_id}' não encontrado")
            
            # Extrair metadados
            project_metadata = await self._agent_service.extract_project_metadata(
                prompt=prompt,
                agent_id=agent_id
            )
            
            return DocumentMapper.project_metadata_to_response(project_metadata)
            
        except ValueError as e:
            raise e
        except Exception as e:
            raise RuntimeError(f"Erro ao extrair metadados: {str(e)}")