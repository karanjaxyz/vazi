# schemas/billing.py
from pydantic import BaseModel


class CheckoutRequest(BaseModel):
    callback_url: str


class CheckoutResponse(BaseModel):
    authorization_url: str


class BillingStatus(BaseModel):
    has_subscription: bool
    status: str | None  # active, non-renewing, attention, cancelled
    next_payment_date: str | None
    subscription_code: str | None