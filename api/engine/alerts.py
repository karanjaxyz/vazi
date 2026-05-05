import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from models import MonitoringRun, RunStatus, Result, Mention

logger = logging.getLogger(__name__)


def check_for_changes(db: Session, project_id: str, current_run_id: str) -> list[dict]:
    """Compare current run to the previous completed run.

    Returns a list of change dicts:
        [{"type": "lost_mention", "message": "You lost a mention in 'best CRM' on ChatGPT"}, ...]
    """
    # Find the previous completed run
    previous_run = db.execute(
        select(MonitoringRun)
        .where(
            MonitoringRun.project_id == project_id,
            MonitoringRun.status == RunStatus.completed,
            MonitoringRun.id != current_run_id,
        )
        .order_by(MonitoringRun.completed_at.desc())
        .limit(1)
    ).scalar_one_or_none()

    if not previous_run:
        return []  # first run, nothing to compare

    current_mentions = _get_mention_map(db, current_run_id)
    previous_mentions = _get_mention_map(db, str(previous_run.id))

    changes = []

    # Check for lost mentions (was mentioned before, not now)
    for key, prev in previous_mentions.items():
        if key not in current_mentions and prev["is_target"]:
            query_text, provider = key
            changes.append({
                "type": "lost_mention",
                "message": f"You're no longer mentioned in '{query_text}' on {provider}",
            })

    # Check for gained mentions (not mentioned before, is now)
    for key, curr in current_mentions.items():
        if key not in previous_mentions and curr["is_target"]:
            query_text, provider = key
            changes.append({
                "type": "gained_mention",
                "message": f"You're now mentioned in '{query_text}' on {provider}",
            })

    # Check for new competitor appearances
    for key, curr in current_mentions.items():
        if not curr["is_target"] and key not in previous_mentions:
            query_text, provider = key
            changes.append({
                "type": "new_competitor",
                "message": f"{curr['brand']} now appears in '{query_text}' on {provider}",
            })

    # Check for sentiment changes
    for key in current_mentions:
        if key in previous_mentions:
            curr = current_mentions[key]
            prev = previous_mentions[key]
            if curr["is_target"] and curr["sentiment"] != prev["sentiment"]:
                query_text, provider = key
                changes.append({
                    "type": "sentiment_change",
                    "message": (
                        f"Sentiment changed from {prev['sentiment']} to {curr['sentiment']} "
                        f"in '{query_text}' on {provider}"
                    ),
                })

    return changes


def _get_mention_map(db: Session, run_id: str) -> dict:
    """Build a map of (query_text, provider) -> mention data for a run."""
    mentions = db.execute(
        select(Mention, Result)
        .join(Result)
        .where(Result.run_id == run_id)
    ).all()

    mention_map = {}
    for mention, result in mentions:
        # We need the query text — get it from the result's query relationship
        query_text = result.query.text if result.query else "unknown"
        key = (query_text, result.provider.value)
        mention_map[key] = {
            "brand": mention.brand_name,
            "is_target": mention.is_target_brand,
            "sentiment": mention.sentiment.value,
            "position": mention.position,
        }

    return mention_map
