#!/usr/bin/env python3
"""
Exemplo prático de uso da integração Groq para geração de documentação.

Este script demonstra como:
1. Criar um agente Groq
2. Validar prompts
3. Extrair metadados de projetos
4. Gerar diferentes tipos de documentos
"""

import asyncio
import os
from typing import List

from app.infrastructure.agents.services.groq_agent_service import GroqAgentService
from app.domain.agents.entities.agent import AgentConfig
from app.domain.agents.entities.project_document import ProjectMetadata, DocumentType
from app.domain.agents.enums import ModelProvider


class GroqDocumentationGenerator:
    """Gerador de documentação usando Groq."""
    
    def __init__(self):
        self.service = GroqAgentService()
        self.agent_id = None
    
    async def setup_agent(self, model_id: str = "llama-3.1-70b-versatile") -> str:
        """Configura e cria um agente Groq."""
        config = AgentConfig(
            model_provider=ModelProvider.GROQ.value,
            model_id=model_id,
            temperature=0.7,
            max_tokens=4000,
            instructions=[
                "Gere documentação técnica clara e bem estruturada",
                "Use formatação Markdown apropriada",
                "Inclua exemplos práticos quando relevante",
                "Mantenha linguagem profissional mas acessível"
            ]
        )
        
        agent = await self.service.create_agent(config)
        self.agent_id = agent.id
        print(f"✅ Agente criado com sucesso: {self.agent_id}")
        return self.agent_id
    
    async def validate_prompt(self, prompt: str) -> bool:
        """Valida um prompt antes da geração."""
        if not self.agent_id:
            raise ValueError("Agente não foi criado. Execute setup_agent() primeiro.")
        
        result = await self.service.validate_prompt(prompt, self.agent_id)
        
        print(f"\n📝 Validação do Prompt:")
        print(f"   Válido: {'✅' if result.is_valid else '❌'} {result.is_valid}")
        print(f"   Confiança: {result.confidence_score:.2f}")
        
        if result.missing_information:
            print(f"   ⚠️  Informações faltando:")
            for info in result.missing_information:
                print(f"      - {info}")
        
        if result.suggestions:
            print(f"   💡 Sugestões:")
            for suggestion in result.suggestions:
                print(f"      - {suggestion}")
        
        return result.is_valid
    
    async def extract_metadata(self, prompt: str) -> ProjectMetadata:
        """Extrai metadados do projeto a partir do prompt."""
        if not self.agent_id:
            raise ValueError("Agente não foi criado. Execute setup_agent() primeiro.")
        
        metadata = await self.service.extract_project_metadata(prompt, self.agent_id)
        
        print(f"\n🔍 Metadados Extraídos:")
        print(f"   Nome: {metadata.project_name}")
        print(f"   Tipo: {metadata.project_type}")
        print(f"   Tecnologias: {', '.join(metadata.technologies) if metadata.technologies else 'N/A'}")
        print(f"   Complexidade: {metadata.complexity_level or 'N/A'}")
        print(f"   Duração: {metadata.estimated_duration or 'N/A'}")
        
        return metadata
    
    async def generate_document(
        self, 
        prompt: str, 
        document_type: DocumentType, 
        project_metadata: ProjectMetadata,
        custom_instructions: List[str] = None
    ) -> str:
        """Gera um documento usando o agente Groq."""
        if not self.agent_id:
            raise ValueError("Agente não foi criado. Execute setup_agent() primeiro.")
        
        print(f"\n📄 Gerando documento: {document_type.value}")
        
        content = await self.service.generate_markdown_document(
            prompt=prompt,
            document_type=document_type,
            project_metadata=project_metadata,
            agent_id=self.agent_id,
            custom_instructions=custom_instructions
        )
        
        print(f"✅ Documento gerado com sucesso ({len(content)} caracteres)")
        return content
    
    async def save_document(self, content: str, filename: str):
        """Salva o documento gerado em arquivo."""
        os.makedirs("generated_docs", exist_ok=True)
        filepath = os.path.join("generated_docs", filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"💾 Documento salvo em: {filepath}")


async def demo_readme_generation():
    """Demonstra geração de README."""
    print("🚀 Demo: Geração de README")
    print("=" * 50)
    
    generator = GroqDocumentationGenerator()
    
    # 1. Configurar agente
    await generator.setup_agent()
    
    # 2. Definir prompt
    prompt = """
    Gere um README completo para um projeto FastAPI que inclui:
    - Autenticação JWT
    - Conexão com PostgreSQL
    - Endpoints CRUD para usuários
    - Documentação da API com Swagger
    - Testes unitários com pytest
    - Containerização com Docker
    - CI/CD com GitHub Actions
    
    O projeto deve ser adequado para desenvolvedores Python intermediários
    e incluir instruções claras de instalação e uso.
    """
    
    # 3. Validar prompt
    is_valid = await generator.validate_prompt(prompt)
    if not is_valid:
        print("❌ Prompt inválido. Ajuste conforme sugestões.")
        return
    
    # 4. Extrair metadados
    metadata = await generator.extract_metadata(prompt)
    
    # 5. Gerar README
    readme_content = await generator.generate_document(
        prompt=prompt,
        document_type=DocumentType.README,
        project_metadata=metadata,
        custom_instructions=[
            "Inclua badges do GitHub",
            "Adicione seção de contribuição",
            "Use emojis para melhor visualização"
        ]
    )
    
    # 6. Salvar documento
    await generator.save_document(readme_content, "fastapi_project_readme.md")
    
    print("\n📋 Preview do README:")
    print("-" * 50)
    print(readme_content[:500] + "..." if len(readme_content) > 500 else readme_content)


