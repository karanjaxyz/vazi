from openai import AsyncOpenAI, APIError

from .base import Provider, ProviderError


class OpenAIProvider(Provider):
    name = "chatgpt"

    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def query(self, text: str) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": text}],
                temperature=0.0,  # deterministic for consistency across runs
            )
            return response.choices[0].message.content
        except APIError as e:
            raise ProviderError(self.name, str(e))
