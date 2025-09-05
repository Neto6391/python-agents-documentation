from typing import Optional, List

from app.domain.agents.entities.project_document import ProjectDocument, DocumentType, DocumentStatus
from app.domain.agents.ports.document_repository import DocumentRepositoryPort
from app.application.agents.dtos.document_dtos import ListDocumentsRequest, ListDocumentsResponse
from app.application.agents.mappers.document_mapper import DocumentMapper


class ListDocumentsUseCase:
    """Caso de uso para listagem de documentos."""
    
    def __init__(self, document_repository: DocumentRepositoryPort):
        self._document_repository = document_repository
    
    async def execute(self, request: ListDocumentsRequest) -> ListDocumentsResponse:
        """Executa a listagem de documentos com filtros e paginação.
        
        Args:
            request: Parâmetros de listagem
            
        Returns:
            ListDocumentsResponse: Lista paginada de documentos
            
        Raises:
            ValueError: Se os parâmetros forem inválidos
            RuntimeError: Se houver erro na consulta
        """
        try:
            # Validar parâmetros de paginação
            self._validate_pagination_params(request.limit, request.offset)
            
            # Aplicar filtros
            documents = await self._apply_filters(request)
            
            # Contar total de registros
            total = len(documents)
            
            # Aplicar paginação
            paginated_documents = documents[request.offset:request.offset + request.limit]
            
            # Converter para response
            return DocumentMapper.entities_to_list_response(
                documents=paginated_documents,
                total=total,
                limit=request.limit,
                offset=request.offset
            )
            
        except ValueError as e:
            raise e
        except Exception as e:
            raise RuntimeError(f"Erro ao listar documentos: {str(e)}")
    
    async def list_by_agent(self, agent_id: str) -> List[ProjectDocument]:
        """Lista documentos por agente.
        
        Args:
            agent_id: ID do agente
            
        Returns:
            List[ProjectDocument]: Lista de documentos do agente
        """
        try:
            return await self._document_repository.find_by_agent_id(agent_id)
        except Exception as e:
            raise RuntimeError(f"Erro ao listar documentos por agente: {str(e)}")
    
    async def list_by_project(self, project_name: str) -> List[ProjectDocument]:
        """Lista documentos por nome do projeto.
        
        Args:
            project_name: Nome do projeto
            
        Returns:
            List[ProjectDocument]: Lista de documentos do projeto
        """
        try:
            return await self._document_repository.find_by_project_name(project_name)
        except Exception as e:
            raise RuntimeError(f"Erro ao listar documentos por projeto: {str(e)}")
    
    async def search_by_tags(self, tags: List[str]) -> List[ProjectDocument]:
        """Busca documentos por tags.
        
        Args:
            tags: Lista de tags para busca
            
        Returns:
            List[ProjectDocument]: Lista de documentos com as tags
        """
        try:
            return await self._document_repository.search_by_tags(tags)
        except Exception as e:
            raise RuntimeError(f"Erro ao buscar documentos por tags: {str(e)}")
    
    async def _apply_filters(self, request: ListDocumentsRequest) -> List[ProjectDocument]:
        """Aplica filtros na consulta de documentos.
        
        Args:
            request: Parâmetros de filtro
            
        Returns:
            List[ProjectDocument]: Lista filtrada de documentos
        """
        # Se não há filtros, retornar todos
        if not any([
            request.document_type, 
            request.status, 
            request.agent_id,
            request.project_name,
            request.tags
        ]):
            return await self._document_repository.list_all()
        
        # Aplicar filtros específicos
        documents = await self._document_repository.list_all()
        
        if request.document_type:
            doc_type = DocumentType(request.document_type)
            documents = [d for d in documents if d.document_type == doc_type]
        
        if request.status:
            status = DocumentStatus(request.status)
            documents = [d for d in documents if d.status == status]
        
        if request.agent_id:
            documents = [d for d in documents if d.agent_id == request.agent_id]
        
        if request.project_name:
            project_filter = request.project_name.lower()
            documents = [
                d for d in documents 
                if project_filter in d.project_metadata.project_name.lower()
            ]
        
        if request.tags:
            # Documentos que contêm pelo menos uma das tags
            documents = [
                d for d in documents 
                if any(tag in d.tags for tag in request.tags)
            ]
        
        return documents
    
    def _validate_pagination_params(self, limit: int, offset: int) -> None:
        """Valida parâmetros de paginação.
        
        Args:
            limit: Limite de registros por página
            offset: Offset para paginação
            
        Raises:
            ValueError: Se os parâmetros forem inválidos
        """
        if limit <= 0:
            raise ValueError("Limit deve ser maior que 0")
        
        if limit > 100:
            raise ValueError("Limit não pode ser maior que 100")
        
        if offset < 0:
            raise ValueError("Offset deve ser maior ou igual a 0")