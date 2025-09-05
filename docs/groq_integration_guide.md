# Guia de Integração Groq

## Visão Geral

Este documento descreve como a integração com o Groq foi implementada no sistema de agentes, permitindo o uso de modelos de linguagem avançados para geração de documentação técnica.

## Funcionalidades Implementadas

### 1. GroqAgentService

- **Criação de Agentes**: Suporte completo para criar agentes usando modelos Groq
- **Validação de Prompts**: Validação inteligente de prompts antes da geração
- **Extração de Metadados**: Extração automática de metadados de projetos
- **Geração de Documentos**: Geração de documentação em formato Markdown

### 2. Modelos Suportados

- `llama-3.1-70b-versatile`: Modelo principal para geração de documentação
- `llama-3.1-8b-instant`: Modelo rápido para validações
- `llama-3.2-90b-text-preview`: Modelo avançado para análises complexas
- `llama-4-scout`: Modelo experimental para casos específicos

### 3. Configuração

#### Variáveis de Ambiente

```bash
GROQ_API_KEY=your_groq_api_key_here
```

#### Exemplo de Configuração de Agente

```python
from app.domain.agents.entities.agent import AgentConfig
from app.domain.agents.enums import ModelProvider

config = AgentConfig(
    model_provider=ModelProvider.GROQ.value,
    model_id="llama-3.1-70b-versatile",
    temperature=0.7,
    max_tokens=4000,
    instructions=["Gere documentação clara e bem estruturada"]
)
```

## Exemplos de Uso

### 1. Criação de Agente

```python
from app.infrastructure.agents.services.groq_agent_service import GroqAgentService

service = GroqAgentService()
agent = await service.create_agent(config)
print(f"Agente criado: {agent.id}")
```

### 2. Validação de Prompt

```python
result = await service.validate_prompt(
    prompt="Gere um README para projeto FastAPI",
    agent_id=agent.id
)
print(f"Válido: {result.is_valid}")
print(f"Sugestões: {result.suggestions}")
```

### 3. Geração de Documento

```python
from app.domain.agents.entities.project_document import ProjectMetadata, DocumentType

metadata = ProjectMetadata(
    project_name="Meu Projeto",
    description="Projeto FastAPI com autenticação",
    project_type="web_application",
    technologies=["Python", "FastAPI", "PostgreSQL"],
    complexity_level="medium",
    estimated_duration="2 semanas"
)

content = await service.generate_markdown_document(
    prompt="Gere um README completo",
    document_type=DocumentType.README,
    project_metadata=metadata,
    agent_id=agent.id
)
```

## Testes

### Executar Testes do GroqAgentService

```bash
pytest tests/test_groq_agent_service.py -v
```

### Teste de Integração Completa

```bash
python test_generate_document.py
```

## Arquitetura

### Componentes Principais

1. **GroqAgentService**: Implementação do port AgentServicePort
2. **AgentServiceFactory**: Factory para criar serviços baseado no provedor
3. **DI Container**: Injeção de dependência configurada
4. **Enums e DTOs**: Suporte para Groq como provedor

### Fluxo de Execução

1. Cliente solicita criação de agente
2. Factory identifica provedor Groq
3. GroqAgentService cria agente usando API Groq
4. Agente fica disponível para validação e geração
5. Documentos são gerados usando modelos Groq

## Benefícios

- **Performance**: Modelos Groq oferecem alta velocidade de inferência
- **Qualidade**: Modelos Llama 3.1/3.2 geram documentação de alta qualidade
- **Flexibilidade**: Suporte a múltiplos modelos para diferentes casos de uso
- **Escalabilidade**: Arquitetura permite fácil adição de novos provedores

## Próximos Passos

- [ ] Implementar cache de respostas para otimização
- [ ] Adicionar métricas de performance
- [ ] Expandir suporte para mais tipos de documento
- [ ] Implementar retry automático em caso de falhas

## Troubleshooting

### Erro: "GROQ_API_KEY não configurada"

**Solução**: Configure a variável de ambiente GROQ_API_KEY com sua chave da API Groq.

### Erro: "Agente não encontrado"

**Solução**: Verifique se o agente foi criado corretamente e se o ID está correto.

### Erro: "Modelo não suportado"

**Solução**: Verifique se o modelo especificado está na lista de modelos suportados.

## Conclusão

A integração com Groq foi implementada com sucesso, fornecendo uma base sólida para geração de documentação técnica usando modelos de linguagem avançados. O sistema é extensível e permite fácil adição de novos provedores no futuro.