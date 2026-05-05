from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from models import User
from schemas.billing import CheckoutRequest, CheckoutResponse, BillingStatus
from services import paystack
from .deps import get_db, get_current_user

router = APIRouter(prefix="/billing", tags=["billing"])


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout(
    data: CheckoutRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a Paystack checkout session for the $29/mo plan."""
    url = await paystack.initialize_transaction(
        email=user.email,
        amount=2900,  # $29.00 in cents
        plan_code=settings.PAYSTACK_PLAN_CODE,
        callback_url=data.callback_url,
        metadata={"user_uid": user.user_uid},
    )

    return CheckoutResponse(authorization_url=url)


@router.get("/status", response_model=BillingStatus)
async def get_billing_status(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current subscription status."""
    if not user.paystack_customer_code:
        return BillingStatus(
            has_subscription=False,
            status=None,
            next_payment_date=None,
            subscription_code=None,
        )

    sub = await paystack.get_subscription(user.paystack_customer_code)

    if not sub:
        return BillingStatus(
            has_subscription=False,
            status=None,
            next_payment_date=None,
            subscription_code=None,
        )

    return BillingStatus(
        has_subscription=True,
        status=sub.get("status"),
        next_payment_date=sub.get("next_payment_date"),
        subscription_code=sub.get("subscription_code"),
    )


@router.post("/webhook")
async def paystack_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Handle Paystack webhook events."""
    payload = await request.body()
    signature = request.headers.get("x-paystack-signature", "")

    if not paystack.verify_webhook(payload, signature, settings.PAYSTACK_WEBHOOK_SECRET):
        raise HTTPException(status_code=400, detail="Invalid signature")

    import json
    event = json.loads(payload)
    event_type = event.get("event")
    data = event.get("data", {})

    if event_type == "subscription.create":
        # User subscribed — store their customer code
        customer_email = data.get("customer", {}).get("email")
        customer_code = data.get("customer", {}).get("customer_code")

        if customer_email and customer_code:
            from sqlalchemy import select
            result = await db.execute(
                select(User).where(User.email == customer_email)
            )
            user = result.scalar_one_or_none()
            if user:
                user.paystack_customer_code = customer_code
                await db.commit()

    elif event_type == "subscription.disable":
        # Subscription cancelled
        customer_code = data.get("customer", {}).get("customer_code")
        if customer_code:
            from sqlalchemy import select
            result = await db.execute(
                select(User).where(User.paystack_customer_code == customer_code)
            )
            user = result.scalar_one_or_none()
            if user:
                user.paystack_customer_code = None
                await db.commit()

    return {"status": "ok"}
