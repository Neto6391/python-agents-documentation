import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from agno.agent import Agent as AgnoAgent
from agno.models.openai import OpenAIChat
from agno.models.anthropic import Claude

from app.domain.agents.entities.agent import AgentType, AgentConfig
from app.domain.agents.entities.project_document import (
    ProjectMetadata,
    ValidationResult,
    DocumentType
)
from app.domain.agents.ports.agent_service import AgentServicePort
from app.core.config.settings import settings


logger = logging.getLogger(__name__)


class AgnoAgentService(AgentServicePort):
    """Implementação do serviço de agentes usando o framework Agno."""
    
    def __init__(self):
        """Inicializa o serviço Agno."""
        self.logger = logging.getLogger(__name__)
        self._agents: Dict[str, AgnoAgent] = {}
        self._agent_configs: Dict[str, AgentConfig] = {}

    def reset(self):
        """Reseta o estado interno do serviço para testes."""
        self._agents = {}
        self._agent_configs = {}
    
    async def create_agent(
        self, 
        agent_id: str, 
        agent_type: AgentType, 
        config: AgentConfig
    ) -> Dict[str, Any]:
        """Cria um agente no framework Agno."""
        try:
            # Configurar modelo baseado no provider
            model = self._create_model(config)
            
            # Criar agente Agno com instruções
            instructions = self._get_agent_instructions(agent_type, config.instructions)
            agno_agent = AgnoAgent(
                model=model,
                instructions=instructions,
                tools=config.tools or [],
                markdown=True
            )
            
            # Armazenar referências
            self._agents[agent_id] = agno_agent
            self._agent_configs[agent_id] = config
            
            logger.info(f"Agente {agent_id} criado com sucesso no Agno")
            
            return {
                "id": agent_id,
                "agno_agent_id": agent_id,  # Usar o agent_id como identificador
                "status": "created",
                "model_provider": config.model_provider,
                "model_id": config.model_id
            }
            
        except Exception as e:
            logger.error(f"Erro ao criar agente {agent_id}: {str(e)}")
            raise RuntimeError(f"Falha na criação do agente: {str(e)}")
    
    async def validate_prompt(self, prompt: str, agent_id: str) -> ValidationResult:
        """Valida um prompt para identificar se contém contexto de projeto."""
        try:
            agno_agent = self._get_agent(agent_id)
            
            validation_prompt = f"""
            Analise o seguinte prompt e determine se ele contém informações suficientes para gerar documentação de projeto:
            
            PROMPT: {prompt}
            
            Responda em formato JSON com:
            {{
                "is_valid": boolean,
                "confidence_score": float (0.0-1.0),
                "identified_project_type": string,
                "missing_information": [lista de informações faltantes],
                "suggestions": [lista de sugestões para melhorar o prompt]
            }}
            """
            
            response = agno_agent.run(validation_prompt)
            result_data = self._parse_json_response(response)
            
            return ValidationResult(
                is_valid=result_data.get("is_valid", False),
                confidence_score=result_data.get("confidence_score", 0.0),
                identified_project_type=result_data.get("identified_project_type", "unknown"),
                missing_information=result_data.get("missing_information", []),
                suggestions=result_data.get("suggestions", [])
            )
            
        except Exception as e:
            logger.error(f"Erro ao validar prompt: {str(e)}")
            # Retornar validação padrão em caso de erro
            return ValidationResult(
                is_valid=False,
                confidence_score=0.0,
                identified_project_type="unknown",
                missing_information=["Erro na validação do prompt"],
                suggestions=["Tente reformular o prompt com mais detalhes sobre o projeto"]
            )
    
    async def extract_project_metadata(
        self, 
        prompt: str, 
        agent_id: str
    ) -> ProjectMetadata:
        """Extrai metadados do projeto a partir do prompt."""
        try:
            agno_agent = self._get_agent(agent_id)
            
            extraction_prompt = f"""
            Extraia os metadados do projeto a partir do seguinte prompt:
            
            PROMPT: {prompt}
            
            Responda em formato JSON com:
            {{
                "project_name": string,
                "project_type": string,
                "technologies": [lista de tecnologias],
                "description": string,
                "target_audience": string,
                "complexity_level": string ("beginner", "intermediate", "advanced"),
                "estimated_duration": string
            }}
            """
            
            response = agno_agent.run(extraction_prompt)
            result_data = self._parse_json_response(response)
            
            return ProjectMetadata(
                project_name=result_data.get("project_name", "Projeto Sem Nome"),
                project_type=result_data.get("project_type", "unknown"),
                technologies=result_data.get("technologies", []),
                description=result_data.get("description", ""),
                target_audience=result_data.get("target_audience", "general"),
                complexity_level=result_data.get("complexity_level", "intermediate"),
                estimated_duration=result_data.get("estimated_duration", "unknown")
            )
            
        except Exception as e:
            logger.error(f"Erro ao extrair metadados: {str(e)}")
            # Retornar metadados padrão em caso de erro
            return ProjectMetadata(
                project_name="Projeto Sem Nome",
                project_type="unknown",
                technologies=[],
                description="Erro na extração de metadados",
                target_audience="general",
                complexity_level="intermediate",
                estimated_duration="unknown"
            )
    
    async def generate_markdown_document(
        self,
        prompt: str,
        document_type: DocumentType,
        project_metadata: ProjectMetadata,
        agent_id: str,
        custom_instructions: Optional[List[str]] = None
    ) -> str:
        """Gera documento markdown usando o agente."""
        try:
            agno_agent = self._get_agent(agent_id)
            
            # Construir prompt de geração
            generation_prompt = self._build_generation_prompt(
                prompt, document_type, project_metadata, custom_instructions
            )
            
            response = agno_agent.run(generation_prompt)
            
            # Extrair conteúdo Markdown da resposta
            content = self._extract_markdown_content(response)
            
            logger.info(f"Documento {document_type.value} gerado com sucesso")
            return content
            
        except Exception as e:
            logger.error(f"Erro ao gerar documento: {str(e)}")
            raise RuntimeError(f"Falha na geração do documento: {str(e)}")
    
    async def improve_prompt(self, prompt: str, agent_id: str) -> str:
        """Melhora um prompt para gerar melhor documentação."""
        try:
            agno_agent = self._get_agent(agent_id)
            
            improvement_prompt = f"""
            Melhore o seguinte prompt para gerar documentação de projeto mais completa e detalhada:
            
            PROMPT ORIGINAL: {prompt}
            
            Retorne apenas o prompt melhorado, sem explicações adicionais.
            """
            
            response = agno_agent.run(improvement_prompt)
            return response.strip()
            
        except Exception as e:
            logger.error(f"Erro ao melhorar prompt: {str(e)}")
            return prompt  # Retornar prompt original em caso de erro
    
    async def analyze_document_quality(self, content: str, agent_id: str) -> Dict[str, Any]:
        """Analisa a qualidade de um documento gerado."""
        try:
            agno_agent = self._get_agent(agent_id)
            
            analysis_prompt = f"""
            Analise a qualidade do seguinte documento Markdown:
            
            DOCUMENTO:
            {content}
            
            Responda em formato JSON com:
            {{
                "quality_score": float (0.0-1.0),
                "completeness_score": float (0.0-1.0),
                "readability_score": float (0.0-1.0),
                "structure_score": float (0.0-1.0),
                "content_relevance_score": float (0.0-1.0),
                "suggestions": [lista de sugestões de melhoria],
                "issues_found": [lista de problemas encontrados]
            }}
            """
            
            response = agno_agent.run(analysis_prompt)
            return self._parse_json_response(response)
            
        except Exception as e:
            logger.error(f"Erro ao analisar qualidade: {str(e)}")
            return {
                "quality_score": 0.5,
                "completeness_score": 0.5,
                "readability_score": 0.5,
                "structure_score": 0.5,
                "content_relevance_score": 0.5,
                "suggestions": ["Erro na análise de qualidade"],
                "issues_found": ["Não foi possível analisar o documento"]
            }
    
    async def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Obtém o status atual de um agente."""
        try:
            agno_agent = self._get_agent(agent_id)
            config = self._agent_configs.get(agent_id)
            
            return {
                "agent_id": agent_id,
                "agno_agent_id": agent_id,  # Usar o agent_id como identificador
                "status": "active",
                "model_provider": config.model_provider if config else "unknown",
                "last_activity": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter status do agente: {str(e)}")
            return {
                "agent_id": agent_id,
                "status": "error",
                "error": str(e)
            }
    
    async def stop_agent(self, agent_id: str) -> bool:
        """Para um agente."""
        try:
            if agent_id in self._agents:
                # Agno não tem método stop explícito, apenas removemos da memória
                del self._agents[agent_id]
                if agent_id in self._agent_configs:
                    del self._agent_configs[agent_id]
                logger.info(f"Agente {agent_id} parado com sucesso")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Erro ao parar agente: {str(e)}")
            return False
    
    async def restart_agent(self, agent_id: str) -> bool:
        """Reinicia um agente."""
        try:
            config = self._agent_configs.get(agent_id)
            if not config:
                return False
            
            # Parar agente atual
            await self.stop_agent(agent_id)
            
            # Recriar agente
            # Nota: Precisaríamos do agent_type aqui, mas não temos acesso
            # Por enquanto, apenas retornamos False
            return False
            
        except Exception as e:
            logger.error(f"Erro ao reiniciar agente: {str(e)}")
            return False
    
    def _create_model(self, config: AgentConfig):
        """Cria um modelo baseado na configuração."""
        if config.model_provider == "openai":
            return OpenAIChat(id=config.model_id, api_key=settings.openai_api_key)
        elif config.model_provider == "anthropic":
            return Claude(id=config.model_id)
        else:
            raise ValueError(f"Provider {config.model_provider} não suportado")
    
    def _get_agent(self, agent_id: str) -> AgnoAgent:
        """Obtém um agente pelo ID."""
        agent = self._agents.get(agent_id)
        if not agent:
            raise ValueError(f"Agente {agent_id} não encontrado")
        return agent
    
    def _get_agent_instructions(self, agent_type: AgentType, custom_instructions: List[str]) -> List[str]:
        """Obtém instruções específicas para o tipo de agente."""
        base_instructions = {
            AgentType.MARKDOWN_GENERATOR: [
                "Você é um especialista em geração de documentação Markdown.",
                "Sempre gere conteúdo bem estruturado e formatado.",
                "Use cabeçalhos, listas e formatação apropriada.",
                "Inclua exemplos práticos quando relevante."
            ],
            AgentType.PROJECT_ANALYZER: [
                "Você é um analista de projetos especializado.",
                "Analise projetos de forma detalhada e estruturada.",
                "Identifique tecnologias, padrões e melhores práticas.",
                "Forneça insights valiosos sobre arquitetura e implementação."
            ],
            AgentType.DOCUMENT_VALIDATOR: [
                "Você é um validador de documentos especializado.",
                "Analise documentos quanto à qualidade e completude.",
                "Identifique problemas e sugira melhorias.",
                "Foque na clareza e utilidade do conteúdo."
            ]
        }
        
        instructions = base_instructions.get(agent_type, [])
        if custom_instructions:
            instructions.extend(custom_instructions)
        
        return instructions
    
    def _build_generation_prompt(
        self,
        prompt: str,
        document_type: DocumentType,
        project_metadata: ProjectMetadata,
        custom_instructions: Optional[List[str]] = None
    ) -> str:
        """Constrói o prompt de geração de documento."""
        type_templates = {
            DocumentType.README: "Gere um README.md completo e profissional",
            DocumentType.API_DOCUMENTATION: "Gere documentação de API detalhada",
            DocumentType.USER_GUIDE: "Gere um guia do usuário abrangente",
            DocumentType.TECHNICAL_SPECIFICATION: "Gere especificação técnica detalhada",
            DocumentType.INSTALLATION_GUIDE: "Gere guia de instalação passo a passo",
            DocumentType.CHANGELOG: "Gere um changelog estruturado",
            DocumentType.CONTRIBUTING_GUIDE: "Gere guia de contribuição para o projeto"
        }
        
        template = type_templates.get(document_type, "Gere documentação")
        
        generation_prompt = f"""
        {template} para o seguinte projeto:
        
        PROMPT ORIGINAL: {prompt}
        
        METADADOS DO PROJETO:
        - Nome: {project_metadata.project_name}
        - Tipo: {project_metadata.project_type}
        - Tecnologias: {', '.join(project_metadata.technologies)}
        - Descrição: {project_metadata.description}
        - Público-alvo: {project_metadata.target_audience}
        - Nível de complexidade: {project_metadata.complexity_level}
        - Duração estimada: {project_metadata.estimated_duration}
        
        INSTRUÇÕES ADICIONAIS:
        - Use formatação Markdown apropriada
        - Inclua seções bem organizadas
        - Adicione exemplos práticos quando relevante
        - Mantenha linguagem clara e profissional
        """
        
        if custom_instructions:
            generation_prompt += f"\n\nINSTRUÇÕES CUSTOMIZADAS:\n" + "\n".join(f"- {inst}" for inst in custom_instructions)
        
        return generation_prompt
    
    def _extract_markdown_content(self, response_content: str) -> str:
        """Extrai conteúdo Markdown da resposta do agente."""
        # Se a resposta contém blocos de código markdown, extrair apenas o conteúdo
        if "```markdown" in response_content:
            start = response_content.find("```markdown") + 11
            end = response_content.find("```", start)
            if end != -1:
                return response_content[start:end].strip()
        
        # Se contém apenas ```, extrair o conteúdo
        if response_content.count("```") >= 2:
            start = response_content.find("```") + 3
            end = response_content.find("```", start)
            if end != -1:
                return response_content[start:end].strip()
        
        # Caso contrário, retornar o conteúdo completo
        return response_content.strip()
    
    def _extract_content_from_response(self, response) -> str:
        """Extrai conteúdo de uma resposta do agente."""
        try:
            if isinstance(response, str):
                return response.strip()
            else:
                return str(response).strip()
        except Exception as e:
            logger.error(f"Erro ao extrair conteúdo da resposta: {str(e)}")
            return "Erro ao processar resposta do agente"
    
    def _parse_json_response(self, response_content: str) -> Dict[str, Any]:
        """Parseia resposta JSON do agente."""
        import json
        
        try:
            # Tentar extrair JSON da resposta
            if "```json" in response_content:
                start = response_content.find("```json") + 7
                end = response_content.find("```", start)
                if end != -1:
                    json_str = response_content[start:end].strip()
                    return json.loads(json_str)
            
            # Tentar parsear a resposta completa como JSON
            return json.loads(response_content)
            
        except json.JSONDecodeError:
            logger.warning("Falha ao parsear resposta JSON, retornando dados padrão")
            return {}