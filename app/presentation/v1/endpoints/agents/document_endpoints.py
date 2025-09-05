from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import inject, Provide

from app.core.di.container import Container
from app.core.security.api_key import api_key_auth
from app.application.agents.use_cases.generate_document_use_case import GenerateDocumentUseCase
from app.application.agents.use_cases.list_documents_use_case import ListDocumentsUseCase
from app.application.agents.dtos.document_dtos import (
    GenerateDocumentRequest,
    ValidatePromptRequest,
    ValidationResultResponse,
    ProjectMetadataResponse,
    DocumentResponse,
    UpdateDocumentRequest,
    DocumentQualityResponse,
    ListDocumentsRequest,
    ListDocumentsResponse,
    ImprovePromptRequest,
    ImprovePromptResponse
)
from app.domain.agents.entities.project_document import DocumentStatus

router = APIRouter(tags=["documents"])


@router.post(
    "/generate",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Gerar documento",
    description="Gera um documento de projeto baseado no prompt fornecido"
)
@inject
async def generate_document(
    request: GenerateDocumentRequest,
    api_key: str = Depends(api_key_auth),
    generate_document_use_case: GenerateDocumentUseCase = Depends(
        Provide[Container.generate_document_use_case]
    )
) -> DocumentResponse:
    """Gera um documento de projeto."""
    try:
        return await generate_document_use_case.execute(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/validate-prompt",
    response_model=ValidationResultResponse,
    summary="Validar prompt",
    description="Valida se um prompt contém informações suficientes para gerar documentação"
)
@inject
async def validate_prompt(
    request: ValidatePromptRequest,
    api_key: str = Depends(api_key_auth),
    generate_document_use_case: GenerateDocumentUseCase = Depends(
        Provide[Container.generate_document_use_case]
    )
) -> ValidationResultResponse:
    """Valida um prompt para geração de documentação."""
    try:
        return await generate_document_use_case.validate_prompt_only(
            prompt=request.prompt,
            agent_id=request.agent_id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/extract-metadata",
    response_model=ProjectMetadataResponse,
    summary="Extrair metadados",
    description="Extrai metadados do projeto a partir do prompt"
)
@inject
async def extract_metadata(
    request: ValidatePromptRequest,
    api_key: str = Depends(api_key_auth),
    generate_document_use_case: GenerateDocumentUseCase = Depends(
        Provide[Container.generate_document_use_case]
    )
) -> ProjectMetadataResponse:
    """Extrai metadados do projeto a partir do prompt."""
    try:
        return await generate_document_use_case.extract_metadata_only(
            prompt=request.prompt,
            agent_id=request.agent_id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/",
    response_model=ListDocumentsResponse,
    summary="Listar documentos",
    description="Lista documentos com filtros e paginação"
)
@inject
async def list_documents(
    limit: int = 10,
    offset: int = 0,
    document_type: str = None,
    status: str = None,
    agent_id: str = None,
    project_name: str = None,
    tags: List[str] = None,
    api_key: str = Depends(api_key_auth),
    list_documents_use_case: ListDocumentsUseCase = Depends(
        Provide[Container.list_documents_use_case]
    )
) -> ListDocumentsResponse:
    """Lista documentos com filtros opcionais."""
    try:
        request = ListDocumentsRequest(
            limit=limit,
            offset=offset,
            document_type=document_type,
            status=status,
            agent_id=agent_id,
            project_name=project_name,
            tags=tags or []
        )
        return await list_documents_use_case.execute(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Obter documento por ID",
    description="Obtém detalhes de um documento específico"
)
@inject
async def get_document(
    document_id: str,
    api_key: str = Depends(api_key_auth),
    document_repository = Depends(Provide[Container.document_repository])
) -> DocumentResponse:
    """Obtém um documento por ID."""
    try:
        from app.application.agents.mappers.document_mapper import DocumentMapper
        
        document = await document_repository.find_by_id(document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Documento com ID '{document_id}' não encontrado"
            )
        
        return DocumentMapper.entity_to_response(document)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Atualizar documento",
    description="Atualiza o conteúdo ou status de um documento"
)
@inject
async def update_document(
    document_id: str,
    request: UpdateDocumentRequest,
    api_key: str = Depends(api_key_auth),
    document_repository = Depends(Provide[Container.document_repository])
) -> DocumentResponse:
    """Atualiza um documento."""
    try:
        from app.application.agents.mappers.document_mapper import DocumentMapper
        
        # Verificar se o documento existe
        document = await document_repository.find_by_id(document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Documento com ID '{document_id}' não encontrado"
            )
        
        # Atualizar conteúdo se fornecido
        if request.content is not None:
            document = await document_repository.update_content(document_id, request.content)
        
        # Atualizar status se fornecido
        if request.status is not None:
            new_status = DocumentStatus(request.status)
            document = await document_repository.update_status(document_id, new_status)
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Falha ao atualizar documento"
            )
        
        return DocumentMapper.entity_to_response(document)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Dados inválidos: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar documento",
    description="Remove um documento do sistema"
)
@inject
async def delete_document(
    document_id: str,
    api_key: str = Depends(api_key_auth),
    document_repository = Depends(Provide[Container.document_repository])
):
    """Remove um documento do sistema."""
    try:
        # Verificar se o documento existe
        document = await document_repository.find_by_id(document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Documento com ID '{document_id}' não encontrado"
            )
        
        # Remover do repositório
        success = await document_repository.delete(document_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Falha ao deletar documento"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/{document_id}/analyze-quality",
    response_model=DocumentQualityResponse,
    summary="Analisar qualidade do documento",
    description="Analisa a qualidade e completude de um documento"
)
@inject
async def analyze_document_quality(
    document_id: str,
    api_key: str = Depends(api_key_auth),
    document_repository = Depends(Provide[Container.document_repository]),
    agent_service = Depends(Provide[Container.agent_service])
) -> DocumentQualityResponse:
    """Analisa a qualidade de um documento."""
    try:
        from app.application.agents.mappers.document_mapper import DocumentMapper
        
        # Verificar se o documento existe
        document = await document_repository.find_by_id(document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Documento com ID '{document_id}' não encontrado"
            )
        
        # Analisar qualidade usando o agente
        quality_data = await agent_service.analyze_document_quality(
            content=document.content,
            agent_id=document.agent_id
        )
        
        return DocumentMapper.create_quality_response(document_id, quality_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/improve-prompt",
    response_model=ImprovePromptResponse,
    summary="Melhorar prompt",
    description="Melhora um prompt para gerar documentação mais completa"
)
@inject
async def improve_prompt(
    request: ImprovePromptRequest,
    api_key: str = Depends(api_key_auth),
    agent_service = Depends(Provide[Container.agent_service])
) -> ImprovePromptResponse:
    """Melhora um prompt para geração de documentação."""
    try:
        improved_prompt = await agent_service.improve_prompt(
            prompt=request.original_prompt,
            agent_id=request.agent_id
        )
        
        return ImprovePromptResponse(
            original_prompt=request.original_prompt,
            improved_prompt=improved_prompt,
            agent_id=request.agent_id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/by-agent/{agent_id}",
    response_model=List[DocumentResponse],
    summary="Listar documentos por agente",
    description="Lista todos os documentos gerados por um agente específico"
)
@inject
async def list_documents_by_agent(
    agent_id: str,
    api_key: str = Depends(api_key_auth),
    list_documents_use_case: ListDocumentsUseCase = Depends(
        Provide[Container.list_documents_use_case]
    )
) -> List[DocumentResponse]:
    """Lista documentos gerados por um agente específico."""
    try:
        from app.application.agents.mappers.document_mapper import DocumentMapper
        
        documents = await list_documents_use_case.list_by_agent(agent_id)
        return [DocumentMapper.entity_to_response(doc) for doc in documents]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/by-project/{project_name}",
    response_model=List[DocumentResponse],
    summary="Listar documentos por projeto",
    description="Lista todos os documentos de um projeto específico"
)
@inject
async def list_documents_by_project(
    project_name: str,
    api_key: str = Depends(api_key_auth),
    list_documents_use_case: ListDocumentsUseCase = Depends(
        Provide[Container.list_documents_use_case]
    )
) -> List[DocumentResponse]:
    """Lista documentos de um projeto específico."""
    try:
        from app.application.agents.mappers.document_mapper import DocumentMapper
        
        documents = await list_documents_use_case.list_by_project(project_name)
        return [DocumentMapper.entity_to_response(doc) for doc in documents]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )