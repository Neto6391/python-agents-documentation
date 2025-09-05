# API de Agentes Inteligentes - Clean Architecture

## 🚀 Visão Geral

API moderna para criação e gerenciamento de agentes inteligentes com capacidades de geração de documentos, análise de prompts e integração com provedores de IA como Groq. Construída com Clean Architecture, DDD e padrão Hexagonal.

## ✨ Principais Funcionalidades

### 🤖 Gerenciamento de Agentes
- **Criação de agentes** personalizados com diferentes tipos e modelos
- **Suporte a múltiplos provedores**: Groq, OpenAI, Anthropic
- **Tipos de agentes**: `markdown_generator`, `code_analyzer`, `document_writer`
- **Configuração flexível**: temperatura, max_tokens, instruções customizadas

### 📄 Geração de Documentos
- **Geração automática** de documentação em markdown
- **Suporte a MVPs**: estrutura especializada para projetos MVP
- **Validação de prompts** com feedback inteligente
- **Extração de metadados** automática dos projetos

### 🏗️ Arquitetura
- **Ports & Adapters**, DI **Singleton**, **lifespan** moderno
- **CORS** configurável, **TrustedHost**, **GZip**, **Correlation-Id**
- **Security headers** (HSTS opcional), **API Key** via `X-API-Key`
- **Envelopes tipados** `HttpRequest[T]` e `HttpResponse[T]`
- **Dockerfile** otimizado com **gunicorn + uvicorn workers**

## 🛠️ Configuração e Execução

### Pré-requisitos
- Python 3.11+
- Poetry ou pip
- Chave de API do Groq (opcional)

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# Configurações da API
API_KEYS=["sua-chave-api-aqui", "123123213"]
ALLOWED_HOSTS=["localhost", "127.0.0.1"]
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]

# Configurações do Groq
GROQ_API_KEY=sua_chave_groq_aqui

# Configurações opcionais
ENVIRONMENT=development
DEBUG=true
```

### Execução Local

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar servidor de desenvolvimento
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Acessar documentação interativa
# http://127.0.0.1:8000/docs
# http://127.0.0.1:8000/redoc

# Verificar saúde da API
# GET http://127.0.0.1:8000/api/v1/health
```

### Docker

```bash
# Construir imagem
docker build -t agents-api .

# Executar container
docker run -p 8080:8080 \
  -e ALLOWED_HOSTS='["*"]' \
  -e CORS_ORIGINS='["http://localhost:3000"]' \
  -e GROQ_API_KEY='sua_chave_groq' \
  agents-api

# Verificar saúde
# http://127.0.0.1:8080/api/v1/health
```

## 📚 Endpoints da API

### 🏥 Health Check
```http
GET /api/v1/health
```

### 🤖 Gerenciamento de Agentes

#### Criar Agente
```http
POST /api/v1/agents
Content-Type: application/json
X-API-Key: sua-chave-api

{
  "name": "Documentador MVP",
  "description": "Agente especializado em documentação de MVPs",
  "agent_type": "markdown_generator",
  "model_provider": "groq",
  "model_id": "llama-3.1-8b-instant",
  "temperature": 0.7,
  "max_tokens": 4000,
  "tools": [],
  "instructions": ["Você é especialista em documentação de projetos MVP"]
}
```

#### Listar Agentes
```http
GET /api/v1/agents
X-API-Key: sua-chave-api
```

#### Obter Agente
```http
GET /api/v1/agents/{agent_id}
X-API-Key: sua-chave-api
```

#### Atualizar Agente
```http
PUT /api/v1/agents/{agent_id}
Content-Type: application/json
X-API-Key: sua-chave-api

{
  "name": "Novo Nome",
  "description": "Nova descrição"
}
```

#### Deletar Agente
```http
DELETE /api/v1/agents/{agent_id}
X-API-Key: sua-chave-api
```

### 📄 Geração de Documentos

#### Gerar Documento
```http
POST /api/v1/agents/documents/generate
Content-Type: application/json
X-API-Key: sua-chave-api

{
  "prompt": "Gere um MVP de sistema de vendas com PostgreSQL",
  "agent_id": "uuid-do-agente",
  "document_type": "readme",
  "project_name": "Sistema de Vendas MVP",
  "additional_context": {
    "project_type": "web_app",
    "technologies": ["FastAPI", "PostgreSQL", "React"]
  }
}
```

