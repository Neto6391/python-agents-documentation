#!/usr/bin/env python3
"""
Exemplo de uso da API de Agentes

Este arquivo demonstra como usar a API para:
1. Criar agentes
2. Gerar documentos
3. Validar prompts
4. Listar agentes e documentos
5. Analisar qualidade de documentos
"""

import asyncio
import httpx
from typing import Dict, Any


class AgentsAPIClient:
    """Cliente para interagir com a API de Agentes."""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = "your-api-key"):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
    
    async def create_agent(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria um novo agente."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/agents",
                json=agent_data,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def list_agents(self, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """Lista agentes disponíveis."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/agents",
                params={"limit": limit, "offset": offset},
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def generate_document(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gera um documento usando um agente."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/agents/documents/generate",
                json=document_data,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def validate_prompt(self, prompt_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida um prompt."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/agents/documents/validate-prompt",
                json=prompt_data,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def list_documents(self, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """Lista documentos gerados."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/agents/documents",
                params={"limit": limit, "offset": offset},
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def analyze_document_quality(self, document_id: str) -> Dict[str, Any]:
        """Analisa a qualidade de um documento."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/agents/documents/{document_id}/analyze-quality",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()


async def demo_basic_usage():
    """Demonstração básica de uso da API."""
    print("🤖 Demonstração da API de Agentes\n")
    
    # Inicializar cliente
    client = AgentsAPIClient()
    
    try:
        # 1. Criar um agente
        print("1. Criando um agente...")
        agent_data = {
            "name": "Documentador de Projetos",
            "description": "Agente especializado em gerar documentação de projetos",
            "agent_type": "markdown_generator",
            "config": {
                "provider": "openai",
                "model_name": "gpt-4",
                "temperature": 0.3,
                "max_tokens": 4000
            }
        }
        
        agent = await client.create_agent(agent_data)
        agent_id = agent["id"]
        print(f"✅ Agente criado: {agent['name']} (ID: {agent_id})\n")
        
        # 2. Listar agentes
        print("2. Listando agentes...")
        agents_list = await client.list_agents()
        print(f"✅ Total de agentes: {agents_list['total']}")
        for agent in agents_list["agents"]:
            print(f"   - {agent['name']} ({agent['agent_type']}) - Status: {agent['status']}")
        print()
        
        # 3. Validar um prompt
        print("3. Validando prompt...")
        prompt_data = {
            "prompt": """
            Preciso de documentação para um projeto de API REST em Python usando FastAPI.
            O projeto implementa um sistema de gerenciamento de usuários com autenticação JWT.
            Inclui endpoints para CRUD de usuários, login, logout e refresh de tokens.
            Usa PostgreSQL como banco de dados e Redis para cache.
            """,
            "agent_id": agent_id
        }
        
        validation = await client.validate_prompt(prompt_data)
        print(f"✅ Prompt válido: {validation['is_valid']}")
        print(f"   Confiança: {validation['confidence']:.2f}")
        if validation["suggestions"]:
            print("   Sugestões:")
            for suggestion in validation["suggestions"]:
                print(f"     - {suggestion}")
        print()
        
        # 4. Gerar documento
        print("4. Gerando documento...")
        document_data = {
            "prompt": prompt_data["prompt"],
            "agent_id": agent_id,
            "document_type": "project_documentation",
            "project_name": "FastAPI User Management API"
        }
        
        document = await client.generate_document(document_data)
        document_id = document["id"]
        print(f"✅ Documento gerado: {document['title']} (ID: {document_id})")
        print(f"   Projeto: {document['project_metadata']['name']}")
        print(f"   Tipo: {document['document_type']}")
        print(f"   Status: {document['status']}")
        print(f"   Tamanho: {len(document['content'])} caracteres\n")
        
        # 5. Listar documentos
        print("5. Listando documentos...")
        documents_list = await client.list_documents()
        print(f"✅ Total de documentos: {documents_list['total']}")
        for doc in documents_list["documents"]:
            print(f"   - {doc['title']} ({doc['document_type']}) - Status: {doc['status']}")
        print()
        
        # 6. Analisar qualidade do documento
        print("6. Analisando qualidade do documento...")
        quality = await client.analyze_document_quality(document_id)
        print(f"✅ Análise de qualidade:")
        print(f"   Score geral: {quality['overall_score']:.2f}")
        print(f"   Completude: {quality['completeness']:.2f}")
        print(f"   Clareza: {quality['clarity']:.2f}")
        print(f"   Estrutura: {quality['structure']:.2f}")
        if quality["suggestions"]:
            print("   Sugestões de melhoria:")
            for suggestion in quality["suggestions"]:
                print(f"     - {suggestion}")
        print()
        
        print("🎉 Demonstração concluída com sucesso!")
        
    except httpx.HTTPStatusError as e:
        print(f"❌ Erro HTTP: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        print(f"❌ Erro: {str(e)}")


async def demo_advanced_usage():
    """Demonstração avançada com múltiplos agentes e tipos de documento."""
    print("\n🚀 Demonstração Avançada da API de Agentes\n")
    
    client = AgentsAPIClient()
    
    try:
        # Criar diferentes tipos de agentes
        agent_types = [
            {
                "name": "Analisador de Código",
                "description": "Especialista em análise de código e arquitetura",
                "agent_type": "code_analyzer"
            },
            {
                "name": "Planejador de Projeto",
                "description": "Especialista em planejamento e roadmaps",
                "agent_type": "project_planner"
            }
        ]
        
        created_agents = []
        for agent_data in agent_types:
            agent_data["config"] = {
                "provider": "openai",
                "model_name": "gpt-4",
                "temperature": 0.4,
                "max_tokens": 3000
            }
            agent = await client.create_agent(agent_data)
            created_agents.append(agent)
            print(f"✅ Criado: {agent['name']}")
        
        print(f"\n📊 Total de agentes criados: {len(created_agents)}\n")
        
        # Gerar diferentes tipos de documentos
        document_prompts = [
            {
                "prompt": "Analise a arquitetura de um sistema de e-commerce com microserviços",
                "agent_id": created_agents[0]["id"],
                "document_type": "architecture_analysis",
                "project_name": "E-commerce Platform"
            },
            {
                "prompt": "Crie um roadmap para implementação de um sistema de IA conversacional",
                "agent_id": created_agents[1]["id"],
                "document_type": "project_roadmap",
                "project_name": "AI Chatbot System"
            }
        ]
        
        generated_docs = []
        for doc_data in document_prompts:
            document = await client.generate_document(doc_data)
            generated_docs.append(document)
            print(f"📄 Documento gerado: {document['title']}")
        
        print(f"\n📚 Total de documentos gerados: {len(generated_docs)}\n")
        
        # Analisar qualidade de todos os documentos
        print("🔍 Analisando qualidade dos documentos...\n")
        for doc in generated_docs:
            quality = await client.analyze_document_quality(doc["id"])
            print(f"📊 {doc['title']}:")
            print(f"   Score: {quality['overall_score']:.2f}")
            print(f"   Completude: {quality['completeness']:.2f}")
            print(f"   Clareza: {quality['clarity']:.2f}")
            print()
        
        print("🎯 Demonstração avançada concluída!")
        
    except Exception as e:
        print(f"❌ Erro na demonstração avançada: {str(e)}")


if __name__ == "__main__":
    print("🔧 Certifique-se de que a API está rodando em http://localhost:8000")
    print("🔑 Configure sua API key no código antes de executar\n")
    
    # Executar demonstrações
    asyncio.run(demo_basic_usage())
    asyncio.run(demo_advanced_usage())