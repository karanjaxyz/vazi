from .base import Provider, ProviderError
from .openai import OpenAIProvider
from .gemini import GeminiProvider
from .perplexity import PerplexityProvider
from .serp import SerpProvider


def create_providers(
    openai_key: str = "",
    gemini_key: str = "",
    perplexity_key: str = "",
    serp_key: str = "",
) -> list[Provider]:
    """Create provider instances for all configured API keys.
    Skips providers with no key — self-hosters might only have some."""
    providers = []
    if openai_key:
        providers.append(OpenAIProvider(api_key=openai_key))
    if gemini_key:
        providers.append(GeminiProvider(api_key=gemini_key))
    if perplexity_key:
        providers.append(PerplexityProvider(api_key=perplexity_key))
    if serp_key:
        providers.append(SerpProvider(api_key=serp_key))
    return providers