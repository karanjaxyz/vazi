import httpx

from .base import Provider, ProviderError

PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"


class PerplexityProvider(Provider):
    name = "perplexity"

    def __init__(self, api_key: str, model: str = "sonar"):
        self.api_key = api_key
        self.model = model

    async def query(self, text: str) -> str:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    PERPLEXITY_API_URL,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": text}],
                        "temperature": 0.0,
                    },
                )
                response.raise_for_status()

            data = response.json()
            return data["choices"][0]["message"]["content"]

        except (httpx.HTTPError, KeyError, IndexError) as e:
            raise ProviderError(self.name, str(e))
