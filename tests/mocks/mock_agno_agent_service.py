from typing import Dict, List, Optional, Any
from app.domain.agents.entities.agent import Agent, AgentType, AgentConfig
from app.domain.agents.entities.project_document import (
    ProjectMetadata,
    ValidationResult,
    DocumentType
)
from app.domain.agents.ports.agent_service import AgentServicePort


class MockAgnoAgentService(AgentServicePort):
    """Mock do serviço de agentes para testes."""
    
    def __init__(self):
        """Inicializa o mock."""
        self._agents: Dict[str, Dict[str, Any]] = {}
        self._agent_configs: Dict[str, AgentConfig] = {}
        self._validation_results: Dict[str, ValidationResult] = {}
        self._metadata_results: Dict[str, ProjectMetadata] = {}

    def reset(self):
        self._agents = {}
        self._agent_configs = {}
        self._validation_results = {}
        self._metadata_results = {}
    
    async def create_agent(
        self, 
        config: AgentConfig,
        agent_id: str = None
    ) -> Agent:
        """Mock para criação de agente."""
        if agent_id is None:
            import uuid
            agent_id = str(uuid.uuid4())
            
        # Criar agente mock
        agent = Agent(
            id=agent_id,
            name=f"Mock Agent {agent_id[:8]}",
            agent_type=AgentType.MARKDOWN_GENERATOR,
            description=f"Mock agent using model {config.model_id}",
            config=config
        )
        
        self._agents[agent_id] = {
            "agent": agent,
            "config": config
        }
        self._agent_configs[agent_id] = config
        
        return agent
    
    async def validate_prompt(self, prompt: str, agent_id: str) -> ValidationResult:
        """Mock para validação de prompt."""
        prompt_lower = prompt.lower()
        
        # Detectar tipo de projeto
        project_type = "unknown"
        if any(word in prompt_lower for word in ["api", "rest", "endpoint"]):
            project_type = "api"
        elif any(word in prompt_lower for word in ["web", "site", "frontend"]):
            project_type = "web"
        elif any(word in prompt_lower for word in ["mobile", "app", "android", "ios"]):
            project_type = "mobile"
        elif any(word in prompt_lower for word in ["bot", "chatbot", "telegram"]):
            project_type = "bot"
        
        # Lógica simplificada: prompts com mais de 5 caracteres são válidos
        word_count = len(prompt.split())
        is_valid = len(prompt.strip()) > 5
        confidence = 0.85 if is_valid else 0.0
        
        suggestions = []
        missing_info = []
        
        # Só adicionar sugestões se o prompt for inválido
        if not is_valid:
            suggestions.append("Tente reformular o prompt com mais detalhes sobre o projeto")
            missing_info.append("Prompt muito curto")
        
        return ValidationResult(
            is_valid=is_valid,
            confidence_score=confidence,
            identified_project_type=project_type,
            missing_information=missing_info,
            suggestions=suggestions
        )
    
    async def extract_project_metadata(
        self, 
        prompt: str, 
        agent_id: str
    ) -> ProjectMetadata:
        """Mock para extração de metadados."""
        prompt_lower = prompt.lower()
        
        # Extrair nome do projeto
        project_name = "Projeto Mock"
        for keyword in ["projeto", "app", "sistema", "aplicação"]:
            if keyword in prompt_lower:
                words = prompt.split()
                try:
                    idx = [w.lower() for w in words].index(keyword)
                    if idx + 1 < len(words):
                        project_name = words[idx + 1].title()
                        break
                except ValueError:
                    continue
        
        # Detectar tecnologias
        technologies = []
        tech_keywords = {
            "python": "Python",
            "javascript": "JavaScript",
            "react": "React",
            "node": "Node.js",
            "django": "Django",
            "flask": "Flask",
            "fastapi": "FastAPI",
            "vue": "Vue.js",
            "angular": "Angular"
        }
        
        for keyword, tech in tech_keywords.items():
            if keyword in prompt_lower:
                technologies.append(tech)
        
        # Detectar tipo de projeto
        project_type = "web"
        if "api" in prompt_lower:
            project_type = "api"
        elif "mobile" in prompt_lower:
            project_type = "mobile"
        elif "bot" in prompt_lower:
            project_type = "bot"
        
        # Detectar complexidade
        complexity = "intermediate"
        if any(word in prompt_lower for word in ["simples", "básico", "iniciante"]):
            complexity = "beginner"
        elif any(word in prompt_lower for word in ["complexo", "avançado", "enterprise"]):
            complexity = "advanced"
        
        return ProjectMetadata(
            project_name=project_name,
            project_type=project_type,
            technologies=technologies,
            description=prompt[:200] + "..." if len(prompt) > 200 else prompt,
            target_audience="developers",
            complexity_level=complexity,
            estimated_duration="2-4 semanas"
        )
    
    async def generate_document(
        self,
        agent_id: str,
        document_type: DocumentType,
        project_metadata: ProjectMetadata,
        custom_instructions: Optional[List[str]] = None
    ) -> str:
        """Mock para geração de documento."""
        return await self.generate_markdown_document(
            prompt="Mock prompt",
            document_type=document_type,
            project_metadata=project_metadata,
            agent_id=agent_id,
            custom_instructions=custom_instructions
        )
    
    async def generate_markdown_document(
        self,
        prompt: str,
        document_type: DocumentType,
        project_metadata: ProjectMetadata,
        agent_id: str,
        custom_instructions: Optional[List[str]] = None
    ) -> str:
        """Mock para geração de documento."""
        
        if document_type == DocumentType.README:
            return f"""# {project_metadata.project_name}

## Descrição
{project_metadata.description}

## Tecnologias
{', '.join(project_metadata.technologies) if project_metadata.technologies else 'A definir'}

## Tipo de Projeto
{project_metadata.project_type}

## Nível de Complexidade
{project_metadata.complexity_level}

## Duração Estimada
{project_metadata.estimated_duration}

## Instalação
```bash
# Instruções de instalação serão adicionadas aqui
```

## Uso
```bash
# Exemplos de uso serão adicionados aqui
```

## Contribuição
Contribuições são bem-vindas! Por favor, leia as diretrizes de contribuição.

## Licença
Este projeto está licenciado sob a licença MIT.

---
*Documento gerado em modo de teste*"""
        
        elif document_type == DocumentType.API_DOCUMENTATION:
            return f"""# API Documentation - {project_metadata.project_name}

## Visão Geral
Documentação da API para {project_metadata.project_name}.

## Base URL
```
https://api.exemplo.com/v1
```

## Autenticação
A API utiliza autenticação via token Bearer.

## Endpoints

### GET /health
Verifica o status da API.

**Response:**
```json
{{
  "status": "ok",
  "timestamp": "2024-01-01T00:00:00Z"
}}
```

---
*Documento gerado em modo de teste*"""
        
        else:
            return f"""# {document_type.value.replace('_', ' ').title()} - {project_metadata.project_name}

## Introdução
Este documento foi gerado automaticamente em modo de teste.

## Conteúdo
O conteúdo específico para {document_type.value} será implementado quando a integração com a API estiver ativa.

## Informações do Projeto
- **Nome:** {project_metadata.project_name}
- **Tipo:** {project_metadata.project_type}
- **Tecnologias:** {', '.join(project_metadata.technologies) if project_metadata.technologies else 'A definir'}
- **Complexidade:** {project_metadata.complexity_level}

---
*Documento gerado em modo de teste*"""
    
    async def improve_prompt(self, prompt: str, agent_id: str) -> str:
        """Mock para melhoria de prompt."""
        return f"Prompt melhorado: {prompt} - Adicione mais detalhes sobre as tecnologias e requisitos específicos."
    
    async def analyze_document_quality(self, content: str, agent_id: str) -> Dict[str, Any]:
        """Mock para análise de qualidade."""
        return {
            "score": 0.85,
            "readability": "good",
            "completeness": "high",
            "suggestions": ["Adicionar mais exemplos de código"],
            "issues": []
        }
    
    async def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Mock para status do agente."""
        if agent_id in self._agents:
            return {
                "agent_id": agent_id,
                "status": "active",
                "last_activity": "2024-01-01T00:00:00Z",
                "total_requests": 10
            }
        return {"agent_id": agent_id, "status": "not_found"}
    
    async def stop_agent(self, agent_id: str) -> bool:
        """Mock para parar agente."""
        return agent_id in self._agents
    
    async def restart_agent(self, agent_id: str) -> bool:
        """Mock para reiniciar agente."""
        return agent_id in self._agents

    def reset(self):
        """Reseta o estado do mock."""
        self._agents = {}
        self._agent_configs = {}
        self._validation_results = {}
        self._metadata_results = {}