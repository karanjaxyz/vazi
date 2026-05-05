from sqlalchemy import select, func
from sqlalchemy.orm import Session

from models import Result, Mention


def compute_visibility_score(db: Session, run_id: str, total_queries: int) -> int:
    """Compute a 0-100 visibility score for a monitoring run.

    Formula:
    - Base: % of (query, provider) pairs where the target brand is mentioned
    - Bonus: weighted by position (mentioned first = more points)
    - Bonus: positive sentiment adds more than neutral

    Returns an integer 0-100.
    """
    if total_queries == 0:
        return 0

    # Count total possible slots (queries × providers that returned results)
    total_results = db.execute(
        select(func.count(Result.id)).where(Result.run_id == run_id)
    ).scalar_one()

    if total_results == 0:
        return 0

    # Get all target brand mentions for this run
    mentions = db.execute(
        select(Mention)
        .join(Result)
        .where(
            Result.run_id == run_id,
            Mention.is_target_brand == True,
        )
    ).scalars().all()

    if not mentions:
        return 0

    # Base score: what % of results mention the brand
    mention_rate = len(mentions) / total_results

    # Position bonus: being mentioned first (position 1) is worth more
    position_scores = []
    for m in mentions:
        if m.position == 1:
            position_scores.append(1.0)
        elif m.position == 2:
            position_scores.append(0.7)
        elif m.position == 3:
            position_scores.append(0.4)
        else:
            position_scores.append(0.2)

    avg_position_score = sum(position_scores) / len(position_scores)

    # Sentiment bonus
    sentiment_scores = []
    for m in mentions:
        if m.sentiment.value == "positive":
            sentiment_scores.append(1.0)
        elif m.sentiment.value == "neutral":
            sentiment_scores.append(0.6)
        else:
            sentiment_scores.append(0.2)

    avg_sentiment_score = sum(sentiment_scores) / len(sentiment_scores)

    # Weighted combination
    score = (
        mention_rate * 0.5
        + avg_position_score * 0.3
        + avg_sentiment_score * 0.2
    ) * 100

    return min(100, max(0, round(score)))
