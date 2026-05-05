from fastapi import Depends, HTTPException, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from models import User
from services.firebase import verify_token


async def get_db(session: AsyncSession = Depends(get_async_session)):
    """Database session dependency."""
    yield session


async def get_current_user(
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Extract and verify Firebase token, return the User.

    Creates the user record on first login (upsert).
    Expects header: Authorization: Bearer <firebase_id_token>
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization.removeprefix("Bearer ").strip()

    try:
        claims = verify_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    uid = claims["uid"]
    email = claims.get("email")

    if not uid:
        raise HTTPException(status_code=401, detail="Invalid token claims")

    # Find or create user
    result = await db.execute(select(User).where(User.user_uid == uid))
    user = result.scalar_one_or_none()

    if not user:
        user = User(user_uid=uid, email=email or "")
        db.add(user)
        await db.commit()
        await db.refresh(user)
    elif email and user.email != email:
        # Sync email from Firebase if it changed
        user.email = email
        await db.commit()

    return user
