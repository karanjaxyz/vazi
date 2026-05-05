import asyncio
import logging
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from config import settings
from models import (
    Project,
    MonitoringRun,
    Result,
    Mention,
    Citation,
    Sentiment,
)
from .providers import create_providers, ProviderError
from .parser import Parser

logger = logging.getLogger(__name__)

# Limit concurrent API calls to avoid rate limits
MAX_CONCURRENT_PROVIDERS = 4
MAX_CONCURRENT_QUERIES = 5


async def run_monitoring(db: Session, project: Project, run: MonitoringRun) -> int:
    """Execute a full monitoring run for a project.

    1. Query all providers for each tracked query (concurrent)
    2. Parse each response for mentions and citations (concurrent)
    3. Store everything in the database

    Returns the total number of target brand mentions found.
    """
    providers = create_providers(
        openai_key=settings.OPENAI_API_KEY,
        gemini_key=settings.GEMINI_API_KEY,
        perplexity_key=settings.PERPLEXITY_API_KEY,
        serp_key=settings.SERP_API_KEY,
    )

    if not providers:
        logger.error("No AI providers configured")
        return 0

    parser = Parser(api_key=settings.OPENAI_API_KEY)
    brand = project.brand_name
    competitors = [c.name for c in project.competitors]
    queries = project.queries

    total_mentions = 0
    query_semaphore = asyncio.Semaphore(MAX_CONCURRENT_QUERIES)

    async def process_query(query):
        """Query all providers for a single query, then parse results."""
        nonlocal total_mentions

        async with query_semaphore:
            # Fan out to all providers concurrently
            provider_tasks = [
                _query_provider(provider, query.text)
                for provider in providers
            ]
            responses = await asyncio.gather(*provider_tasks, return_exceptions=True)

            # Process each response
            for provider, response in zip(providers, responses):
                if isinstance(response, Exception):
                    logger.warning(f"Provider {provider.name} failed for '{query.text}': {response}")
                    continue

                if not response:
                    continue

                # Store raw result
                result = Result(
                    run_id=run.id,
                    query_id=query.id,
                    provider=provider.name,
                    raw_response=response,
                )
                db.add(result)
                db.flush()  # get result.id

                # Parse for mentions and citations
                parsed = await parser.parse(response, brand, competitors)

                # Store mentions
                for m in parsed.get("mentions", []):
                    brand_name = m.get("brand", "")
                    is_target = brand_name.lower() == brand.lower()

                    mention = Mention(
                        result_id=result.id,
                        brand_name=brand_name,
                        is_target_brand=is_target,
                        sentiment=_parse_sentiment(m.get("sentiment", "neutral")),
                        context=m.get("context", "")[:1000],
                        position=m.get("position", 99),
                    )
                    db.add(mention)

                    if is_target:
                        total_mentions += 1

                # Store citations
                for c in parsed.get("citations", []):
                    url = c.get("url", "")
                    if not url:
                        continue

                    citation = Citation(
                        result_id=result.id,
                        url=url,
                        domain=_extract_domain(url),
                        title=c.get("title"),
                    )
                    db.add(citation)

    # Run all queries concurrently (bounded by semaphore)
    await asyncio.gather(*[process_query(q) for q in queries])

    db.commit()
    return total_mentions


async def _query_provider(provider, text: str) -> str:
    """Query a single provider with error handling."""
    try:
        return await provider.query(text)
    except ProviderError as e:
        raise e
    except Exception as e:
        raise ProviderError(provider.name, str(e))


def _parse_sentiment(value: str) -> Sentiment:
    """Safely parse a sentiment string to the enum."""
    value = value.lower().strip()
    if value == "positive":
        return Sentiment.positive
    elif value == "negative":
        return Sentiment.negative
    return Sentiment.neutral


def _extract_domain(url: str) -> str:
    """Extract domain from a URL."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path
        return domain.removeprefix("www.")
    except Exception:
        return url[:255]
