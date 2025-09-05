from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.agents.entities.project_document import (
    ProjectDocument, 
    DocumentType, 
    DocumentStatus
)


class DocumentRepositoryPort(ABC):
    """Port para repositório de documentos de projeto."""
    
    @abstractmethod
    async def save(self, document: ProjectDocument) -> ProjectDocument:
        """Salva um documento."""
        pass
    
    @abstractmethod
    async def find_by_id(self, document_id: str) -> Optional[ProjectDocument]:
        """Busca um documento por ID."""
        pass
    
    @abstractmethod
    async def find_by_type(self, document_type: DocumentType) -> List[ProjectDocument]:
        """Busca documentos por tipo."""
        pass
    
    @abstractmethod
    async def find_by_agent_id(self, agent_id: str) -> List[ProjectDocument]:
        """Busca documentos gerados por um agente específico."""
        pass
    
    @abstractmethod
    async def find_by_status(self, status: DocumentStatus) -> List[ProjectDocument]:
        """Busca documentos por status."""
        pass
    
    @abstractmethod
    async def find_by_project_name(self, project_name: str) -> List[ProjectDocument]:
        """Busca documentos por nome do projeto."""
        pass
    
    @abstractmethod
    async def update_content(self, document_id: str, content: str) -> bool:
        """Atualiza o conteúdo de um documento."""
        pass
    
    @abstractmethod
    async def update_status(self, document_id: str, status: DocumentStatus) -> bool:
        """Atualiza o status de um documento."""
        pass
    
    @abstractmethod
    async def delete(self, document_id: str) -> bool:
        """Remove um documento."""
        pass
    
    @abstractmethod
    async def list_all(self) -> List[ProjectDocument]:
        """Lista todos os documentos."""
        pass
    
    @abstractmethod
    async def search_by_tags(self, tags: List[str]) -> List[ProjectDocument]:
        """Busca documentos por tags."""
        pass