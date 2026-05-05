import httpx

from .base import Provider, ProviderError

SERP_API_URL = "https://serpapi.com/search"


class SerpProvider(Provider):
    name = "ai_overview"

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def query(self, text: str) -> str:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    SERP_API_URL,
                    params={
                        "q": text,
                        "api_key": self.api_key,
                        "engine": "google",
                        "gl": "us",
                        "hl": "en",
                    },
                )
                response.raise_for_status()

            data = response.json()

            # SerpAPI returns AI Overview in the ai_overview key
            ai_overview = data.get("ai_overview")
            if ai_overview:
                # Extract the text content from the AI overview snippet
                if isinstance(ai_overview, dict):
                    return ai_overview.get("text", str(ai_overview))
                return str(ai_overview)

            # Fallback: no AI Overview was shown for this query
            return ""

        except (httpx.HTTPError, KeyError) as e:
            raise ProviderError(self.name, str(e))
