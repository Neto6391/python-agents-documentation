import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from groq import Groq

from app.domain.agents.entities.agent import Agent, AgentType, AgentConfig
from app.domain.agents.entities.project_document import (
    ProjectDocument,
    ProjectMetadata,
    ValidationResult,
    DocumentType
)
from app.domain.agents.ports.agent_service import AgentServicePort
from app.core.config.settings import settings


logger = logging.getLogger(__name__)


class GroqAgentService(AgentServicePort):
    """Implementação do serviço de agentes usando Groq API."""
    
    def __init__(self):
        self._agents: Dict[str, Dict[str, Any]] = {}
        self._groq_client = None
        
    def _get_groq_client(self) -> Groq:
        """Obtém o cliente Groq configurado."""
        if self._groq_client is None:
            api_key = getattr(settings, 'groq_api_key', None)
            if not api_key:
                raise ValueError("GROQ_API_KEY não configurada")
            self._groq_client = Groq(api_key=api_key)
        return self._groq_client
    
    async def create_agent(self, config: AgentConfig, agent_id: str = None) -> Agent:
        """Cria um agente no Groq.
        
        Args:
            config: Configuração do agente
            
        Returns:
            Agente criado
            
        Raises:
            ValueError: Se a configuração for inválida
            RuntimeError: Se houver erro na criação
        """
        try:
            # Validar configuração
            self._validate_config(config)
            
            # Usar ID fornecido ou gerar um novo
            if agent_id is None:
                import uuid
                agent_id = str(uuid.uuid4())
            
            logger.info(f"Criando agente Groq {agent_id} com modelo {config.model_id}")
            
            # Criar agente
            agent = Agent(
                id=agent_id,
                name=f"Groq Agent {agent_id[:8]}",
                agent_type=AgentType.MARKDOWN_GENERATOR,
                description=f"Agente Groq usando modelo {config.model_id}",
                config=config
            )
            
            # Armazenar referência do agente
            self._agents[agent_id] = {
                "agent": agent,
                "created_at": datetime.utcnow().isoformat(),
                "status": "active",
                "temperature": config.temperature,
                "max_tokens": config.max_tokens,
                "instructions": config.instructions or []
            }
            
            logger.info(f"Agente Groq {agent_id} criado com sucesso")
            
            return agent
            
        except Exception as e:
            logger.error(f"Erro ao criar agente Groq: {str(e)}")
            raise RuntimeError(f"Falha ao criar agente: {str(e)}")
    
    def _validate_config(self, config: AgentConfig) -> None:
        """Valida a configuração do agente para Groq."""
        if config.model_provider != "groq":
            raise ValueError(f"Provider {config.model_provider} não suportado pelo GroqAgentService")
        
        # Modelos suportados pelo Groq (atualizados)
        supported_models = [
            "llama-3.1-405b-reasoning",
            "llama-3.1-8b-instant",
            "llama-3.2-1b-preview",
            "llama-3.2-3b-preview",
            "llama-3.2-11b-text-preview",
            "llama-3.2-90b-text-preview",
            "llama3-groq-70b-8192-tool-use-preview",
            "llama3-groq-8b-8192-tool-use-preview",
            "llama3-70b-8192",
            "llama3-8b-8192",
            "mixtral-8x7b-32768",
            "gemma-7b-it",
            "gemma2-9b-it",
            "meta-llama/llama-4-scout-17b-16e-instruct"
        ]
        
        if config.model_id not in supported_models:
            raise ValueError(f"Modelo {config.model_id} não suportado. Modelos disponíveis: {supported_models}")
        
        if not 0.0 <= config.temperature <= 2.0:
            raise ValueError("Temperatura deve estar entre 0.0 e 2.0")
        
        if config.max_tokens and (config.max_tokens <= 0 or config.max_tokens > 8192):
            raise ValueError("max_tokens deve estar entre 1 e 8192 para Groq")
    
    async def validate_prompt(self, prompt: str, agent_id: str) -> ValidationResult:
        """Valida um prompt usando o agente Groq.
        
        Args:
            agent_id: ID do agente
            prompt: Prompt a ser validado
            
        Returns:
            Resultado da validação
        """
        try:
            if agent_id not in self._agents:
                return ValidationResult(
                    is_valid=False,
                    confidence_score=0.0,
                    identified_project_type=None,
                    missing_information=["Agente não encontrado"],
                    suggestions=[]
                )
            
            agent_info = self._agents[agent_id]
            client = self._get_groq_client()
            
            # Prompt para validação otimizado para MVPs
            validation_prompt = f"""
            Você é um especialista em MVPs (Minimum Viable Products). Analise se o seguinte prompt contém informações SUFICIENTES para gerar um MVP básico.
            
            CRITÉRIOS PARA VALIDAÇÃO:
            - O prompt deve mencionar pelo menos um tipo de aplicação (web, mobile, API, etc.)
            - Deve ter uma ideia central clara do que será desenvolvido
            - Não precisa ter todos os detalhes técnicos - um MVP é mínimo por natureza
            - Seja GENEROSO na validação - prefira aprovar prompts que tenham potencial
            
            PROMPT: {prompt}
            
            Responda APENAS em formato JSON válido:
            {{
                "is_valid": true/false,
                "confidence": 0.0-1.0,
                "issues": ["lista de problemas críticos apenas"],
                "suggestions": ["sugestões apenas se realmente necessário"]
            }}
            """
            
            response = client.chat.completions.create(
                model=agent_info["agent"].config.model_id,
                messages=[
                    {"role": "system", "content": "Você é um especialista em MVPs que valida prompts de forma generosa. Aprove prompts que tenham potencial, mesmo que não sejam perfeitos. Um MVP deve ser mínimo e funcional."},
                    {"role": "user", "content": validation_prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            result_text = response.choices[0].message.content
            logger.info(f"Resposta da API Groq para validação: {result_text}")
            
            try:
                # Extrair JSON da resposta (pode vir com texto adicional)
                json_start = result_text.find('{')
                json_end = result_text.rfind('}') + 1
                
                if json_start != -1 and json_end > json_start:
                    json_text = result_text[json_start:json_end]
                    result_data = json.loads(json_text)
                else:
                    # Se não encontrar JSON, tentar parse direto
                    result_data = json.loads(result_text)
                
                return ValidationResult(
                    is_valid=result_data.get("is_valid", False),
                    confidence_score=result_data.get("confidence", 0.0),
                    identified_project_type=result_data.get("project_type"),
                    missing_information=result_data.get("issues", result_data.get("missing_information", [])),
                    suggestions=result_data.get("suggestions", [])
                )
            except json.JSONDecodeError as e:
                logger.error(f"Erro ao fazer parse JSON da resposta: {e}. Resposta: {result_text}")
                return ValidationResult(
                    is_valid=False,
                    confidence_score=0.5,
                    identified_project_type=None,
                    missing_information=["Erro ao processar resposta da validação"],
                    suggestions=["Tente reformular o prompt"]
                )
                
        except Exception as e:
            logger.error(f"Erro na validação do prompt: {str(e)}")
            return ValidationResult(
                is_valid=False,
                confidence_score=0.0,
                identified_project_type=None,
                missing_information=[f"Erro interno: {str(e)}"],
                suggestions=["Tente novamente mais tarde"]
            )
    
    async def extract_metadata(self, agent_id: str, project_path: str) -> ProjectMetadata:
        """Extrai metadados de um projeto usando o agente Groq.
        
        Args:
            agent_id: ID do agente
            project_path: Caminho do projeto
            
        Returns:
            Metadados extraídos do projeto
        """
        try:
            if agent_id not in self._agents:
                raise ValueError("Agente não encontrado")
            
            agent_info = self._agents[agent_id]
            client = self._get_groq_client()
            
            # Simular análise de projeto (em um caso real, analisaria os arquivos)
            analysis_prompt = f"""
            Analise o projeto no caminho: {project_path}
            
            Extraia e retorne metadados em formato JSON:
            {{
                "name": "nome do projeto",
                "description": "descrição do projeto",
                "language": "linguagem principal",
                "framework": "framework utilizado",
                "dependencies": ["lista de dependências"],
                "structure": "estrutura do projeto",
                "complexity": "baixa/média/alta"
            }}
            """
            
            response = client.chat.completions.create(
                model=agent_info["agent"].config.model_id,
                messages=[
                    {"role": "system", "content": "Você é um especialista em análise de projetos de software."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.1,
                max_tokens=1500
            )
            
            result_text = response.choices[0].message.content
            
            try:
                metadata_data = json.loads(result_text)
                return ProjectMetadata(
                    project_name=metadata_data.get("name", "Projeto Desconhecido"),
                    description=metadata_data.get("description", "Sem descrição"),
                    technologies=[metadata_data.get("language", "Desconhecido")],
                    project_type=metadata_data.get("framework", "general"),
                    complexity_level=metadata_data.get("complexity", "medium"),
                    estimated_duration=metadata_data.get("duration", "unknown"),
                    key_features=metadata_data.get("features", []),
                    technical_requirements=metadata_data.get("dependencies", [])
                )
            except json.JSONDecodeError:
                 return ProjectMetadata(
                     project_name="Projeto",
                     description="Erro ao extrair metadados",
                     technologies=["Desconhecido"],
                     project_type="general",
                     complexity_level="medium",
                     estimated_duration="unknown",
                     key_features=[],
                     technical_requirements=[]
                 )
                
        except Exception as e:
            logger.error(f"Erro na extração de metadados: {str(e)}")
            return ProjectMetadata(
                project_name="Projeto",
                description="Erro ao extrair metadados",
                technologies=["Desconhecido"],
                project_type="general",
                complexity_level="medium",
                estimated_duration="unknown",
                key_features=[],
                technical_requirements=[]
            )
    
    async def generate_document(
        self,
        agent_id: str,
        document_type: DocumentType,
        project_metadata: ProjectMetadata,
        custom_instructions: Optional[List[str]] = None
    ) -> str:
        """Gera um documento usando o agente Groq.
        
        Args:
            agent_id: ID do agente
            document_type: Tipo de documento a ser gerado
            project_metadata: Metadados do projeto
            custom_instructions: Instruções customizadas opcionais
            
        Returns:
            Conteúdo do documento gerado
        """
        try:
            if agent_id not in self._agents:
                raise ValueError("Agente não encontrado")
            
            agent_info = self._agents[agent_id]
            client = self._get_groq_client()
            
            # Construir prompt baseado no tipo de documento
            instructions = custom_instructions or []
            all_instructions = agent_info["instructions"] + instructions
            
            prompt = self._build_document_prompt(
                document_type, project_metadata, all_instructions
            )
            
            response = client.chat.completions.create(
                model=agent_info["agent"].config.model_id,
                messages=[
                    {"role": "system", "content": "Você é um especialista em documentação técnica."},
                    {"role": "user", "content": prompt}
                ],
                temperature=agent_info["temperature"],
                max_tokens=agent_info.get("max_tokens", 4000)
            )
            
            content = response.choices[0].message.content
            
            logger.info(f"Documento {document_type.value} gerado com sucesso pelo agente {agent_id}")
            return content
            
        except Exception as e:
            logger.error(f"Erro na geração de documento: {str(e)}")
            raise RuntimeError(f"Falha ao gerar documento: {str(e)}")
    
    def _build_document_prompt(
        self,
        document_type: DocumentType,
        metadata: ProjectMetadata,
        instructions: List[str]
    ) -> str:
        """Constrói o prompt para geração de documento."""
        base_prompt = f"""
        Gere um documento do tipo {document_type.value} para o projeto:
        
        Nome: {metadata.project_name}
        Descrição: {metadata.description}
        Tipo: {metadata.project_type}
        Tecnologias: {', '.join(metadata.technologies)}
        Público-alvo: {metadata.target_audience or 'Não especificado'}
        Complexidade: {metadata.complexity_level or 'Não especificado'}
        Duração estimada: {metadata.estimated_duration or 'Não especificado'}
        """
        
        if instructions:
            base_prompt += "\n\nInstruções adicionais:\n"
            for i, instruction in enumerate(instructions, 1):
                base_prompt += f"{i}. {instruction}\n"
        
        base_prompt += "\n\nGere um documento completo, bem estruturado e informativo."
        
        return base_prompt
    
    def _build_generation_prompt(
        self,
        prompt: str,
        document_type: DocumentType,
        metadata: ProjectMetadata,
        custom_instructions: Optional[List[str]] = None
    ) -> str:
        """Constrói o prompt para geração de documento."""
        
        # Verificar se é um MVP em tópicos
        is_mvp_topics = "mvp" in prompt.lower() and "tópicos" in prompt.lower()
        
        if is_mvp_topics:
            generation_prompt = f"""
Gere um MVP (Minimum Viable Product) completo e detalhado em formato de tópicos baseado no seguinte prompt:

{prompt}

Informações do projeto:
- Nome: {metadata.project_name}
- Descrição: {metadata.description}
- Tipo: {metadata.project_type}
- Tecnologias: {', '.join(metadata.technologies) if metadata.technologies else 'A definir'}
- Complexidade: {metadata.complexity_level}
- Duração estimada: {metadata.estimated_duration}

ESTRUTURA OBRIGATÓRIA PARA MVP EM TÓPICOS:

# 1. Visão Geral do Projeto
- Objetivo principal
- Problema que resolve
- Público-alvo
- Proposta de valor

# 2. Funcionalidades Principais
- Lista detalhada de features essenciais
- Fluxos de usuário principais
- Casos de uso prioritários

# 3. Arquitetura Técnica
- Stack tecnológico detalhado
- Estrutura do banco de dados
- APIs e endpoints necessários
- Integrações externas

# 4. Interface e Experiência do Usuário
- Telas principais
- Fluxos de navegação
- Componentes de UI essenciais

# 5. Implementação e Desenvolvimento
- Cronograma de desenvolvimento
- Priorização de features
- Marcos e entregas

# 6. Considerações Técnicas
- Segurança
- Performance
- Escalabilidade
- Manutenibilidade

Gere conteúdo EXTENSO e DETALHADO para cada seção (mínimo 2000 palavras total).
"""
        else:
            generation_prompt = f"""
Gere um documento do tipo {document_type.value} baseado no seguinte prompt:

{prompt}

Informações do projeto:
- Nome: {metadata.project_name}
- Descrição: {metadata.description}
- Tipo: {metadata.project_type}
- Tecnologias: {', '.join(metadata.technologies) if metadata.technologies else 'A definir'}
- Complexidade: {metadata.complexity_level}
- Duração estimada: {metadata.estimated_duration}

INSTRUÇÕES:
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
    
    async def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Obtém o status de um agente.
        
        Args:
            agent_id: ID do agente
            
        Returns:
            Status do agente ou None se não encontrado
        """
        if agent_id not in self._agents:
            return None
        
        agent_info = self._agents[agent_id]
        return {
            "status": agent_info["status"],
            "model_id": agent_info["agent"].config.model_id,
            "created_at": agent_info["created_at"],
            "last_activity": datetime.utcnow().isoformat()
        }
    
    async def delete_agent(self, agent_id: str) -> bool:
        """Remove um agente.
        
        Args:
            agent_id: ID do agente
            
        Returns:
            True se removido com sucesso, False caso contrário
        """
        if agent_id in self._agents:
            del self._agents[agent_id]
            logger.info(f"Agente Groq {agent_id} removido")
            return True
        return False
    
    async def extract_project_metadata(self, prompt: str, agent_id: str) -> ProjectMetadata:
        """Extrai metadados do projeto a partir do prompt."""
        if agent_id not in self._agents:
            raise ValueError("Agente não encontrado")
        
        agent_info = self._agents[agent_id]
        client = self._get_groq_client()
        
        extraction_prompt = f"""
        Extraia os metadados do seguinte prompt de projeto:
        
        Prompt: {prompt}
        
        Retorne um JSON com os seguintes campos:
        {{
            "project_name": "nome do projeto",
            "project_type": "tipo do projeto (web_app, api, mobile_app, etc.)",
            "technologies": ["lista", "de", "tecnologias"],
            "description": "descrição do projeto",
            "target_audience": "público-alvo (opcional)",
            "complexity_level": "simple, medium ou complex",
            "estimated_duration": "duração estimada (opcional)"
        }}
        """
        
        try:
            response = client.chat.completions.create(
                model=agent_info["agent"].config.model_id,
                messages=[
                    {"role": "system", "content": "Você é um especialista em análise de projetos de software."},
                    {"role": "user", "content": extraction_prompt}
                ],
                temperature=0.1,
                max_tokens=800
            )
            
            try:
                metadata_dict = json.loads(response.choices[0].message.content)
                return ProjectMetadata(
                    project_name=metadata_dict.get("project_name", "Projeto Sem Nome"),
                    project_type=metadata_dict.get("project_type", "web_app"),
                    technologies=metadata_dict.get("technologies", []),
                    description=metadata_dict.get("description", "Descrição não fornecida"),
                    target_audience=metadata_dict.get("target_audience"),
                    complexity_level=metadata_dict.get("complexity_level", "medium"),
                    estimated_duration=metadata_dict.get("estimated_duration")
                )
            except json.JSONDecodeError:
                # Fallback para metadados básicos
                return ProjectMetadata(
                    project_name="Projeto Extraído",
                    project_type="web_app",
                    technologies=["Python"],
                    description=prompt[:200] + "..." if len(prompt) > 200 else prompt
                )
        except Exception as e:
            logger.error(f"Erro ao extrair metadados: {str(e)}")
            # Fallback para metadados básicos
            return ProjectMetadata(
                project_name="Projeto Extraído",
                project_type="web_app",
                technologies=["Python"],
                description=prompt[:200] + "..." if len(prompt) > 200 else prompt
            )
    
    async def generate_markdown_document(
        self,
        prompt: str,
        document_type: DocumentType,
        project_metadata: ProjectMetadata,
        agent_id: str,
        custom_instructions: Optional[List[str]] = None
    ) -> str:
        """Gera documento Markdown a partir do prompt."""
        try:
            if agent_id not in self._agents:
                raise ValueError("Agente não encontrado")
            
            agent_info = self._agents[agent_id]
            client = self._get_groq_client()
            
            # Construir prompt de geração
            generation_prompt = self._build_generation_prompt(
                prompt, document_type, project_metadata, custom_instructions
            )
            
            # Construir mensagem do sistema com instruções do agente
            agent_instructions = agent_info["agent"].config.instructions or []
            system_message = "Você é um especialista em documentação técnica. Gere documentação clara, bem estruturada e informativa em formato Markdown."
            
            if agent_instructions:
                system_message += "\n\nINSTRUÇÕES ESPECÍFICAS DO AGENTE:\n" + "\n".join(f"- {inst}" for inst in agent_instructions)
            
            # Adicionar instruções específicas para MVP em tópicos
            if "mvp" in prompt.lower() and "tópicos" in prompt.lower():
                system_message += "\n\nPARA MVP EM TÓPICOS:\n- Organize o conteúdo em seções claras com títulos em markdown\n- Use listas e subtópicos para estruturar as ideias\n- Inclua detalhes técnicos e funcionais\n- Mantenha o foco em um MVP completo e detalhado\n- Gere conteúdo extenso e informativo (mínimo 2000 palavras)"
            
            response = client.chat.completions.create(
                model=agent_info["agent"].config.model_id,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": generation_prompt}
                ],
                temperature=agent_info["temperature"],
                max_tokens=agent_info.get("max_tokens", 4000)
            )
            
            content = response.choices[0].message.content
            
            # Extrair conteúdo Markdown se necessário
            content = self._extract_markdown_content(content)
            
            logger.info(f"Documento {document_type.value} gerado com sucesso pelo agente {agent_id}")
            return content
            
        except Exception as e:
            logger.error(f"Erro ao gerar documento markdown: {str(e)}")
            raise RuntimeError(f"Falha ao gerar documento: {str(e)}")
    
    async def _generate_document_content(self, prompt: str, document_type: str, metadata: ProjectMetadata) -> str:
        """Gera o conteúdo do documento baseado no prompt e metadados."""
        # Implementação básica para geração de conteúdo
        # Em uma implementação real, isso seria mais sofisticado
        
        if document_type == "readme":
            return f"""# {metadata.project_name}

## Descrição
{metadata.description}

## Tecnologias
{', '.join(metadata.technologies)}

## Tipo de Projeto
{metadata.project_type}

## Complexidade
{metadata.complexity_level}

## Instalação
[Instruções de instalação]

## Uso
[Instruções de uso]

## Contribuição
[Guia de contribuição]
"""
        
        return f"Documento {document_type} para {metadata.project_name}"
    
    async def improve_prompt(
        self, 
        original_prompt: str, 
        validation_result: ValidationResult,
        agent_id: str
    ) -> str:
        """Gera sugestões para melhorar o prompt baseado na validação."""
        if validation_result.is_valid:
            return original_prompt
        
        if agent_id not in self._agents:
            raise ValueError("Agente não encontrado")
        
        agent_info = self._agents[agent_id]
        client = self._get_groq_client()
        
        improvement_prompt = f"""
        Melhore o seguinte prompt para geração de documentação de projeto:
        
        Prompt original: {original_prompt}
        
        Problemas identificados:
        {', '.join(validation_result.issues)}
        
        Sugestões:
        {', '.join(validation_result.suggestions)}
        
        Gere um prompt melhorado que seja mais claro e completo.
        """
        
        try:
            response = client.chat.completions.create(
                model=agent_info["agent"].config.model_id,
                messages=[
                    {"role": "system", "content": "Você é um especialista em melhorar prompts para geração de documentação."},
                    {"role": "user", "content": improvement_prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Erro ao melhorar prompt: {str(e)}")
            raise RuntimeError(f"Erro ao melhorar prompt: {str(e)}")
    
    async def analyze_document_quality(
        self, 
        document: ProjectDocument, 
        agent_id: str
    ) -> Dict[str, Any]:
        """Analisa a qualidade do documento gerado."""
        if agent_id not in self._agents:
            raise ValueError("Agente não encontrado")
        
        agent_info = self._agents[agent_id]
        client = self._get_groq_client()
        
        analysis_prompt = f"""
        Analise a qualidade do seguinte documento de projeto:
        
        Título: {document.title}
        Tipo: {document.document_type.value}
        Conteúdo: {document.content[:1500]}...
        
        Avalie os seguintes aspectos (escala 1-10):
        1. Clareza e organização
        2. Completude das informações
        3. Qualidade técnica
        4. Utilidade prática
        
        Retorne uma análise em formato JSON com scores e comentários:
        {{
            "overall_score": 0.0,
            "clarity": 0.0,
            "completeness": 0.0,
            "technical_quality": 0.0,
            "usefulness": 0.0,
            "comments": "comentários detalhados"
        }}
        """
        
        try:
            response = client.chat.completions.create(
                model=agent_info["agent"].config.model_id,
                messages=[
                    {"role": "system", "content": "Você é um especialista em análise de qualidade de documentação técnica."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.1,
                max_tokens=800
            )
            
            try:
                return json.loads(response.choices[0].message.content)
            except json.JSONDecodeError:
                return {
                    "overall_score": 7.0,
                    "clarity": 7.0,
                    "completeness": 7.0,
                    "technical_quality": 7.0,
                    "usefulness": 7.0,
                    "comments": response.choices[0].message.content
                }
        except Exception as e:
            logger.error(f"Erro na análise de qualidade: {str(e)}")
            return {
                "overall_score": 5.0,
                "error": f"Erro na análise: {str(e)}"
            }
    
    async def stop_agent(self, agent_id: str) -> bool:
        """Para a execução de um agente."""
        if agent_id in self._agents:
            self._agents[agent_id]["status"] = "inactive"
            logger.info(f"Agente Groq {agent_id} parado")
            return True
        return False
    
    async def restart_agent(self, agent_id: str) -> bool:
        """Reinicia um agente."""
        if agent_id in self._agents:
            self._agents[agent_id]["status"] = "active"
            logger.info(f"Agente Groq {agent_id} reiniciado")
            return True
        return False
    
    def reset(self):
        """Reseta o estado do serviço para testes."""
        self._agents.clear()
        logger.info("Estado do GroqAgentService resetado")
    
    def _get_supported_models(self) -> List[str]:
        """Retorna lista de modelos suportados pelo Groq."""
        return [
            "llama-3.1-405b-reasoning",
            "llama-3.1-8b-instant",
            "llama-3.2-1b-preview",
            "llama-3.2-3b-preview",
            "llama-3.2-11b-text-preview",
            "llama-3.2-90b-text-preview",
            "llama3-groq-70b-8192-tool-use-preview",
            "llama3-groq-8b-8192-tool-use-preview",
            "mixtral-8x7b-32768",
            "gemma-7b-it",
            "gemma2-9b-it",
            "meta-llama/llama-4-scout-17b-16e-instruct"
        ]
    
    def get_supported_models(self) -> List[str]:
        """Retorna lista de modelos suportados pelo Groq."""
        return [
            "llama-3.1-405b-reasoning",
            "llama-3.1-8b-instant",
            "llama-3.2-1b-preview",
            "llama-3.2-3b-preview",
            "llama-3.2-11b-text-preview",
            "llama-3.2-90b-text-preview",
            "llama3-groq-70b-8192-tool-use-preview",
            "llama3-groq-8b-8192-tool-use-preview",
            "llama3-70b-8192",
            "llama3-8b-8192",
            "mixtral-8x7b-32768",
            "gemma-7b-it",
            "gemma2-9b-it",
            "meta-llama/llama-4-scout-17b-16e-instruct"
        ]
    
    def get_agent_by_id(self, agent_id: str) -> Optional[Agent]:
        """Obtém um agente pelo ID."""
        if agent_id in self._agents:
            return self._agents[agent_id]["agent"]
        return None
    
    def delete_agent(self, agent_id: str) -> bool:
        """Deleta um agente pelo ID."""
        if agent_id in self._agents:
            del self._agents[agent_id]
            return True
        return False