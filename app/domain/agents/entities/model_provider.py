from enum import Enum


class ModelProvider(Enum):
    """Provedores de modelo de IA suportados."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROQ = "groq"
    LOCAL = "local"
    
    @classmethod
    def get_supported_providers(cls) -> list[str]:
        """Retorna a lista de provedores suportados."""
        return [provider.value for provider in cls]
    
    @classmethod
    def is_valid_provider(cls, provider: str) -> bool:
        """Verifica se um provedor é válido."""
        return provider in cls.get_supported_providers()