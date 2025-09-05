from typing import Dict, List, Optional
from datetime import datetime

from app.domain.agents.entities.project_document import ProjectDocument, DocumentType, DocumentStatus
from app.domain.agents.ports.document_repository import DocumentRepositoryPort


class MemoryDocumentRepository(DocumentRepositoryPort):
    """Implementação em memória do repositório de documentos."""
    
    def __init__(self):
        self._documents: Dict[str, ProjectDocument] = {}
    
    async def save(self, document: ProjectDocument) -> ProjectDocument:
        """Salva um documento no repositório."""
        document.updated_at = datetime.utcnow()
        self._documents[document.id] = document
        return document
    
    async def find_by_id(self, document_id: str) -> Optional[ProjectDocument]:
        """Busca um documento por ID."""
        return self._documents.get(document_id)
    
    async def find_by_type(self, document_type: DocumentType) -> List[ProjectDocument]:
        """Busca documentos por tipo."""
        return [
            doc for doc in self._documents.values() 
            if doc.document_type == document_type
        ]
    
    async def find_by_agent_id(self, agent_id: str) -> List[ProjectDocument]:
        """Busca documentos por ID do agente."""
        return [
            doc for doc in self._documents.values() 
            if doc.agent_id == agent_id
        ]
    
    async def find_by_status(self, status: DocumentStatus) -> List[ProjectDocument]:
        """Busca documentos por status."""
        return [
            doc for doc in self._documents.values() 
            if doc.status == status
        ]
    
    async def find_by_project_name(self, project_name: str) -> List[ProjectDocument]:
        """Busca documentos por nome do projeto."""
        project_name_lower = project_name.lower()
        return [
            doc for doc in self._documents.values() 
            if doc.project_metadata.project_name.lower() == project_name_lower
        ]
    
    async def update_content(self, document_id: str, content: str) -> Optional[ProjectDocument]:
        """Atualiza o conteúdo de um documento."""
        document = self._documents.get(document_id)
        if document:
            document.content = content
            document.updated_at = datetime.utcnow()
            document.version += 1
            return document
        return None
    
    async def update_status(self, document_id: str, status: DocumentStatus) -> Optional[ProjectDocument]:
        """Atualiza o status de um documento."""
        document = self._documents.get(document_id)
        if document:
            document.status = status
            document.updated_at = datetime.utcnow()
            return document
        return None
    
    async def delete(self, document_id: str) -> bool:
        """Remove um documento do repositório."""
        if document_id in self._documents:
            del self._documents[document_id]
            return True
        return False
    
    async def list_all(self) -> List[ProjectDocument]:
        """Lista todos os documentos."""
        return list(self._documents.values())
    
    async def search_by_tags(self, tags: List[str]) -> List[ProjectDocument]:
        """Busca documentos que contêm pelo menos uma das tags."""
        if not tags:
            return []
        
        tags_lower = [tag.lower() for tag in tags]
        return [
            doc for doc in self._documents.values() 
            if any(
                tag.lower() in tags_lower 
                for tag in doc.tags
            )
        ]
    
    async def find_by_title_pattern(self, pattern: str) -> List[ProjectDocument]:
        """Busca documentos por padrão no título."""
        pattern_lower = pattern.lower()
        return [
            doc for doc in self._documents.values() 
            if pattern_lower in doc.title.lower()
        ]
    
    async def find_recent_documents(self, limit: int = 10) -> List[ProjectDocument]:
        """Busca documentos mais recentes."""
        documents = list(self._documents.values())
        documents.sort(key=lambda x: x.updated_at, reverse=True)
        return documents[:limit]
    
    async def count_by_status(self, status: DocumentStatus) -> int:
        """Conta documentos por status."""
        return len([
            doc for doc in self._documents.values() 
            if doc.status == status
        ])
    
    async def count_by_type(self, document_type: DocumentType) -> int:
        """Conta documentos por tipo."""
        return len([
            doc for doc in self._documents.values() 
            if doc.document_type == document_type
        ])
    
    async def count_by_agent(self, agent_id: str) -> int:
        """Conta documentos por agente."""
        return len([
            doc for doc in self._documents.values() 
            if doc.agent_id == agent_id
        ])
    
    def clear(self) -> None:
        """Limpa todos os documentos (útil para testes)."""
        self._documents.clear()
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas do repositório."""
        total = len(self._documents)
        by_status = {}
        by_type = {}
        by_agent = {}
        total_words = 0
        
        for doc in self._documents.values():
            # Contar por status
            status_key = doc.status.value
            by_status[status_key] = by_status.get(status_key, 0) + 1
            
            # Contar por tipo
            type_key = doc.document_type.value
            by_type[type_key] = by_type.get(type_key, 0) + 1
            
            # Contar por agente
            agent_key = doc.agent_id or "unknown"
            by_agent[agent_key] = by_agent.get(agent_key, 0) + 1
            
            # Somar palavras
            total_words += doc.get_word_count()
        
        return {
            "total_documents": total,
            "total_words": total_words,
            "by_status": by_status,
            "by_type": by_type,
            "by_agent": by_agent
        }