import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from app.infrastructure.agents.services.groq_agent_service import GroqAgentService
from app.domain.agents.entities.agent import AgentConfig, AgentType
from app.domain.agents.entities.model_provider import ModelProvider
from app.domain.agents.entities.project_document import DocumentType, ProjectMetadata, ValidationResult, ProjectDocument


class TestGroqAgentService:
    """Testes para o GroqAgentService."""
    
    def setup_method(self):
        """Configuração para cada teste."""
        self.service = GroqAgentService()
        
        # Configuração de agente para testes
        self.agent_config = AgentConfig(
            model_provider=ModelProvider.GROQ.value,
            model_id="llama-3.1-8b-instant",
            temperature=0.7,
            max_tokens=2000,
            tools=[],
            instructions=["Você é um assistente especializado em documentação"]
        )
        
        # Metadados de projeto para testes
        self.project_metadata = ProjectMetadata(
            project_name="Test Project",
            project_type="web_application",
            technologies=["Python", "FastAPI"],
            description="Projeto de teste",
            target_audience="developers",
            complexity_level="medium"
        )
    
    @pytest.mark.asyncio
    async def test_create_agent_success(self):
        """Testa criação bem-sucedida de agente."""
        config = AgentConfig(
            model_provider=ModelProvider.GROQ.value,
            model_id="llama-3.1-8b-instant",
            temperature=0.7,
            max_tokens=2000,
            tools=[],
            instructions=["Você é um assistente especializado em documentação"]
        )
        
        agent = await self.service.create_agent(config)
        
        assert agent.config.model_provider == ModelProvider.GROQ.value
        assert agent.config.model_id == "llama-3.1-8b-instant"
    
    @pytest.mark.asyncio
    async def test_create_agent_invalid_config(self):
        """Testa criação de agente com configuração inválida."""
        # Configuração inválida (modelo não suportado)
        invalid_config = AgentConfig(
            model_provider=ModelProvider.GROQ.value,
            model_id="modelo-inexistente",
            temperature=0.7,
            max_tokens=2000,
            tools=[],
            instructions=[]
        )
        
        with pytest.raises(RuntimeError, match="Falha ao criar agente: Modelo modelo-inexistente não suportado"):
            await self.service.create_agent(invalid_config)
    
    @pytest.mark.asyncio
    async def test_validate_prompt_success(self):
        """Testa validação bem-sucedida de prompt."""
        # Primeiro criar um agente
        config = AgentConfig(
            model_provider=ModelProvider.GROQ.value,
            model_id="llama-3.1-8b-instant",
            temperature=0.7,
            max_tokens=2000,
            tools=[],
            instructions=[]
        )
        
        agent = await self.service.create_agent(config)
        prompt = "Gere um documento de especificação técnica"
        
        with patch.object(self.service, '_get_groq_client') as mock_client:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = '{"is_valid": true, "confidence": 0.9, "project_type": "web_app", "missing_information": [], "suggestions": []}'
            mock_client.return_value.chat.completions.create = Mock(return_value=mock_response)
            
            result = await self.service.validate_prompt(prompt, agent.id)
            
            assert isinstance(result, ValidationResult)
            assert result.is_valid is True
            assert result.confidence_score == 0.9
            assert result.identified_project_type == "web_app"
            assert result.missing_information == []
            assert result.suggestions == []
    
    @pytest.mark.asyncio
    async def test_extract_metadata_success(self):
        """Testa extração bem-sucedida de metadados."""
        prompt = "Este é um projeto Python para análise de dados"
        
        # Primeiro criar um agente
        config = AgentConfig(
            model_provider=ModelProvider.GROQ.value,
            model_id="llama-3.1-8b-instant",
            temperature=0.7,
            max_tokens=1000,
            tools=[],
            instructions=[]
        )
        
        agent = await self.service.create_agent(config)
        
        with patch.object(self.service, '_get_groq_client') as mock_client:
            # Mock da resposta da API
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = '{"project_name": "Data Analysis", "description": "Python data analysis project", "project_type": "data_analysis", "technologies": ["Python", "Pandas"]}'
            mock_client.return_value.chat.completions.create = Mock(return_value=mock_response)
            
            result = await self.service.extract_project_metadata(prompt, agent.id)
            
            assert isinstance(result, ProjectMetadata)
            assert result.project_name == "Data Analysis"
            assert result.description == "Python data analysis project"
            assert result.project_type == "data_analysis"
            assert "Python" in result.technologies
    
    @pytest.mark.asyncio
    async def test_generate_document_success(self):
        """Testa geração bem-sucedida de documento."""
        # Primeiro criar um agente
        config = AgentConfig(
            model_provider=ModelProvider.GROQ.value,
            model_id="llama-3.1-8b-instant",
            temperature=0.7,
            max_tokens=2000,
            tools=[],
            instructions=[]
        )
        
        agent = await self.service.create_agent(config)
        
        with patch.object(self.service, '_get_groq_client') as mock_client:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "# Technical Specification\n\nThis is a test document."
            mock_client.return_value.chat.completions.create = Mock(return_value=mock_response)
            
            # Criar metadados do projeto para o teste
            project_metadata = ProjectMetadata(
                project_name="Test Project",
                description="A test project for technical specification",
                project_type="web_application",
                technologies=["Python", "FastAPI"],
                complexity_level="medium",
                estimated_duration="2 weeks"
            )
            
            result = await self.service.generate_markdown_document(
                prompt="Generate a technical specification document",
                document_type=DocumentType.TECHNICAL_SPECIFICATION,
                project_metadata=project_metadata,
                agent_id=agent.id
            )
            
            assert isinstance(result, str)
            assert "Technical Specification" in result or "technical specification" in result
    
    @pytest.mark.asyncio
    async def test_get_agent_success(self):
        """Testa obtenção bem-sucedida de agente."""
        # Primeiro criar um agente
        config = AgentConfig(
            model_provider=ModelProvider.GROQ.value,
            model_id="llama3-8b-8192",
            temperature=0.7,
            max_tokens=2000,
            tools=[],
            instructions=["Você é um assistente especializado em documentação"]
        )
        
        agent = await self.service.create_agent(config)
        
        # Agora obter o agente
        retrieved_agent = self.service.get_agent_by_id(agent.id)
        
        assert retrieved_agent is not None
        assert retrieved_agent.id == agent.id
    
    @pytest.mark.asyncio
    async def test_get_agent_not_found(self):
        """Testa obtenção de agente inexistente."""
        agent_id = "nonexistent-agent"
        
        result = self.service.get_agent_by_id(agent_id)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_delete_agent_success(self):
        """Testa exclusão bem-sucedida de agente."""
        # Primeiro criar um agente
        config = AgentConfig(
            model_provider=ModelProvider.GROQ.value,
            model_id="llama3-8b-8192",
            temperature=0.7,
            max_tokens=2000,
            tools=[],
            instructions=["Você é um assistente especializado em documentação"]
        )
        
        agent = await self.service.create_agent(config)
        
        # Agora deletar o agente
        result = self.service.delete_agent(agent.id)
        
        assert result is True
        
        # Verificar que o agente foi removido
        deleted_agent = self.service.get_agent_by_id(agent.id)
        assert deleted_agent is None
    
    @pytest.mark.asyncio
    async def test_delete_agent_not_found(self):
        """Testa exclusão de agente inexistente."""
        agent_id = "nonexistent-agent"
        
        result = self.service.delete_agent(agent_id)
        assert result is False
    
    def test_validate_config_valid(self):
        """Testa validação de configuração válida."""
        # Não deve lançar exceção
        self.service._validate_config(self.agent_config)
    
    def test_validate_config_invalid_provider(self):
        """Testa validação de configuração com provedor inválido."""
        invalid_config = AgentConfig(
            model_provider="provider_invalido",
            model_id="llama3-8b-8192",
            temperature=0.7,
            max_tokens=2000,
            tools=[],
            instructions=[]
        )
        
        with pytest.raises(ValueError, match="Provider provider_invalido não suportado pelo Groq"):
            self.service._validate_config(invalid_config)
    
    def test_validate_config_invalid_model(self):
        """Testa validação de configuração com modelo inválido."""
        invalid_config = AgentConfig(
            model_provider=ModelProvider.GROQ.value,
            model_id="modelo-inexistente",
            temperature=0.7,
            max_tokens=2000,
            tools=[],
            instructions=[]
        )
        
        with pytest.raises(ValueError, match="Modelo modelo-inexistente não suportado"):
            self.service._validate_config(invalid_config)
    
    def test_get_supported_models(self):
        """Testa obtenção de modelos suportados."""
        models = self.service.get_supported_models()
        
        assert isinstance(models, list)
        assert len(models) > 0
        assert "llama-3.1-8b-instant" in models
        assert "mixtral-8x7b-32768" in models
        assert "gemma-7b-it" in models