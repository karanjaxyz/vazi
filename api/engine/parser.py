import json
import logging

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

PARSE_PROMPT = """Analyze this AI-generated response for brand mentions.

Target brand: {brand}
Competitors to check: {competitors}

Extract ALL brand mentions from the response. For each mention:
- brand: exact brand name as it appears
- sentiment: "positive", "neutral", or "negative"
- context: the sentence containing the mention
- position: 1 for first brand mentioned, 2 for second, etc.

Also extract any URLs or sources cited in the response:
- url: the full URL
- domain: the domain name (e.g. "g2.com")
- title: title or description if given, otherwise null

If no brands are mentioned, return empty arrays.
If no URLs are cited, return empty citations array.

Respond with ONLY valid JSON, no markdown:
{{"mentions": [...], "citations": [...]}}

Response to analyze:
\"\"\"{response}\"\"\"
"""


class Parser:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def parse(
        self,
        response_text: str,
        brand: str,
        competitors: list[str],
    ) -> dict:
        """Parse an AI response and extract mentions + citations.

        Returns:
            {
                "mentions": [
                    {"brand": "Acme", "sentiment": "positive", "context": "...", "position": 1},
                    ...
                ],
                "citations": [
                    {"url": "https://...", "domain": "g2.com", "title": "..."},
                    ...
                ]
            }
        """
        if not response_text or not response_text.strip():
            return {"mentions": [], "citations": []}

        prompt = PARSE_PROMPT.format(
            brand=brand,
            competitors=", ".join(competitors) if competitors else "none",
            response=response_text[:8000],  # truncate to avoid token limits
        )

        try:
            completion = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.0,
            )

            raw = completion.choices[0].message.content
            parsed = json.loads(raw)

            # Validate structure
            if "mentions" not in parsed:
                parsed["mentions"] = []
            if "citations" not in parsed:
                parsed["citations"] = []

            return parsed

        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Parse failed: {e}")
            return {"mentions": [], "citations": []}
