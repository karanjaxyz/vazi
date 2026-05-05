import httpx

from .base import Provider, ProviderError

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"


class GeminiProvider(Provider):
    name = "gemini"

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def query(self, text: str) -> str:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    GEMINI_API_URL,
                    params={"key": self.api_key},
                    json={
                        "contents": [{"parts": [{"text": text}]}],
                        "generationConfig": {"temperature": 0.0},
                    },
                )
                response.raise_for_status()

            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]

        except (httpx.HTTPError, KeyError, IndexError) as e:
            raise ProviderError(self.name, str(e))