async def demo_api_documentation():
    """Demonstra geração de documentação de API."""
    print("\n\n🔌 Demo: Geração de Documentação de API")
    print("=" * 50)
    
    generator = GroqDocumentationGenerator()
    await generator.setup_agent()
    
    prompt = """
    Gere documentação completa da API para um sistema de e-commerce que inclui:
    - Endpoints de autenticação (login, registro, refresh token)
    - CRUD de produtos (criar, listar, atualizar, deletar)
    - Carrinho de compras (adicionar, remover, finalizar)
    - Histórico de pedidos
    - Sistema de avaliações
    
    Inclua exemplos de request/response, códigos de status HTTP,
    e descrições detalhadas de cada endpoint.
    """
    
    # Criar metadados específicos para API
    metadata = ProjectMetadata(
        project_name="E-commerce API",
        description="API REST para sistema de e-commerce",
        project_type="api",
        technologies=["FastAPI", "PostgreSQL", "Redis", "JWT"],
        complexity_level="high",
        estimated_duration="6 semanas"
    )
    
    api_docs = await generator.generate_document(
        prompt=prompt,
        document_type=DocumentType.API_DOCUMENTATION,
        project_metadata=metadata
    )
    
    await generator.save_document(api_docs, "ecommerce_api_docs.md")
    
    print("\n📋 Preview da Documentação da API:")
    print("-" * 50)
    print(api_docs[:500] + "..." if len(api_docs) > 500 else api_docs)


async def demo_technical_specification():
    """Demonstra geração de especificação técnica."""
    print("\n\n⚙️ Demo: Geração de Especificação Técnica")
    print("=" * 50)
    
    generator = GroqDocumentationGenerator()
    await generator.setup_agent("llama-3.2-90b-text-preview")  # Modelo mais avançado
    
    prompt = """
    Gere uma especificação técnica detalhada para um sistema de monitoramento
    de infraestrutura que deve:
    - Coletar métricas de servidores (CPU, memória, disco, rede)
    - Armazenar dados em time series database
    - Gerar alertas baseados em thresholds
    - Fornecer dashboards em tempo real
    - Suportar múltiplos ambientes (dev, staging, prod)
    - Integrar com sistemas de notificação (Slack, email)
    
    A especificação deve incluir arquitetura, tecnologias, requisitos
    não-funcionais e plano de implementação.
    """
    
    metadata = ProjectMetadata(
        project_name="InfraMonitor",
        description="Sistema de monitoramento de infraestrutura",
        project_type="monitoring_system",
        technologies=["Python", "InfluxDB", "Grafana", "Prometheus", "Docker"],
        complexity_level="high",
        estimated_duration="12 semanas"
    )
    
    tech_spec = await generator.generate_document(
        prompt=prompt,
        document_type=DocumentType.TECHNICAL_SPECIFICATION,
        project_metadata=metadata,
        custom_instructions=[
            "Inclua diagramas de arquitetura em formato Mermaid",
            "Detalhe requisitos de performance",
            "Especifique estratégias de backup e recovery"
        ]
    )
    
    await generator.save_document(tech_spec, "inframonitor_tech_spec.md")
    
    print("\n📋 Preview da Especificação Técnica:")
    print("-" * 50)
    print(tech_spec[:500] + "..." if len(tech_spec) > 500 else tech_spec)


async def main():
    """Função principal que executa todas as demonstrações."""
    print("🤖 Demonstração da Integração Groq")
    print("===================================\n")
    
    # Verificar se a API key está configurada
    if not os.getenv("GROQ_API_KEY"):
        print("❌ GROQ_API_KEY não configurada!")
        print("Configure a variável de ambiente antes de executar:")
        print("export GROQ_API_KEY=your_api_key_here")
        return
    
    try:
        # Executar demonstrações
        await demo_readme_generation()
        await demo_api_documentation()
        await demo_technical_specification()
        
        print("\n\n🎉 Todas as demonstrações concluídas com sucesso!")
        print("📁 Documentos gerados salvos na pasta 'generated_docs/'")
        
    except Exception as e:
        print(f"❌ Erro durante execução: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())