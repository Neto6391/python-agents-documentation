# Sistema de Agentes - Documentação

## Visão Geral

O Sistema de Agentes é um framework integrado à API FastAPI que permite a criação e gerenciamento de agentes de IA especializados para geração de documentação de projetos. O sistema utiliza arquitetura hexagonal (Clean Architecture) com injeção de dependência para garantir flexibilidade e testabilidade.

## Arquitetura

### Camadas da Aplicação

```
app/
├── domain/agents/           # Camada de Domínio
│   ├── entities/           # Entidades de negócio
│   ├── value_objects/      # Objetos de valor
│   └── ports/             # Interfaces (contratos)
├── application/agents/      # Camada de Aplicação
│   ├── dtos/              # Data Transfer Objects
│   ├── mappers/           # Conversores entre camadas
│   └── use_cases/         # Casos de uso
├── infrastructure/agents/   # Camada de Infraestrutura
│   ├── repositories/      # Implementações de repositórios
│   └── services/          # Serviços externos
└── presentation/v1/endpoints/agents/  # Camada de Apresentação
    ├── agent_endpoints.py     # Endpoints de agentes
    └── document_endpoints.py  # Endpoints de documentos
```

### Componentes Principais

#### 1. Entidades de Domínio

- **Agent**: Representa um agente de IA com configurações específicas
- **ProjectDocument**: Documento gerado por um agente
- **ProjectMetadata**: Metadados extraídos de projetos
- **ValidationResult**: Resultado da validação de prompts

#### 2. Casos de Uso

- **CreateAgentUseCase**: Criação de novos agentes
- **GenerateDocumentUseCase**: Geração de documentos
- **ListAgentsUseCase**: Listagem de agentes com filtros
- **ListDocumentsUseCase**: Listagem de documentos com filtros

#### 3. Repositórios

- **AgentRepository**: Gerenciamento de agentes
- **DocumentRepository**: Gerenciamento de documentos

#### 4. Serviços

- **AgentService**: Interface com o framework Agno

## Funcionalidades

### Gerenciamento de Agentes

#### Criar Agente
```http
POST /api/v1/agents
Content-Type: application/json
X-API-Key: your-api-key

{
  "name": "Documentador de Projetos",
  "description": "Agente especializado em gerar documentação",
  "agent_type": "markdown_generator",
  "config": {
    "provider": "openai",
    "model_name": "gpt-4",
    "temperature": 0.3,
    "max_tokens": 4000
  }
}
```

#### Listar Agentes
```http
GET /api/v1/agents?limit=10&offset=0&agent_type=markdown_generator
X-API-Key: your-api-key
```

#### Obter Agente por ID
```http
GET /api/v1/agents/{agent_id}
X-API-Key: your-api-key
```

#### Atualizar Status do Agente
```http
PUT /api/v1/agents/{agent_id}/status
Content-Type: application/json
X-API-Key: your-api-key

{
  "status": "active"
}
```

### Geração de Documentos

#### Gerar Documento
```http
POST /api/v1/agents/documents/generate
Content-Type: application/json
X-API-Key: your-api-key

{
  "prompt": "Documentação para API REST em FastAPI...",
  "agent_id": "agent-uuid",
  "document_type": "project_documentation",
  "project_name": "FastAPI User API"
}
```

#### Validar Prompt
```http
POST /api/v1/agents/documents/validate-prompt
Content-Type: application/json
X-API-Key: your-api-key

{
  "prompt": "Seu prompt aqui...",
  "agent_id": "agent-uuid"
}
```

#### Extrair Metadados
```http
POST /api/v1/agents/documents/extract-metadata
Content-Type: application/json
X-API-Key: your-api-key

{
  "prompt": "Descrição do projeto...",
  "agent_id": "agent-uuid"
}
```

#### Listar Documentos
```http
GET /api/v1/agents/documents?limit=10&offset=0&document_type=project_documentation
X-API-Key: your-api-key
```

#### Analisar Qualidade do Documento
```http
POST /api/v1/agents/documents/{document_id}/analyze-quality
X-API-Key: your-api-key
```

#### Melhorar Prompt
```http
POST /api/v1/agents/documents/improve-prompt
Content-Type: application/json
X-API-Key: your-api-key

{
  "original_prompt": "Prompt original...",
  "agent_id": "agent-uuid"
}
```

## Tipos de Agentes

### 1. Markdown Generator
- **Tipo**: `markdown_generator`
- **Especialidade**: Geração de documentação em Markdown
- **Capacidades**: 
  - Gerar documentação estruturada
  - Validar prompts
  - Extrair metadados de projetos
  - Melhorar prompts
  - Analisar qualidade de documentos

### 2. Code Analyzer
- **Tipo**: `code_analyzer`
- **Especialidade**: Análise de código e arquitetura
- **Capacidades**:
  - Analisar estrutura de código
  - Gerar documentação técnica
  - Extrair padrões arquiteturais
  - Sugerir melhorias

### 3. Project Planner
- **Tipo**: `project_planner`
- **Especialidade**: Planejamento e estruturação de projetos
- **Capacidades**:
  - Criar estrutura de projetos
  - Gerar roadmaps
  - Identificar requisitos
  - Sugerir arquiteturas

## Tipos de Documentos

- `project_documentation`: Documentação geral de projeto
- `api_documentation`: Documentação de APIs
- `architecture_analysis`: Análise arquitetural
- `project_roadmap`: Roadmap de projeto
- `technical_specification`: Especificação técnica
- `user_guide`: Guia do usuário
- `deployment_guide`: Guia de deploy

## Status dos Agentes

- `inactive`: Agente criado mas não ativo
- `active`: Agente ativo e disponível
- `busy`: Agente processando uma tarefa
- `error`: Agente com erro
- `maintenance`: Agente em manutenção

