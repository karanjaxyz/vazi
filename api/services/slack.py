import httpx


async def send_slack_webhook(webhook_url: str, text: str) -> bool:
    """Send a message to a Slack incoming webhook. Returns True on success."""
    if not webhook_url:
        return False

    async with httpx.AsyncClient() as client:
        response = await client.post(webhook_url, json={"text": text})

    return response.status_code == 200


async def send_alert(
    webhook_url: str,
    project_name: str,
    changes: list[dict],
) -> bool:
    """Send a monitoring alert to Slack."""
    change_lines = "\n".join(f"• {c['message']}" for c in changes)

    text = f"*Vazi Alert: {project_name}*\n\n{change_lines}\n\n<https://app.vazi.io|View dashboard>"

    return await send_slack_webhook(webhook_url, text)
