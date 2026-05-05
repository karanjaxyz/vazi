import httpx

_api_key: str | None = None
_from_address: str = "Vazi <alerts@vazi.io>"


def init_email(api_key: str, from_address: str | None = None) -> None:
    global _api_key, _from_address
    _api_key = api_key
    if from_address:
        _from_address = from_address


async def send_email(to: str, subject: str, html: str) -> bool:
    """Send an email via Resend API. Returns True on success."""
    if not _api_key:
        return False

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {_api_key}"},
            json={
                "from": _from_address,
                "to": [to],
                "subject": subject,
                "html": html,
            },
        )

    return response.status_code == 200


async def send_alert(
    to: str,
    project_name: str,
    changes: list[dict],
) -> bool:
    """Send a monitoring alert email."""
    change_items = "".join(
        f"<li>{c['message']}</li>" for c in changes
    )

    html = f"""
    <h2>Vazi Alert: {project_name}</h2>
    <p>We detected changes in your AI visibility:</p>
    <ul>{change_items}</ul>
    <p><a href="https://app.vazi.io">View your dashboard →</a></p>
    """

    return await send_email(
        to=to,
        subject=f"Vazi Alert: Changes detected for {project_name}",
        html=html,
    )