## Status dos Documentos

- `draft`: Rascunho inicial
- `in_progress`: Em processo de geração
- `completed`: Documento finalizado
- `failed`: Falha na geração
- `reviewing`: Em revisão
- `published`: Publicado

## Configuração

### Variáveis de Ambiente

```bash
# Configurações do modelo de IA
AGENTS_MODEL__PROVIDER=openai
AGENTS_MODEL__MODEL_NAME=gpt-4
AGENTS_MODEL__TEMPERATURE=0.7
AGENTS_MODEL__MAX_TOKENS=2000

# Configurações do framework Agno
AGENTS_FRAMEWORK__BASE_URL=http://localhost:8080
AGENTS_FRAMEWORK__API_KEY=your-agno-api-key
AGENTS_FRAMEWORK__TIMEOUT=60

# Configurações de geração de documentos
AGENTS_DOCUMENT_GENERATION__MAX_CONTENT_LENGTH=50000
AGENTS_DOCUMENT_GENERATION__QUALITY_THRESHOLD=0.7
AGENTS_DOCUMENT_GENERATION__AUTO_IMPROVE_PROMPTS=true

# Configurações de repositório
AGENTS_REPOSITORY_MAX_ITEMS=10000

# Configurações de cache
AGENTS_CACHE_ENABLED=true
AGENTS_CACHE_TTL=3600

# Configurações de segurança
AGENTS_VALIDATE_PROMPTS=true
AGENTS_SANITIZE_CONTENT=true
```

## Exemplos de Uso

### Exemplo Básico com Python

```python
import asyncio
import httpx

async def create_and_use_agent():
    headers = {"X-API-Key": "your-api-key"}
    
    # Criar agente
    agent_data = {
        "name": "Documentador",
        "agent_type": "markdown_generator",
        "config": {
            "provider": "openai",
            "model_name": "gpt-4",
            "temperature": 0.3
        }
    }
    
    async with httpx.AsyncClient() as client:
        # Criar agente
        response = await client.post(
            "http://localhost:8000/api/v1/agents",
            json=agent_data,
            headers=headers
        )
        agent = response.json()
        
        # Gerar documento
        doc_data = {
            "prompt": "Documentação para API de usuários",
            "agent_id": agent["id"],
            "document_type": "api_documentation"
        }
        
        response = await client.post(
            "http://localhost:8000/api/v1/agents/documents/generate",
            json=doc_data,
            headers=headers
        )
        document = response.json()
        
        print(f"Documento gerado: {document['title']}")

asyncio.run(create_and_use_agent())
```

### Exemplo com JavaScript/Node.js

```javascript
const axios = require('axios');

const API_BASE = 'http://localhost:8000/api/v1';
const headers = { 'X-API-Key': 'your-api-key' };

async function createAndUseAgent() {
  try {
    // Criar agente
    const agentResponse = await axios.post(`${API_BASE}/agents`, {
      name: 'Documentador JS',
      agent_type: 'markdown_generator',
      config: {
        provider: 'openai',
        model_name: 'gpt-4',
        temperature: 0.3
      }
    }, { headers });
    
    const agent = agentResponse.data;
    
    // Gerar documento
    const docResponse = await axios.post(`${API_BASE}/agents/documents/generate`, {
      prompt: 'Documentação para aplicação Node.js',
      agent_id: agent.id,
      document_type: 'project_documentation'
    }, { headers });
    
    const document = docResponse.data;
    console.log(`Documento gerado: ${document.title}`);
    
  } catch (error) {
    console.error('Erro:', error.response?.data || error.message);
  }
}

createAndUseAgent();
```

## Tratamento de Erros

### Códigos de Status HTTP

- `200`: Sucesso
- `201`: Criado com sucesso
- `400`: Dados inválidos
- `401`: Não autorizado (API key inválida)
- `404`: Recurso não encontrado
- `500`: Erro interno do servidor

### Exemplos de Respostas de Erro

```json
{
  "detail": "Agente com ID 'invalid-id' não encontrado"
}
```

```json
{
  "detail": "Dados inválidos: temperatura deve estar entre 0.0 e 2.0"
}
```

## Monitoramento e Logs

O sistema registra automaticamente:

- Criação e atualização de agentes
- Geração de documentos
- Validação de prompts
- Análises de qualidade
- Erros e exceções

Os logs incluem:
- Timestamp
- Nível de log (INFO, WARNING, ERROR)
- ID do agente/documento
- Detalhes da operação
- Tempo de execução

## Limitações e Considerações

### Limitações Atuais

1. **Repositório em Memória**: Os dados são perdidos ao reiniciar a aplicação
2. **Framework Agno**: Implementação simulada para demonstração
3. **Autenticação**: Apenas API key simples
4. **Rate Limiting**: Não implementado

### Próximos Passos

1. Implementar repositórios persistentes (PostgreSQL/MongoDB)
2. Integração real com frameworks de IA
3. Sistema de autenticação mais robusto
4. Rate limiting e throttling
5. Cache distribuído (Redis)
6. Métricas e observabilidade
7. Testes automatizados
8. Documentação OpenAPI/Swagger

## Contribuição

Para contribuir com o sistema de agentes:

1. Siga a arquitetura hexagonal estabelecida
2. Implemente testes unitários para novos casos de uso
3. Mantenha a separação clara entre camadas
4. Use injeção de dependência para novos serviços
5. Documente novas funcionalidades

## Suporte

Para dúvidas ou problemas:

1. Verifique os logs da aplicação
2. Consulte esta documentação
3. Execute os exemplos de uso
4. Verifique a configuração das variáveis de ambiente