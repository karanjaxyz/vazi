# services/paystack.py
import httpx

_secret_key: str | None = None
_base_url = "https://api.paystack.co"


def init_paystack(secret_key: str) -> None:
    global _secret_key
    _secret_key = secret_key


def _headers() -> dict:
    return {"Authorization": f"Bearer {_secret_key}"}


async def initialize_transaction(
    email: str,
    amount: int,  # in kobo/cents (e.g. 2900 for $29)
    plan_code: str,
    callback_url: str,
    metadata: dict | None = None,
) -> str:
    """Initialize a Paystack transaction. Returns the authorization URL."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{_base_url}/transaction/initialize",
            headers=_headers(),
            json={
                "email": email,
                "amount": amount,
                "plan": plan_code,
                "callback_url": callback_url,
                "metadata": metadata or {},
            },
        )

    data = response.json()
    return data["data"]["authorization_url"]


async def verify_transaction(reference: str) -> dict:
    """Verify a transaction by reference."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{_base_url}/transaction/verify/{reference}",
            headers=_headers(),
        )

    return response.json()["data"]


async def get_subscription(subscription_code: str) -> dict | None:
    """Get subscription details."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{_base_url}/subscription/{subscription_code}",
            headers=_headers(),
        )

    data = response.json()
    if not data.get("status"):
        return None
    return data["data"]


def verify_webhook(payload: bytes, signature: str, secret_key: str) -> bool:
    """Verify Paystack webhook signature."""
    import hashlib
    import hmac

    expected = hmac.new(
        secret_key.encode(), payload, hashlib.sha512
    ).hexdigest()
    return hmac.compare_digest(expected, signature)