#### Validar Prompt
```http
POST /api/v1/agents/documents/validate-prompt
Content-Type: application/json
X-API-Key: sua-chave-api

{
  "prompt": "Seu prompt aqui",
  "agent_id": "uuid-do-agente"
}
```

#### Extrair Metadados
```http
POST /api/v1/agents/documents/extract-metadata
Content-Type: application/json
X-API-Key: sua-chave-api

{
  "prompt": "Seu prompt aqui",
  "agent_id": "uuid-do-agente"
}
```

#### Listar Documentos
```http
GET /api/v1/agents/documents
X-API-Key: sua-chave-api
```

## 💡 Exemplos Práticos

### Exemplo 1: Criando um Agente e Gerando Documentação MVP

```python
import requests

# Configuração
base_url = "http://localhost:8000/api/v1"
headers = {
    "Content-Type": "application/json",
    "X-API-Key": "sua-chave-api"
}

# 1. Criar um agente
agent_data = {
    "name": "Documentador MVP",
    "description": "Especialista em documentação de MVPs",
    "agent_type": "markdown_generator",
    "model_provider": "groq",
    "model_id": "llama-3.1-8b-instant",
    "temperature": 0.7,
    "max_tokens": 4000,
    "instructions": ["Você é especialista em documentação de projetos MVP"]
}

response = requests.post(f"{base_url}/agents", json=agent_data, headers=headers)
agent = response.json()
print(f"Agente criado: {agent['id']}")

# 2. Gerar documentação
doc_data = {
    "prompt": "Gere um MVP de e-commerce com carrinho de compras, PostgreSQL e React",
    "agent_id": agent["id"],
    "document_type": "readme",
    "project_name": "E-commerce MVP",
    "additional_context": {
        "project_type": "web_app",
        "technologies": ["React", "FastAPI", "PostgreSQL"]
    }
}

response = requests.post(f"{base_url}/agents/documents/generate", json=doc_data, headers=headers)
document = response.json()
print(f"Documento gerado: {document['word_count']} palavras")
print(document['content'][:200] + "...")
```

### Exemplo 2: Validação de Prompt

```python
# Validar um prompt antes de gerar o documento
validation_data = {
    "prompt": "Crie um sistema de vendas",
    "agent_id": agent["id"]
}

response = requests.post(f"{base_url}/agents/documents/validate-prompt", json=validation_data, headers=headers)
validation = response.json()

if validation["is_valid"]:
    print(f"Prompt válido! Confiança: {validation['confidence_score']}")
else:
    print("Prompt precisa de melhorias:")
    for suggestion in validation["suggestions"]:
        print(f"- {suggestion}")
```

### Exemplo 3: Usando cURL

```bash
# Criar agente
curl -X POST "http://localhost:8000/api/v1/agents" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-chave-api" \
  -d '{
    "name": "MVP Generator",
    "agent_type": "markdown_generator",
    "model_provider": "groq",
    "model_id": "llama-3.1-8b-instant"
  }'

# Gerar documento
curl -X POST "http://localhost:8000/api/v1/agents/documents/generate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-chave-api" \
  -d '{
    "prompt": "MVP de sistema de gestão escolar",
    "agent_id": "uuid-do-agente",
    "document_type": "readme",
    "project_name": "Gestão Escolar MVP"
  }'
```

## 🏗️ Estrutura do Projeto

```
app/
├── application/          # Casos de uso e DTOs
│   ├── agents/
│   │   ├── dtos/        # Data Transfer Objects
│   │   ├── mappers/     # Conversores entre camadas
│   │   └── use_cases/   # Lógica de aplicação
│   └── health/
├── core/                # Configurações e DI
│   ├── config/         # Settings e configurações
│   ├── di/             # Dependency Injection
│   ├── middleware/     # Middlewares customizados
│   └── security/       # Autenticação e autorização
├── domain/              # Entidades e regras de negócio
│   ├── agents/
│   │   ├── entities/   # Entidades do domínio
│   │   ├── ports/      # Interfaces/contratos
│   │   └── services/   # Serviços de domínio
│   └── health/
├── infrastructure/      # Implementações externas
│   ├── agents/
│   │   └── adapters/   # Implementações dos ports
│   └── external/
│       └── groq/       # Integração com Groq
└── presentation/        # Controllers e schemas
    ├── shared/         # Componentes compartilhados
    └── v1/
        ├── endpoints/  # Endpoints da API
        └── schemas/    # Schemas de request/response
```

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Executar com cobertura
pytest --cov=app

