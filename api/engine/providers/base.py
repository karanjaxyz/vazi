from abc import ABC, abstractmethod


class Provider(ABC):
    """Base class for AI providers. Each provider takes a query string
    and returns the raw text response from the AI."""

    name: str

    @abstractmethod
    async def query(self, text: str) -> str:
        """Send a query to the AI provider and return the raw response text.

        Raises:
            ProviderError: if the API call fails after retries.
        """
        ...


class ProviderError(Exception):
    """Raised when a provider API call fails."""

    def __init__(self, provider: str, message: str):
        self.provider = provider
        self.message = message
        super().__init__(f"{provider}: {message}")