# Executar testes específicos
pytest tests/test_agents.py
```

## 🎯 Casos de Uso

### 1. Documentação Automática de MVPs
Perfeito para startups e equipes que precisam documentar rapidamente suas ideias de produto.

### 2. Geração de READMEs Técnicos
Crie documentação técnica consistente para seus projetos de desenvolvimento.

### 3. Análise e Validação de Prompts
Valide e melhore prompts antes de gerar documentação, economizando tokens e tempo.

### 4. Prototipagem Rápida
Gere documentação estruturada para validar conceitos antes do desenvolvimento.

### 5. Padronização de Documentação
Mantenha consistência na documentação entre diferentes projetos e equipes.

## 🚀 Recursos Avançados

### Tipos de Agentes Suportados

- **`markdown_generator`**: Especializado em geração de documentação em markdown
- **`code_analyzer`**: Análise e revisão de código
- **`document_writer`**: Criação de documentos técnicos
- **`mvp_specialist`**: Focado em documentação de MVPs

### Provedores de IA

- **Groq**: Modelos Llama otimizados para velocidade
- **OpenAI**: GPT-3.5, GPT-4 (em desenvolvimento)
- **Anthropic**: Claude (em desenvolvimento)

### Modelos Disponíveis (Groq)

- `llama-3.1-8b-instant`: Rápido e eficiente
- `llama-3.1-70b-versatile`: Mais poderoso para tarefas complexas
- `mixtral-8x7b-32768`: Boa para contextos longos

## 🔒 Segurança

### Autenticação
- API Key obrigatória via header `X-API-Key`
- Múltiplas chaves suportadas
- Rate limiting (em desenvolvimento)

### Headers de Segurança
- HSTS (HTTP Strict Transport Security)
- Content Security Policy
- X-Frame-Options
- X-Content-Type-Options

### Boas Práticas
- Nunca commite chaves de API no código
- Use variáveis de ambiente para configurações sensíveis
- Mantenha as dependências atualizadas

## 📊 Monitoramento

### Métricas Disponíveis
- Tempo de resposta dos endpoints
- Taxa de sucesso/erro
- Uso de tokens por agente
- Contagem de documentos gerados

### Logs
- Logs estruturados em JSON
- Correlation ID para rastreamento
- Diferentes níveis de log (DEBUG, INFO, WARNING, ERROR)

## 🤝 Contribuição

### Como Contribuir

1. **Fork** o repositório
2. **Clone** seu fork localmente
3. **Crie** uma branch para sua feature: `git checkout -b feature/nova-funcionalidade`
4. **Implemente** suas mudanças seguindo os padrões do projeto
5. **Teste** suas mudanças: `pytest`
6. **Commit** suas mudanças: `git commit -m "feat: adiciona nova funcionalidade"`
7. **Push** para sua branch: `git push origin feature/nova-funcionalidade`
8. **Abra** um Pull Request

### Padrões de Código

- Siga PEP 8 para Python
- Use type hints em todas as funções
- Documente classes e métodos públicos
- Mantenha cobertura de testes acima de 80%
- Use conventional commits

### Estrutura de Commits

```
feat: adiciona nova funcionalidade
fix: corrige bug específico
docs: atualiza documentação
test: adiciona ou modifica testes
refactor: refatora código sem mudar funcionalidade
style: mudanças de formatação
chore: tarefas de manutenção
```

## 📝 Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

## 📞 Suporte

### Documentação
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

### Problemas Comuns

**Erro: "Invalid or missing API key"**
- Verifique se o header `X-API-Key` está presente
- Confirme se a chave está configurada em `API_KEYS`

**Erro: "Agent not found"**
- Verifique se o `agent_id` existe
- Use `GET /api/v1/agents` para listar agentes disponíveis

**Erro de conexão com Groq**
- Verifique se `GROQ_API_KEY` está configurada
- Confirme se a chave é válida no painel da Groq

### Versão

**Versão Atual**: 1.0.0

**Changelog**:
- v1.0.0: Lançamento inicial com suporte a agentes Groq
- v0.9.0: Beta com funcionalidades básicas
- v0.8.0: Alpha com arquitetura Clean Architecture

---

**Desenvolvido com ❤️ usando Clean Architecture, DDD e Hexagonal Pattern**
